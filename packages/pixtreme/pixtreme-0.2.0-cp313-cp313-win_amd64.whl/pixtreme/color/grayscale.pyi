from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.utils.dtypes import to_float32
__all__ = ['bgr_to_grayscale', 'bgr_to_rgb', 'cp', 'rgb_to_grayscale', 'rgb_to_grayscale_kernel', 'rgb_to_grayscale_kernel_code', 'to_float32']
def bgr_to_grayscale(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert BGR to Grayscale
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in BGR format.
    
        Returns
        -------
        image_gray : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in RGB format.
        
    """
def rgb_to_grayscale(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert RGB to Grayscale
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in RGB format.
    
        Returns
        -------
        frame_gray : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in RGB format.
        
    """
__test__: dict = {}
rgb_to_grayscale_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
rgb_to_grayscale_kernel_code: str = '\nextern "C" __global__\nvoid rgb_to_grayscale_kernel(const float* rgb, float* gray, int width, int height) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n    float r = rgb[idx];\n    float g = rgb[idx + 1];\n    float b = rgb[idx + 2];\n\n    float gray_val = 0.2126f * r + 0.7152f * g + 0.0722f * b;\n\n    gray[idx] = gray_val;\n    gray[idx + 1] = gray_val;\n    gray[idx + 2] = gray_val;\n}\n'
