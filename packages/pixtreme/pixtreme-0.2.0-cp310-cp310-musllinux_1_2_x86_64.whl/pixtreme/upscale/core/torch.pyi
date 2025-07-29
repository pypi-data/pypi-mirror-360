from __future__ import annotations
from _io import BytesIO
import builtins as __builtins__
import cupy as cp
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.transform.resize import resize
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_tensor
from pixtreme.utils.dtypes import to_float32
from spandrel.__helpers.loader import ModelLoader
from spandrel.__helpers.model_descriptor import Architecture
from spandrel.__helpers.model_descriptor import ImageModelDescriptor
from spandrel.__helpers.model_descriptor import ModelTiling
from spandrel.__helpers.size_req import SizeRequirements
import torch as torch
import typing
__all__ = ['Architecture', 'BytesIO', 'INTER_AUTO', 'ImageModelDescriptor', 'ModelLoader', 'ModelTiling', 'SizeRequirements', 'TorchUpscaler', 'bgr_to_rgb', 'cp', 'resize', 'rgb_to_bgr', 'to_cupy', 'to_float32', 'to_tensor', 'torch']
class TorchUpscaler:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def _get(self, image: cp.ndarray) -> cp.ndarray:
        ...
    def get(self, image: cp.ndarray | list[cp.ndarray]) -> cp.ndarray | list[cp.ndarray]:
        ...
    def post_process(self, output_tensor: torch.Tensor) -> cp.ndarray:
        ...
    def pre_process(self, input_image: cp.ndarray) -> torch.Tensor:
        ...
INTER_AUTO: int = -1
__test__: dict = {}
