from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
__all__ = ['cp', 'uyvy422_to_ycbcr444', 'uyvy422_to_ycbcr444_cp', 'uyvy422_to_ycbcr444_kernel', 'uyvy422_to_ycbcr444_kernel_code']
def uyvy422_to_ycbcr444(uyvy_data: cp.ndarray, height: int, width: int) -> cp.ndarray:
    """
    
        Convert UYVY422 to YCbCr444.
    
        Parameters
        ----------
        uyvy_data : cp.ndarray
            The input UYVY422 data. The 1d array of the shape (height * width * 2).
        height : int
            The height of the input image.
        width : int
            The width of the input image.
    
        Returns
        -------
        yuv444p : cp.ndarray
            The output YCbCr444 data. The 3d array of the shape (height, width, 3).
        
    """
def uyvy422_to_ycbcr444_cp(uyvy_data: cp.ndarray, height: int, width: int) -> cp.ndarray:
    """
    
        Convert UYVY422 to YCbCr444.
    
        Parameters
        ----------
        uyvy_data : cp.ndarray
            The input UYVY422 data. The 1d array of the shape (height * width * 2).
        height : int
            The height of the input image.
        width : int
            The width of the input image.
    
        Returns
        -------
        yuv444p : cp.ndarray
            The output YCbCr444 data. The 3d array of the shape (height, width, 3).
        
    """
__test__: dict = {}
uyvy422_to_ycbcr444_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
uyvy422_to_ycbcr444_kernel_code: str = '\nextern "C" __global__\nvoid uyvy422_to_ycbcr444_kernel(\n    const unsigned char* uyvy_data,\n    unsigned char* yuv444_data,\n    int height,\n    int width\n) {\n    int idx = blockIdx.x * blockDim.x + threadIdx.x;\n    int total_pixels = height * width;\n\n    if (idx >= total_pixels) return;\n\n    int row = idx / width;\n    int col = idx % width;\n\n    // Position of the pixel in the UYVY422 format\n    int pair_col = col / 2;\n    int is_odd = col % 2;\n\n    // Index in the UYVY422 data\n    int uyvy_base_idx = row * width * 2 + pair_col * 4;\n\n    // Extract Y value (even pixel: Y0, odd pixel: Y1)\n    unsigned char y_val = uyvy_data[uyvy_base_idx + 1 + is_odd * 2];\n\n    // Extract U and V values (shared between pixel pairs)\n    unsigned char u_val = uyvy_data[uyvy_base_idx];\n    unsigned char v_val = uyvy_data[uyvy_base_idx + 2];\n\n    // YUV444 output index\n    int yuv444_base_idx = idx * 3;\n\n    // Write to YUV444 data\n    yuv444_data[yuv444_base_idx] = y_val;\n    yuv444_data[yuv444_base_idx + 1] = u_val;\n    yuv444_data[yuv444_base_idx + 2] = v_val;\n}\n'
