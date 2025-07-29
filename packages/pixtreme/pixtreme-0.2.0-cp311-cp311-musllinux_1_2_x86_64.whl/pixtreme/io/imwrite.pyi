import Imath as Imath
import OpenEXR as OpenEXR
from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
import os as os
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float16
from pixtreme.utils.dtypes import to_uint16
from pixtreme.utils.dtypes import to_uint8
import torch as torch
import typing
__all__ = ['Imath', 'OpenEXR', 'bgr_to_rgb', 'cp', 'cv2', 'imwrite', 'np', 'os', 'rgb_to_bgr', 'to_float16', 'to_numpy', 'to_uint16', 'to_uint8', 'torch']
def imwrite(output_path: str, image: cp.ndarray | np.ndarray, param: int = -1, is_rgb: bool = False) -> None:
    ...
__test__: dict = {}
