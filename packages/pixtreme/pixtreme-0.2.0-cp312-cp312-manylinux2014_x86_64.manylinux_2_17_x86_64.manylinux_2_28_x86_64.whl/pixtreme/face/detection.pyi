from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import onnxruntime as onnxruntime
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.face.schema import PxFace
from pixtreme.transform.affine import crop_from_kps
from pixtreme.transform.resize import resize
from pixtreme.utils.blob import to_blob
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float32
import typing
__all__ = ['FaceDetection', 'INTER_AUTO', 'PxFace', 'bgr_to_rgb', 'cp', 'crop_from_kps', 'np', 'onnxruntime', 'resize', 'rgb_to_bgr', 'to_blob', 'to_cupy', 'to_float32', 'to_numpy']
class FaceDetection:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0, device: str = 'cuda') -> None:
        ...
    def _init_vars(self):
        ...
    def crop(self, image: cp.ndarray, kps: cp.ndarray, size: int = 512) -> tuple:
        ...
    def distance2bbox(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        ...
    def distance2kps(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        ...
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        ...
    def get(self, image: cp.ndarray, crop_size: int = 512, max_num: int = 0, metric: str = 'default') -> list[PxFace]:
        ...
    def nms(self, dets: cp.ndarray) -> list[int]:
        ...
INTER_AUTO: int = -1
__test__: dict = {}
