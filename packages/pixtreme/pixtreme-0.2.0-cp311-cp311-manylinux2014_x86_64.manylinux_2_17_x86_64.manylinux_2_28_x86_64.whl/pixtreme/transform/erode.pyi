from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
import numpy as np
from pixtreme.utils.dtypes import to_float32
__all__ = ['cp', 'create_erode_kernel', 'erode', 'erode_kernel', 'erode_kernel_code', 'np', 'to_float32']
def create_erode_kernel(kernel_size: int) -> cp.ndarray:
    """
    
        Create kernel for erosion processing
    
        Parameters:
        -----------
        kernel_size : int
            Kernel size
    
        Returns:
        --------
        cp.ndarray
            Kernel
        
    """
def erode(image: cp.ndarray, kernel_size: int, kernel = None, border_value = 0.0):
    """
    
        Perform GPU-based erosion processing on RGB images
    
        Parameters:
        -----------
        image : cp.ndarray (float32)
            Input RGB image (HxWx3), value range [0, 1]
        kernel : np.ndarray or cp.ndarray
            Structuring element (kernel). Binary 2D array
        border_value : float
            Pixel value outside boundaries
    
        Returns:
        --------
        cp.ndarray
            RGB image after erosion processing
        
    """
__test__: dict = {}
erode_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
erode_kernel_code: str = '\nextern "C" __global__ void erode_kernel(\n    const float* input,\n    float* output,\n    const int* kernel,\n    const int kernel_size,\n    const int width,\n    const int height,\n    const int kernel_center,\n    const float border_value\n) {\n    // Calculate the pixel coordinates for the current thread\n    const int x = blockIdx.x * blockDim.x + threadIdx.x;\n    const int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    // Out of bounds check\n    if (x >= width || y >= height) return;\n\n    // Process each channel (RGB)\n    for (int c = 0; c < 3; c++) {\n        float min_val = 1.0f;  // Initialize to maximum for float32\n\n        // Find minimum value in kernel area\n        for (int ky = 0; ky < kernel_size; ky++) {\n            for (int kx = 0; kx < kernel_size; kx++) {\n                // Coordinates in input image with kernel offset\n                const int img_x = x + (kx - kernel_center);\n                const int img_y = y + (ky - kernel_center);\n\n                // Check if current kernel position is 1\n                if (kernel[ky * kernel_size + kx] == 1) {\n                    float pixel_value;\n\n                    // Check if within image bounds\n                    if (img_x >= 0 && img_x < width && img_y >= 0 && img_y < height) {\n                        // Get value from input image\n                        pixel_value = input[(img_y * width + img_x) * 3 + c];\n                    } else {\n                        // Use border_value for out of bounds\n                        pixel_value = border_value;\n                    }\n\n                    min_val = min(min_val, pixel_value);\n                }\n            }\n        }\n\n        // Output result\n        output[(y * width + x) * 3 + c] = min_val;\n    }\n}\n'
