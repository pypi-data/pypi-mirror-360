import torch
from polygraphy.backend.trt import Profile


class Node:
    def __init__(self, name: str, dtype: torch.dtype) -> None:
        self.name = name
        self.dtype = dtype


class Engine:
    def __init__(
        self,
        name: str,
        inputs: list[Node],
        outputs: list[Node],
        tf32: bool,
        bf16: bool,
        strongly_typed: bool,
        weight_streaming: bool,
        profile: Profile,
    ) -> None:
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.tf32 = tf32
        self.bf16 = bf16
        self.strongly_typed = strongly_typed
        self.weight_streaming = weight_streaming
        self.profile = profile
