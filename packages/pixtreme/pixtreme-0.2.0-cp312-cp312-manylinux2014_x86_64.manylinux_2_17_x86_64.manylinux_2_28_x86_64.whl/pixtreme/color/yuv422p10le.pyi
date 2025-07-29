from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
__all__ = ['cp', 'yuv422p10le_to_ycbcr444', 'yuv422p10le_to_ycbcr444_cp', 'yuv422p10le_to_ycbcr444_kernel', 'yuv422p10le_to_ycbcr444_kernel_code']
def yuv422p10le_to_ycbcr444(ycbcr422_data: cp.ndarray, width: int, height: int) -> cp.ndarray:
    """
    
        Convert YCbCr 4:2:2 to YCbCr 4:4:4
    
        Parameters
        ----------
        ycbcr422_data : cp.ndarray
            Input frame. Shape 1D array in YUV 4:2:2 10bit format. (uint8)
        width : int
            Width of the frame.
        height : int
            Height of the frame.
    
        Returns
        -------
        frame_ycbcr444 : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
        
    """
def yuv422p10le_to_ycbcr444_cp(ycbcr422_data: cp.ndarray, width: int, height: int) -> cp.ndarray:
    """
    
        Convert YCbCr 4:2:2 to YCbCr 4:4:4
    
        Parameters
        ----------
        frame_ycbcr422 : cp.ndarray
            Input frame. Shape 1D array (uint8).
        width : int
            Width of the frame.
        height : int
            Height of the frame.
    
        Returns
        -------
        frame_ycbcr444 : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
        
    """
__test__: dict = {}
yuv422p10le_to_ycbcr444_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
yuv422p10le_to_ycbcr444_kernel_code: str = '\nextern "C" __global__\nvoid yuv422p10le_to_ycbcr444_kernel(const unsigned short* src, float* dst, int width, int height) {\n    const int x = blockIdx.x * blockDim.x + threadIdx.x;\n    const int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    const int frame_size = width * height;\n    const int uv_width = width / 2;\n    const int y_index = y * width + x;\n\n    const int u_index = frame_size + y * uv_width + x / 2;\n    const int v_index = u_index + frame_size / 2;\n\n    float y_component = ((float)(src[y_index] & 0x03FF)) / 1023.0f;\n\n    float u_component = ((float)(src[u_index] & 0x03FF)) / 1023.0f;\n    if (x % 2 == 1 && x < width - 1) {\n        float u_next = ((float)(src[u_index + 1] & 0x03FF)) / 1023.0f;\n        u_component = (u_component + u_next) / 2.0f;\n    }\n\n    float v_component = ((float)(src[v_index] & 0x03FF)) / 1023.0f;\n    if (x % 2 == 1 && x < width - 1) {\n        float v_next = ((float)(src[v_index + 1] & 0x03FF)) / 1023.0f;\n        v_component = (v_component + v_next) / 2.0f;\n    }\n\n    const int dst_index = (y * width + x) * 3;\n    dst[dst_index] = y_component;\n    dst[dst_index + 1] = u_component;\n    dst[dst_index + 2] = v_component;\n}\n\n\n'
