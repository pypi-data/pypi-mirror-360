from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.transform.resize import resize
__all__ = ['cp', 'ndi_uyvy422_to_ycbcr444', 'ndi_uyvy422_to_ycbcr444_bilinear_kernel', 'ndi_uyvy422_to_ycbcr444_bilinear_kernel_code', 'ndi_uyvy422_to_ycbcr444_cp', 'ndi_uyvy422_to_ycbcr444_kernel', 'ndi_uyvy422_to_ycbcr444_kernel_code', 'resize']
def ndi_uyvy422_to_ycbcr444(uyvy_data: cp.ndarray, use_bilinear: bool = True) -> cp.ndarray:
    """
    
        Convert NDI UYVY422 to YCbCr444 using CUDA kernel.
    
        Parameters
        ----------
        uyvy_data : cp.ndarray
            The input UYVY422 data. The 3d array of the shape (height, width, 2).
        use_bilinear : bool
            Whether to use bilinear interpolation for UV components.
    
        Returns
        -------
        yuv444p : cp.ndarray
            The output YCbCr444 data. The 3d array of the shape (height, width, 3).
        
    """
def ndi_uyvy422_to_ycbcr444_cp(uyvy_data: cp.ndarray) -> cp.ndarray:
    """
    
        Convert NDI UYVY422 to YCbCr444.
    
        Parameters
        ----------
        uyvy_data : cp.ndarray
            The input UYVY422 data. The 3d array of the shape (height, width, 2).
    
        Returns
        -------
        yuv444p : cp.ndarray
            The output YCbCr444 data. The 3d array of the shape (height, width, 3).
        
    """
__test__: dict = {}
ndi_uyvy422_to_ycbcr444_bilinear_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
ndi_uyvy422_to_ycbcr444_bilinear_kernel_code: str = '\nextern "C" __global__\nvoid ndi_uyvy422_to_ycbcr444_bilinear_kernel(\n    const unsigned char* uyvy_data,\n    unsigned char* yuv444_data,\n    int height,\n    int width\n) {\n    int idx = blockIdx.x * blockDim.x + threadIdx.x;\n    int total_pixels = height * width;\n\n    if (idx >= total_pixels) return;\n\n    int row = idx / width;\n    int col = idx % width;\n\n    // Y component (channel 1)\n    int y_idx = row * width * 2 + col * 2 + 1;\n    unsigned char y_val = uyvy_data[y_idx];\n\n    // UV interpolation with bilinear sampling\n    float uv_x = (float)col / 2.0f;\n    int uv_x0 = (int)uv_x;\n    int uv_x1 = min(uv_x0 + 1, width / 2 - 1);\n    float weight = uv_x - (float)uv_x0;\n\n    // UV indices\n    int uv_idx0 = row * width * 2 + uv_x0 * 4;  // channel 0\n    int uv_idx1 = row * width * 2 + uv_x1 * 4;  // channel 0\n\n    // Get UV values\n    unsigned char u0 = uyvy_data[uv_idx0];\n    unsigned char v0 = uyvy_data[uv_idx0 + 2];\n    unsigned char u1 = uyvy_data[uv_idx1];\n    unsigned char v1 = uyvy_data[uv_idx1 + 2];\n\n    // Bilinear interpolation\n    unsigned char u_val = (unsigned char)((1.0f - weight) * u0 + weight * u1);\n    unsigned char v_val = (unsigned char)((1.0f - weight) * v0 + weight * v1);\n\n    // Output YUV444\n    int output_idx = idx * 3;\n    yuv444_data[output_idx] = y_val;\n    yuv444_data[output_idx + 1] = u_val;\n    yuv444_data[output_idx + 2] = v_val;\n}\n'
ndi_uyvy422_to_ycbcr444_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
ndi_uyvy422_to_ycbcr444_kernel_code: str = '\nextern "C" __global__\nvoid ndi_uyvy422_to_ycbcr444_kernel(\n    const unsigned char* uyvy_data,\n    unsigned char* yuv444_data,\n    int height,\n    int width\n) {\n    int idx = blockIdx.x * blockDim.x + threadIdx.x;\n    int total_pixels = height * width;\n\n    if (idx >= total_pixels) return;\n\n    int row = idx / width;\n    int col = idx % width;\n\n    // NDI UYVY422 format: (height, width, 2)\n    // channel 0: UV components [U0, V0, U1, V1, ...]\n    // channel 1: Y components\n\n    // Y component is directly available\n    int y_idx = row * width * 2 + col * 2 + 1;  // channel 1\n    unsigned char y_val = uyvy_data[y_idx];\n\n    // UV components need interpolation\n    int uv_idx = row * width * 2 + col * 2;  // channel 0\n\n    // For UV interpolation, find the nearest UV pair\n    int uv_col = col / 2;  // UV sample position\n    int uv_base_idx = row * width * 2 + uv_col * 4;  // Base index for UV pair\n\n    unsigned char u_val, v_val;\n\n    if (col % 2 == 0) {\n        // Even column: use current UV values\n        u_val = uyvy_data[uv_base_idx];      // U0\n        v_val = uyvy_data[uv_base_idx + 2];  // V0\n    } else {\n        // Odd column: interpolate between current and next UV\n        if (uv_col * 2 + 1 < width / 2) {\n            // Linear interpolation between UV pairs\n            unsigned char u0 = uyvy_data[uv_base_idx];\n            unsigned char v0 = uyvy_data[uv_base_idx + 2];\n            unsigned char u1 = uyvy_data[uv_base_idx + 4];\n            unsigned char v1 = uyvy_data[uv_base_idx + 6];\n\n            u_val = (u0 + u1) / 2;\n            v_val = (v0 + v1) / 2;\n        } else {\n            // At the edge, use the current UV values\n            u_val = uyvy_data[uv_base_idx];\n            v_val = uyvy_data[uv_base_idx + 2];\n        }\n    }\n\n    // Output YUV444\n    int output_idx = idx * 3;\n    yuv444_data[output_idx] = y_val;      // Y\n    yuv444_data[output_idx + 1] = u_val;  // U\n    yuv444_data[output_idx + 2] = v_val;  // V\n}\n'
