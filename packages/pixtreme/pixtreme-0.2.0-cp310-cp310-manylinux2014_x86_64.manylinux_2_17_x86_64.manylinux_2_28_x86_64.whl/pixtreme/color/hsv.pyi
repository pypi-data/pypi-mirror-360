from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.utils.dtypes import to_float32
__all__ = ['bgr_to_hsv', 'bgr_to_rgb', 'cp', 'hsv_to_bgr', 'hsv_to_rgb', 'hsv_to_rgb_kernel', 'hsv_to_rgb_kernel_code', 'rgb_to_bgr', 'rgb_to_hsv', 'rgb_to_hsv_kernel', 'rgb_to_hsv_kernel_code', 'to_float32']
def bgr_to_hsv(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert BGR to HSV
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in BGR format.
    
        Returns
        -------
        image_hsv : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in
        
    """
def hsv_to_bgr(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert HSV to BGR
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in HSV format.
    
        Returns
        -------
        image_bgr : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in BGR format.
        
    """
def hsv_to_rgb(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert HSV to RGB
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in HSV format.
    
        Returns
        -------
        image_rgb : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in RGB format.
        
    """
def rgb_to_hsv(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert RGB to HSV
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in RGB format.
    
        Returns
        -------
        image_hsv : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in HSV format.
        
    """
__test__: dict = {}
hsv_to_rgb_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
hsv_to_rgb_kernel_code: str = '\nextern "C" __global__\nvoid hsv_to_rgb_kernel_optimized(const float* hsv, float* rgb, int height, int width) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n    float h = hsv[idx] * 360.0f;\n    float s = hsv[idx + 1];\n    float v = hsv[idx + 2];\n\n    float c = v * s;\n    //float h_prime = fmodf(h / 60.0, 6);\n    h = fmodf(h, 360.0f);\n    if (h < 0) h += 360.0f;\n    float h_prime = h / 60.0f;\n\n    float x_tmp = c * (1 - fabsf(fmodf(h_prime, 2) - 1));\n    float m = v - c;\n\n    float r, g, b;\n\n    if (0 <= h_prime && h_prime < 1) {\n        r = c; g = x_tmp; b = 0;\n    } else if (1 <= h_prime && h_prime < 2) {\n        r = x_tmp; g = c; b = 0;\n    } else if (2 <= h_prime && h_prime < 3) {\n        r = 0; g = c; b = x_tmp;\n    } else if (3 <= h_prime && h_prime < 4) {\n        r = 0; g = x_tmp; b = c;\n    } else if (4 <= h_prime && h_prime < 5) {\n        r = x_tmp; g = 0; b = c;\n    } else if (5 <= h_prime && h_prime < 6) {\n        r = c; g = 0; b = x_tmp;\n    } else {\n        r = 0; g = 0; b = 0;\n    }\n\n    r += m;\n    g += m;\n    b += m;\n\n    rgb[idx] = r;\n    rgb[idx + 1] = g;\n    rgb[idx + 2] = b;\n}\n'
rgb_to_hsv_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
rgb_to_hsv_kernel_code: str = '\nextern "C" __global__\nvoid rgb_to_hsv_kernel(const float* rgb, float* hsv, int height, int width) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n    float r = rgb[idx];\n    float g = rgb[idx + 1];\n    float b = rgb[idx + 2];\n\n    float maxc = fmaxf(r, fmaxf(g, b));\n    float minc = fminf(r, fminf(g, b));\n    float delta = maxc - minc;\n\n    // Value\n    float v = maxc;\n\n    // Saturation\n    float s = maxc == 0 ? 0 : delta / maxc;\n\n    // Hue\n    float h = 0;\n    if (delta > 0) {\n        if (r == maxc) {\n            h = (g - b) / delta;\n        } else if (g == maxc) {\n            h = 2.0f + (b - r) / delta;\n        } else {\n            h = 4.0f + (r - g) / delta;\n        }\n        h *= 60.0f;\n        if (h < 0) h += 360.0f;\n    }\n\n    h /= 360.0f;\n    hsv[idx] = h;\n    hsv[idx + 1] = s;\n    hsv[idx + 2] = v;\n}\n'
