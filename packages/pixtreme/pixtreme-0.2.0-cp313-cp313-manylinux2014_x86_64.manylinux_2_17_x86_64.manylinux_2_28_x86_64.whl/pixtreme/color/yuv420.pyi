from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.transform.resize import resize
__all__ = ['cp', 'resize', 'yuv420p_to_ycbcr444', 'yuv420p_to_ycbcr444_bilinear_kernel', 'yuv420p_to_ycbcr444_bilinear_kernel_code', 'yuv420p_to_ycbcr444_cp', 'yuv420p_to_ycbcr444_nearest_kernel', 'yuv420p_to_ycbcr444_nearest_kernel_code']
def yuv420p_to_ycbcr444(yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1) -> cp.ndarray:
    """
    
        Convert YUV 4:2:0 to YCbCr 4:4:4
    
        Parameters
        ----------
        yuv420_data : cp.ndarray
            Input frame. Shape 1D array (uint8).
        width : int
            Width of the frame.
        height : int
            Height of the frame.
    
        Returns
        -------
        image_ycbcr444 : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
        
    """
def yuv420p_to_ycbcr444_cp(yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1) -> cp.ndarray:
    """
    
        Convert YUV 4:2:0 to YCbCr 4:4:4
    
        Parameters
        ----------
        yuv420_data : cp.ndarray
            Input frame. Shape 1D array (uint8).
        width : int
            Width of the frame.
        height : int
            Height of the frame.
    
        Returns
        -------
        image_ycbcr444 : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
        
    """
__test__: dict = {}
yuv420p_to_ycbcr444_bilinear_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
yuv420p_to_ycbcr444_bilinear_kernel_code: str = '\nextern "C" __global__\nvoid yuv420p_to_ycbcr444_bilinear_kernel(const float* src, float* dst, int width, int height) {\n    const int x = blockIdx.x * blockDim.x + threadIdx.x;\n    const int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    const int image_size = width * height;\n    const float fx = x / 2.0f;\n    const float fy = y / 2.0f;\n    const int src_x = int(fx);\n    const int src_y = int(fy);\n    const float dx = fx - src_x;\n    const float dy = fy - src_y;\n    const int image_size_quarter = image_size / 4;\n    const int width_half = width / 2;\n\n    const int uv_index = image_size + src_y * (width_half) + src_x;\n    const int next_x_index = min(src_x + 1, width_half - 1);\n    const int next_y_index = min(src_y + 1, height / 2 - 1);\n    const int uv_index_next_x = image_size + src_y * (width_half) + next_x_index;\n    const int uv_index_next_y = image_size + next_y_index * (width_half) + src_x;\n    const int uv_index_next_xy = image_size + next_y_index * (width_half) + next_x_index;\n\n    float u_component = (1 - dx) * (1 - dy) * src[uv_index] +\n              dx * (1 - dy) * src[uv_index_next_x] +\n              (1 - dx) * dy * src[uv_index_next_y] +\n              dx * dy * src[uv_index_next_xy];\n\n    float v_component = (1 - dx) * (1 - dy) * src[uv_index + image_size_quarter] +\n              dx * (1 - dy) * src[uv_index_next_x + image_size_quarter] +\n              (1 - dx) * dy * src[uv_index_next_y + image_size_quarter] +\n              dx * dy * src[uv_index_next_xy + image_size_quarter];\n\n    float y_component = src[y * width + x];\n\n    const int dst_index = (y * width + x) * 3;\n    dst[dst_index] = y_component;\n    dst[dst_index + 1] = u_component;\n    dst[dst_index + 2] = v_component;\n}\n'
yuv420p_to_ycbcr444_nearest_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
yuv420p_to_ycbcr444_nearest_kernel_code: str = '\nextern "C" __global__\nvoid yuv420p_to_ycbcr444_nearest_kernel(const float* src, float* dst, int width, int height) {\n    const int x = blockIdx.x * blockDim.x + threadIdx.x;\n    const int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    const int image_size = width * height;\n    const int src_x = x / 2;\n    const int src_y = y / 2;\n\n    const int uv_index = image_size + src_y * (width / 2) + src_x;\n\n    float u_component = src[uv_index];\n    float v_component = src[uv_index + image_size / 4];\n\n    float y_component = src[y * width + x];\n\n    y_component = max(0.0f, min(1.0f, (y_component - 64.0f / 1023.0f) * (1023.0f / (940.0f - 64.0f))));\n\n\n    const int dst_index = (y * width + x) * 3;\n    dst[dst_index] = y_component;\n    dst[dst_index + 1] = u_component;\n    dst[dst_index + 2] = v_component;\n}\n'
