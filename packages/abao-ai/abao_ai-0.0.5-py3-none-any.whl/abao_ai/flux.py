import torch
import sys
import random
import math
from typing import cast, Callable
from einops import rearrange
from tqdm.auto import tqdm
from transformers import CLIPTokenizer, T5Tokenizer
from cuda.bindings.runtime import (
    cudaStream_t,
    cudaStreamCreate,
    cudaStreamSynchronize,
)
from ray.experimental.tqdm_ray import tqdm
from polygraphy.backend.trt import (
    Profile,
    ShapeTuple,
    EngineFromPath,
)
from pathlib import Path
from abao_ai.engine import Engine, Node
from abao_ai.util import _cce, _ccr
from huggingface_hub import snapshot_download, hf_hub_download


scale_factor = 0.3611
shift_factor = 0.1159


def time_shift(mu: float, sigma: float, t: torch.Tensor):
    return math.exp(mu) / (math.exp(mu) + (1 / t - 1) ** sigma)


def get_lin_function(
    x1: float = 256, y1: float = 0.5, x2: float = 4096, y2: float = 1.15
) -> Callable[[float], float]:
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return lambda x: m * x + b


def get_schedule(
    steps: int,
    image_seq_len: int,
    base_shift: float = 0.5,
    max_shift: float = 1.15,
    shift: bool = True,
) -> list[float]:
    timesteps = torch.linspace(1, 0, steps + 1)
    if shift:
        mu = get_lin_function(y1=base_shift, y2=max_shift)(image_seq_len)
        timesteps = time_shift(mu, 1.0, timesteps)
    return timesteps.tolist()


def get_noise(
    height: int, width: int, seed: int, generator: torch.Generator, device: str
) -> torch.Tensor:
    print(device)
    generator.manual_seed(seed)
    return torch.randn(
        1,
        16,
        2 * math.ceil(height / 16),
        2 * math.ceil(width / 16),
        device=device,
        dtype=torch.bfloat16,
        generator=generator,
    )


def unpack(x: torch.Tensor, height: int, width: int) -> torch.Tensor:
    return rearrange(
        x,
        "b (h w) (c ph pw) -> b c (h ph) (w pw)",
        h=math.ceil(height / 16),
        w=math.ceil(width / 16),
        ph=2,
        pw=2,
    )


