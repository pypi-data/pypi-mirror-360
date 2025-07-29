from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.utils.dtypes import to_float32
import typing
__all__ = ['GaussianBlur', 'cp', 'gaussian_blur', 'get_gaussian_kernel', 'horizontal_blur_kernel', 'horizontal_blur_kernel_code', 'to_float32', 'vertical_blur_kernel', 'vertical_blur_kernel_code']
class GaussianBlur:
    def __init__(self):
        ...
    def get(self, image: cp.ndarray, ksize: int, sigma: float) -> cp.ndarray:
        ...
def gaussian_blur(image: cp.ndarray, ksize: int | tuple[int, int], sigma: float, kernel: tuple[cp.ndarray, cp.ndarray] | None = None) -> cp.ndarray:
    """
    
        Apply Gaussian blur to RGB image using CuPy's RawKernel
    
        Parameters:
        -----------
        image: cp.ndarray
            Input image (HxWx3, float32 [0-1])
        ksize: int | tuple[int, int]
            Kernel size (odd number)
        sigma: float
            Standard deviation of Gaussian distribution
    
        Returns:
        --------
        cp.ndarray
            Output image (HxWx3, float32 [0-1])
        
    """
def get_gaussian_kernel(ksize: int, sigma: float) -> cp.ndarray:
    """
    
        Generate 1D Gaussian kernel
    
        Parameters:
        kernel_size (int): Kernel size (odd number)
        sigma (float): Standard deviation of Gaussian distribution
    
        Returns:
        cupy.ndarray: Normalized 1D Gaussian kernel
        
    """
__test__: dict = {}
horizontal_blur_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
horizontal_blur_kernel_code: str = '\nextern "C" __global__\nvoid horizontal_blur_kernel(const float* input, float* output, const float* kernel,\n                        int height, int width, int kernel_size) {\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n\n    if (y < height && x < width) {\n        float sum_r = 0.0f;\n        float sum_g = 0.0f;\n        float sum_b = 0.0f;\n        float kernel_sum = 0.0f;\n        int radius = kernel_size / 2;\n\n        for (int k = -radius; k <= radius; k++) {\n            int px = min(max(x + k, 0), width - 1);\n            int idx = (y * width + px) * 3;\n            float kernel_val = kernel[k + radius];\n            kernel_sum += kernel_val;\n            sum_r += input[idx] * kernel_val;\n            sum_g += input[idx + 1] * kernel_val;\n            sum_b += input[idx + 2] * kernel_val;\n        }\n\n        int out_idx = (y * width + x) * 3;\n        if (kernel_sum > 0.0f) {\n            sum_r /= kernel_sum;\n            sum_g /= kernel_sum;\n            sum_b /= kernel_sum;\n        }\n        output[out_idx] = sum_r;\n        output[out_idx + 1] = sum_g;\n        output[out_idx + 2] = sum_b;\n    }\n}\n'
vertical_blur_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
vertical_blur_kernel_code: str = '\nextern "C" __global__\nvoid vertical_blur_kernel(const float* input, float* output, const float* kernel,\n                      int height, int width, int kernel_size) {\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n\n    if (y < height && x < width) {\n        float sum_r = 0.0f;\n        float sum_g = 0.0f;\n        float sum_b = 0.0f;\n        float kernel_sum = 0.0f;\n        int radius = kernel_size / 2;\n\n        for (int k = -radius; k <= radius; k++) {\n            int py = min(max(y + k, 0), height - 1);\n            int idx = (py * width + x) * 3;\n            float kernel_val = kernel[k + radius];\n            kernel_sum += kernel_val;\n            sum_r += input[idx] * kernel_val;\n            sum_g += input[idx + 1] * kernel_val;\n            sum_b += input[idx + 2] * kernel_val;\n        }\n\n        int out_idx = (y * width + x) * 3;\n        if (kernel_sum > 0.0f) {\n            sum_r /= kernel_sum;\n            sum_g /= kernel_sum;\n            sum_b /= kernel_sum;\n        }\n        output[out_idx] = fmaxf(0.0f, fminf(1.0f, sum_r));\n        output[out_idx + 1] = fmaxf(0.0f, fminf(1.0f, sum_g));\n        output[out_idx + 2] = fmaxf(0.0f, fminf(1.0f, sum_b));\n    }\n}\n'
