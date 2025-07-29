from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
from pixtreme.filter.gaussian import GaussianBlur
from pixtreme.transform.affine import affine_transform
from pixtreme.transform.affine import get_inverse_matrix
from pixtreme.transform.resize import resize
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float32
__all__ = ['GaussianBlur', 'INTER_AUTO', 'PasteBack', 'affine_transform', 'cp', 'get_inverse_matrix', 'np', 'paste_back', 'resize', 'to_cupy', 'to_float32', 'to_numpy']
class PasteBack:
    def __init__(self):
        ...
    def create_mask(self, size: tuple):
        ...
    def get(self, target_image: cp.ndarray, paste_image: cp.ndarray, M: cp.ndarray) -> cp.ndarray:
        ...
def paste_back(target_image: cp.ndarray, paste_image: cp.ndarray, M: cp.ndarray, mask: cp.ndarray = None) -> cp.ndarray:
    ...
INTER_AUTO: int = -1
__test__: dict = {}
