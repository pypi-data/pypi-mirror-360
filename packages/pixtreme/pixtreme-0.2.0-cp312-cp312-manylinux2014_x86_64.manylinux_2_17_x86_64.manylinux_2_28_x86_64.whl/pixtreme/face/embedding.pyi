from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import onnx as onnx
import onnxruntime as onnxruntime
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.face.schema import PxFace
from pixtreme.utils.blob import to_blobs
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float32
import typing
__all__ = ['FaceEmbedding', 'PxFace', 'bgr_to_rgb', 'cp', 'np', 'onnx', 'onnxruntime', 'to_blobs', 'to_cupy', 'to_float32', 'to_numpy']
class FaceEmbedding:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda'):
        ...
    def forward(self, imgs: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        ...
    def get(self, face: PxFace) -> PxFace:
        ...
__test__: dict = {}
