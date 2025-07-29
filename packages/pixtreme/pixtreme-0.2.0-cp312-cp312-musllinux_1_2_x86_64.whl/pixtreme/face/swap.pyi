from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import onnxruntime as onnxruntime
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.face.emap import load_emap
from pixtreme.face.schema import PxFace
from pixtreme.transform.resize import resize
from pixtreme.utils.blob import to_blob
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
import typing
__all__ = ['FaceSwap', 'INTER_AUTO', 'PxFace', 'bgr_to_rgb', 'cp', 'load_emap', 'np', 'onnxruntime', 'resize', 'rgb_to_bgr', 'to_blob', 'to_cupy', 'to_numpy']
class FaceSwap:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0, device: str = 'cuda'):
        ...
    def forward(self, img, latent) -> np.ndarray:
        ...
    def get(self, target_face: PxFace, source_face: PxFace) -> cp.ndarray:
        ...
INTER_AUTO: int = -1
__test__: dict = {}