class Flux:
    flux_onnx_repo = "black-forest-labs/FLUX.1-dev-onnx"
    kontext_onnx_repo = "black-forest-labs/FLUX.1-Kontext-dev-onnx"

    def __init__(
        self,
        precision: str,
        weight_streaming: bool,
        engine_dir: Path,
        device: str = "cuda",
    ) -> None:
        self.precision = precision
        self.weight_streaming = weight_streaming
        self.engine_dir = engine_dir
        self.device = device
        clip = Engine(
            "clip",
            inputs=[Node("input_ids", torch.int32)],
            outputs=[
                Node("pooled_embeddings", torch.bfloat16),
                Node("text_embeddings", torch.bfloat16),
            ],
            tf32=True,
            bf16=True,
            strongly_typed=False,
            weight_streaming=False,
            profile=Profile(
                {
                    "input_ids": ShapeTuple(
                        (1, 77),
                        (1, 77),
                        (1, 77),
                    ),
                }
            ),
        )
        t5 = Engine(
            "t5",
            inputs=[Node("input_ids", torch.int32)],
            outputs=[Node("text_embeddings", torch.bfloat16)],
            tf32=True,
            bf16=False,
            strongly_typed=True,
            weight_streaming=False,
            profile=Profile(
                {
                    "input_ids": ShapeTuple(
                        (1, 512),
                        (1, 512),
                        (1, 512),
                    ),
                }
            ),
        )
        transformer_dev = Engine(
            "transformer_dev",
            inputs=[
                Node("hidden_states", torch.bfloat16),
                Node("encoder_hidden_states", torch.bfloat16),
                Node("pooled_projections", torch.bfloat16),
                Node("timestep", torch.bfloat16),
                Node("img_ids", torch.float32),
                Node("txt_ids", torch.float32),
                Node("guidance", torch.float32),
            ],
            outputs=[Node("latent", torch.bfloat16)],
            tf32=True,
            bf16=False,
            strongly_typed=True,
            weight_streaming=weight_streaming,
            profile=Profile(
                {
                    "hidden_states": ShapeTuple(
                        (1, 1024, 64),
                        (1, 3600, 64),
                        (1, 8100, 64),
                    ),
                    "encoder_hidden_states": ShapeTuple(
                        (1, 512, 4096),
                        (1, 512, 4096),
                        (1, 512, 4096),
                    ),
                    "pooled_projections": ShapeTuple(
                        (1, 768),
                        (1, 768),
                        (1, 768),
                    ),
                    "timestep": ShapeTuple(
                        (1,),
                        (1,),
                        (1,),
                    ),
                    "img_ids": ShapeTuple(
                        (1024, 3),
                        (3600, 3),
                        (8100, 3),
                    ),
                    "txt_ids": ShapeTuple(
                        (512, 3),
                        (512, 3),
                        (512, 3),
                    ),
                    "guidance": ShapeTuple(
                        (1,),
                        (1,),
                        (1,),
                    ),
                }
            ),
        )
        decoder = Engine(
            "decoder",
            inputs=[Node("latent", torch.bfloat16)],
            outputs=[Node("images", torch.bfloat16)],
            tf32=True,
            bf16=True,
            strongly_typed=False,
            weight_streaming=False,
            profile=Profile(
                {
                    "latent": ShapeTuple(
                        (1, 16, 64, 64),
                        (1, 16, 160, 90),
                        (1, 16, 180, 180),
                    ),
                }
            ),
        )

        self.models = ["clip", "t5", "transformer_dev", "decoder"]
        self.engines = {
            "clip": clip,
            "t5": t5,
            "transformer_dev": transformer_dev,
            "decoder": decoder,
        }
        self.plans = {
            "clip": "clip.plan",
            "t5": "t5.plan",
            "transformer_dev": f"transformer_dev_{precision}.plan",
            "decoder": "decoder.plan",
        }

        self.cuda_stream: cudaStream_t = cudaStreamCreate()[1]
        self.generator = torch.Generator(device=self.device)

    def get_onnxs(self) -> dict[str, str]:
        onnxs = {
            "clip": hf_hub_download(self.flux_onnx_repo, f"clip.opt/model.onnx"),
            "t5": hf_hub_download(self.flux_onnx_repo, f"t5.opt/model.onnx"),
            "transformer_dev": hf_hub_download(
                self.flux_onnx_repo,
                f"transformer.opt/{self.precision}/model.onnx",
            ),
            "decoder": hf_hub_download(self.flux_onnx_repo, f"vae.opt/model.onnx"),
        }
        return onnxs

    def get_plan_path(self, model: str) -> str:
        path = self.engine_dir / self.plans[model]
        return str(path)

    def get_shapes(
        self,
        model: str,
        height: int = 1280,
        width: int = 720,
    ) -> dict[str, list[int]]:
        latent_height = height // 8
        latent_width = width // 8
        shapes: dict[str, dict[str, list[int]]] = {
            "clip": {
                "input_ids": [1, 77],
                "pooled_embeddings": [1, 768],
                "text_embeddings": [1, 77, 768],
            },
            "t5": {
                "input_ids": [1, 512],
                "text_embeddings": [1, 512, 4096],
            },
            "transformer_dev": {
                "hidden_states": [1, (latent_height // 2) * (latent_width // 2), 64],
                "encoder_hidden_states": [1, 512, 4096],
                "pooled_projections": [1, 768],
                "timestep": [1],
                "img_ids": [(latent_height // 2) * (latent_width // 2), 3],
                "txt_ids": [512, 3],
                "guidance": [1],
                "latent": [1, (latent_height // 2) * (latent_width // 2), 64],
            },
            "decoder": {
                "latent": [1, 16, latent_height, latent_width],
                "images": [1, 3, height, width],
            },
        }
        return shapes[model]

    def clip(self, prompt) -> torch.Tensor:
        print("clip")
        clip_tokenizer = cast(
            CLIPTokenizer,
            CLIPTokenizer.from_pretrained(
                "black-forest-labs/FLUX.1-dev",
                subfolder="tokenizer",
            ),
        )
        batch_encoding = clip_tokenizer(
            prompt,
            truncation=True,
            max_length=77,
            return_length=False,
            return_overflowing_tokens=False,
            padding="max_length",
            return_tensors="pt",
        )
        shapes = self.get_shapes("clip")

        input_ids: torch.Tensor = batch_encoding.input_ids.type(torch.int32).to(
            self.device
        )
        pooled_embeddings = torch.empty(
            shapes["pooled_embeddings"], dtype=torch.bfloat16, device=self.device
        )
        text_embeddings = torch.empty(
            shapes["text_embeddings"], dtype=torch.bfloat16, device=self.device
        )
        engine = EngineFromPath(self.get_plan_path("clip"))()
        context = engine.create_execution_context()
        context.set_input_shape("input_ids", shapes["input_ids"])
        context.set_tensor_address("input_ids", input_ids.data_ptr())
        context.set_tensor_address("pooled_embeddings", pooled_embeddings.data_ptr())
        context.set_tensor_address("text_embeddings", text_embeddings.data_ptr())
        context.execute_async_v3(self.cuda_stream)
        _cce(cudaStreamSynchronize(self.cuda_stream))
        return pooled_embeddings

    def t5(self, prompt: str) -> torch.Tensor:
        print("t5")
        t5_tokenizer = cast(
            T5Tokenizer,
            T5Tokenizer.from_pretrained(
                "black-forest-labs/FLUX.1-dev",
                subfolder="tokenizer_2",
            ),
        )
        batch_encoding = t5_tokenizer(
            prompt,
            truncation=True,
            max_length=512,
            return_length=False,
            return_overflowing_tokens=False,
            padding="max_length",
            return_tensors="pt",
        )

        shapes = self.get_shapes("t5")

        input_ids: torch.Tensor = batch_encoding.input_ids.type(torch.int32).cuda()
        text_embeddings = torch.empty(
            shapes["text_embeddings"], dtype=torch.bfloat16, device=self.device
        )

        engine = EngineFromPath(self.get_plan_path("t5"))()
        context = engine.create_execution_context()
        context.set_input_shape("input_ids", shapes["input_ids"])
        context.set_tensor_address("input_ids", input_ids.data_ptr())
        context.set_tensor_address("text_embeddings", text_embeddings.data_ptr())
        context.execute_async_v3(self.cuda_stream)
        _cce(cudaStreamSynchronize(self.cuda_stream))
        return text_embeddings

    def transformer(
        self,
        hidden_states: torch.Tensor,
        encoder_hidden_states: torch.Tensor,
        pooled_projections: torch.Tensor,
        timesteps: list[float],
        img_ids: torch.Tensor,
        txt_ids: torch.Tensor,
        guidance: torch.Tensor,
        height: int,
        width: int,
    ) -> torch.Tensor:
        print("transformer")
        shapes = self.get_shapes("transformer_dev", height=height, width=width)
        timestep = torch.empty(
            shapes["timestep"], dtype=torch.bfloat16, device=self.device
        )
        latent = torch.empty(shapes["latent"], dtype=torch.bfloat16, device=self.device)

        engine = EngineFromPath(self.get_plan_path("transformer_dev"))()
        if self.weight_streaming:
            engine.weight_streaming_budget_v2 = 0

        context = engine.create_execution_context()
        context.set_input_shape("hidden_states", shapes["hidden_states"])
        context.set_input_shape(
            "encoder_hidden_states", shapes["encoder_hidden_states"]
        )
        context.set_input_shape("pooled_projections", shapes["pooled_projections"])
        context.set_input_shape("timestep", shapes["timestep"])
        context.set_input_shape("img_ids", shapes["img_ids"])
        context.set_input_shape("txt_ids", shapes["txt_ids"])
        context.set_input_shape("guidance", shapes["guidance"])

        context.set_tensor_address("hidden_states", hidden_states.data_ptr())
        context.set_tensor_address(
            "encoder_hidden_states", encoder_hidden_states.data_ptr()
        )
        context.set_tensor_address("pooled_projections", pooled_projections.data_ptr())
        context.set_tensor_address("timestep", timestep.data_ptr())
        context.set_tensor_address("img_ids", img_ids.data_ptr())
        context.set_tensor_address("txt_ids", txt_ids.data_ptr())
        context.set_tensor_address("guidance", guidance.data_ptr())
        context.set_tensor_address("latent", latent.data_ptr())

        for t_curr, t_prev in tqdm(zip(timesteps[:-1], timesteps[1:])):
            timestep.fill_(t_curr)
            context.execute_async_v3(self.cuda_stream)
            _cce(cudaStreamSynchronize(self.cuda_stream))
            hidden_states.add_((t_prev - t_curr) * latent)

        return hidden_states

    def decoder(self, latent: torch.Tensor, height: int, width: int) -> torch.Tensor:
        print("decoder")
        shapes = self.get_shapes("decoder", height=height, width=width)
        images = torch.empty(shapes["images"], dtype=torch.bfloat16, device=self.device)
        engine = EngineFromPath(self.get_plan_path("decoder"))()
        context = engine.create_execution_context()
        context.set_input_shape("latent", shapes["latent"])
        context.set_tensor_address("latent", latent.data_ptr())
        context.set_tensor_address("images", images.data_ptr())
        context.execute_async_v3(self.cuda_stream)
        _cce(cudaStreamSynchronize(self.cuda_stream))
        return images

    def generate(
        self,
        prompt: str,
        height: int,
        width: int,
        steps: int = 30,
        seed: int = 0,
        guidance_scale: float = 4.0,
    ) -> torch.Tensor:
        seed = seed if seed > 0 else random.randint(0, sys.maxsize)
        img = get_noise(height, width, seed, self.generator, self.device)

        bs, c, h, w = img.shape

        hidden_states = rearrange(
            img, "b c (h ph) (w pw) -> b (h w) (c ph pw)", ph=2, pw=2
        )

        img_ids = torch.zeros(
            h // 2, w // 2, 3, dtype=torch.float32, device=self.device
        )
        img_ids[..., 1] = (
            img_ids[..., 1] + torch.arange(h // 2, device=self.device)[:, None]
        )
        img_ids[..., 2] = (
            img_ids[..., 2] + torch.arange(w // 2, device=self.device)[None, :]
        )

        text_embeddings = self.t5(prompt)

        txt_ids = torch.zeros(512, 3, dtype=torch.float32, device=self.device)

        pooled_embeddings = self.clip(prompt)

        guidance = torch.full(
            [1], guidance_scale, dtype=torch.float32, device=self.device
        )

        timesteps = get_schedule(steps, hidden_states.shape[1], shift=True)

        hidden_states = self.transformer(
            hidden_states=hidden_states,
            encoder_hidden_states=text_embeddings,
            pooled_projections=pooled_embeddings,
            timesteps=timesteps,
            img_ids=img_ids,
            txt_ids=txt_ids,
            guidance=guidance,
            width=width,
            height=height,
        )
        hidden_states = unpack(hidden_states, height, width)
        hidden_states = hidden_states / scale_factor + shift_factor

        with torch.autocast(device_type=self.device, dtype=torch.bfloat16):
            images = self.decoder(hidden_states, height=height, width=width)
        return images
