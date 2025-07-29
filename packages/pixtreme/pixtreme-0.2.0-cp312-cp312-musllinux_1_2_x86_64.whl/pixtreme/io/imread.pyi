import Imath as Imath
import OpenEXR as OpenEXR
from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
from nvidia import nvimgcodec
import os as os
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
__all__ = ['Imath', 'OpenEXR', 'bgr_to_rgb', 'cp', 'cv2', 'imread', 'np', 'nvimgcodec', 'os', 'rgb_to_bgr']
def imread(input_path: str, is_rgb = False, is_nvimgcodec = False) -> cp.ndarray:
    """
    
        Read an image from a file into a CuPy array.
    
        Args:
            input_path (str): Path to the image file.
            is_rgb (bool): If True, the image will be read in RGB format. Default is False (BGR).
            is_nvimgcodec (bool): If True, use NVIDIA's nvimgcodec for reading the image. Default is False.
        Returns:
            cp.ndarray: The image as a CuPy array.
        Raises:
            FileNotFoundError: If the image file does not exist.
        
    """
__test__: dict = {}
