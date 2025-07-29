from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import onnxruntime as onnxruntime
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.face.schema import PxFace
from pixtreme.transform.resize import resize
from pixtreme.utils.blob import to_blob
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float32
__all__ = ['GFPGAN', 'INTER_AUTO', 'PxFace', 'bgr_to_rgb', 'cp', 'np', 'onnxruntime', 'resize', 'rgb_to_bgr', 'to_blob', 'to_cupy', 'to_float32', 'to_numpy']
class GFPGAN:
    def __init__(self, model_file, *args, **kwargs):
        ...
    def forward(self, image: cp.ndarray, density: int = 1) -> np.ndarray:
        ...
INTER_AUTO: int = -1
__test__: dict = {}
