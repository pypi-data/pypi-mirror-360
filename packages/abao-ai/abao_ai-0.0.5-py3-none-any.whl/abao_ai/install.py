import os
from huggingface_hub import snapshot_download, hf_hub_download
from polygraphy.backend.trt import (
    CreateConfig,
    NetworkFromOnnxPath,
    EngineFromNetwork,
    SaveEngine,
)
import tensorrt as trt
from abao_ai.info import get_devices
from pathlib import Path
from abao_ai.flux import Flux
from cuda.bindings.runtime import cudaSetDevice


def install_flux(
    device_name: str,
    device_index: str,
    engines_dir: Path,
    precision: str,
    weight_streaming: bool,
):
    flux_onnx_repo = "black-forest-labs/FLUX.1-dev-onnx"
    kontext_onnx_repo = "black-forest-labs/FLUX.1-Kontext-dev-onnx"

    assert os.getenv("HF_HOME") == "/mnt/huggingface"
    assert os.getenv("HF_TOKEN")
    snapshot_download(flux_onnx_repo)
    snapshot_download(kontext_onnx_repo)
    flux = Flux(precision, weight_streaming, Path("."))
    onnxs = flux.get_onnxs()
    for model, engine in flux.engines.items():
        engine_dir = engines_dir / device_name / device_index
        os.makedirs(engine_dir, exist_ok=True)
        plan_path = engine_dir / flux.plans[model]
        print(plan_path)
        if os.path.exists(plan_path):
            continue
        onnx_file = onnxs[model]
        network = NetworkFromOnnxPath(
            onnx_file,
            plugin_instancenorm=False,
            strongly_typed=engine.strongly_typed,
        )()
        config = CreateConfig(
            tf32=True,
            bf16=engine.bf16,
            profiles=[engine.profile],
            weight_streaming=engine.weight_streaming,
            builder_optimization_level=3,
            tactic_sources=[],
        )
        engine = EngineFromNetwork(network, config)()
        SaveEngine(engine, plan_path)()


def install(
    model: str,
    engines_dir: str,
    transformer_dtype: str,
    transformer_weight_streaming: bool,
):
    for device in get_devices():
        device_name = device["name"]
        device_index = device["index"]
        cudaSetDevice(int(device_index))
        match model:
            case "flux":
                install_flux(
                    device_name,
                    device_index,
                    Path(engines_dir),
                    transformer_dtype,
                    transformer_weight_streaming,
                )
            case _:
                print("install", model, device_name)
