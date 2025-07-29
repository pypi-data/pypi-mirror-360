from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.utils.dtypes import to_float32
__all__ = ['apply_lut', 'apply_lut_cp', 'cp', 'lut_tetrahedral_kernel', 'lut_tetrahedral_kernel_code', 'lut_trilinear_kernel', 'lut_trilinear_kernel_code', 'to_float32']
def apply_lut(image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0) -> cp.ndarray:
    """
    
        Apply a 3D LUT to an image with trilinear interpolation.
    
        Parameters:
        ----------
        image : cp.ndarray
            Input image. Shape 3D array (height, width, 3) in RGB format.
        lut : cp.ndarray
            3D LUT. Shape 3D array (N, N, N, 3) in RGB format.
        interpolation : int
            Interpolation method. 0 for trilinear, 1 for tetrahedral.
    
        Returns
        -------
        result : cp.ndarray
            Output image. Shape 3D array (height, width, 3) in RGB format.
        
    """
def apply_lut_cp(image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0) -> cp.ndarray:
    """
    
        Apply a 3D LUT to an image with trilinear interpolation.
    
        Parameters:
        image : cp.ndarray
            Input image. The shape is (height, width, 3). dtype is float32.
        lut : cp.ndarray
            Input LUT. The shape is (N, N, N, 3). dtype is float32.
        interpolation : int (optional)
            The interpolation method to use. by default 0, options are: 0 for trilinear, 1 for tetrahedral.
    
        Returns:
        result : cp.ndarray
            Output image. The shape is (height, width, 3). dtype is float32.
        
    """
__test__: dict = {}
lut_tetrahedral_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
lut_tetrahedral_kernel_code: str = '\n__device__ float3 get_lut_value(const float *lut, int x, int y, int z, int lutSize, int lutSizeSquared) {\n    int index = (x * lutSizeSquared + y * lutSize + z) * 3;\n    return {lut[index], lut[index + 1], lut[index + 2]};\n}\n\nextern "C" __global__\nvoid lut_tetrahedral_kernel(const float *frame_rgb, float *output, const float *lut, int height, int width, int lutSize, int lutSizeSquared) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n\n    float r = frame_rgb[idx] * (lutSize - 1);\n    float g = frame_rgb[idx + 1] * (lutSize - 1);\n    float b = frame_rgb[idx + 2] * (lutSize - 1);\n\n    int x0 = static_cast<int>(r);\n    int x1 = min(x0 + 1, lutSize - 1);\n    int y0 = static_cast<int>(g);\n    int y1 = min(y0 + 1, lutSize - 1);\n    int z0 = static_cast<int>(b);\n    int z1 = min(z0 + 1, lutSize - 1);\n\n    float dx = r - x0;\n    float dy = g - y0;\n    float dz = b - z0;\n\n    float3 c000 = get_lut_value(lut, x0, y0, z0, lutSize, lutSizeSquared);\n    float3 c111 = get_lut_value(lut, x1, y1, z1, lutSize, lutSizeSquared);\n    float3 cA, cB;\n    float s0, s1, s2, s3;\n\n    if (dx > dy) {\n        if (dy > dz) { // dx > dy > dz\n            cA = get_lut_value(lut, x1, y0, z0, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x1, y1, z0, lutSize, lutSizeSquared);\n            s0 = 1.0 - dx;\n            s1 = dx - dy;\n            s2 = dy - dz;\n            s3 = dz;\n        } else if (dx > dz) { // dx > dz > dy\n            cA = get_lut_value(lut, x1, y0, z0, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x1, y0, z1, lutSize, lutSizeSquared);\n            s0 = 1.0 - dx;\n            s1 = dx - dz;\n            s2 = dz - dy;\n            s3 = dy;\n        } else { // dz > dx > dy\n            cA = get_lut_value(lut, x0, y0, z1, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x1, y0, z1, lutSize, lutSizeSquared);\n            s0 = 1.0 - dz;\n            s1 = dz - dx;\n            s2 = dx - dy;\n            s3 = dy;\n        }\n    } else {\n        if (dz > dy) { // dz > dy > dx\n            cA = get_lut_value(lut, x0, y0, z1, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x0, y1, z1, lutSize, lutSizeSquared);\n            s0 = 1.0 - dz;\n            s1 = dz - dy;\n            s2 = dy - dx;\n            s3 = dx;\n        } else if (dz > dx) { // dy > dz > dx\n            cA = get_lut_value(lut, x0, y1, z0, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x0, y1, z1, lutSize, lutSizeSquared);\n            s0 = 1.0 - dy;\n            s1 = dy - dz;\n            s2 = dz - dx;\n            s3 = dx;\n        } else { // dy > dx > dz\n            cA = get_lut_value(lut, x0, y1, z0, lutSize, lutSizeSquared);\n            cB = get_lut_value(lut, x1, y1, z0, lutSize, lutSizeSquared);\n            s0 = 1.0 - dy;\n            s1 = dy - dx;\n            s2 = dx - dz;\n            s3 = dz;\n        }\n    }\n\n    output[idx] = s0 * c000.x + s1 * cA.x + s2 * cB.x + s3 * c111.x;\n    output[idx + 1] = s0 * c000.y + s1 * cA.y + s2 * cB.y + s3 * c111.y;\n    output[idx + 2] = s0 * c000.z + s1 * cA.z + s2 * cB.z + s3 * c111.z;\n}\n'
lut_trilinear_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
lut_trilinear_kernel_code: str = '\nextern "C" __global__\nvoid lut_trilinear_kernel(const float* frame_rgb, const float* lut, float* result, int height, int width, int N) {\n    int idx = blockIdx.x * blockDim.x + threadIdx.x;\n    int idy = blockIdx.y * blockDim.y + threadIdx.y;\n    if (idx >= width || idy >= height) return;\n\n    int frame_rgb_index = (idy * width + idx) * 3;\n    float r = frame_rgb[frame_rgb_index] * (N - 1);\n    float g = frame_rgb[frame_rgb_index + 1] * (N - 1);\n    float b = frame_rgb[frame_rgb_index + 2] * (N - 1);\n\n    int r_low = max(0, min(int(r), N - 2));\n    int g_low = max(0, min(int(g), N - 2));\n    int b_low = max(0, min(int(b), N - 2));\n    int r_high = r_low + 1;\n    int g_high = g_low + 1;\n    int b_high = b_low + 1;\n\n    float r_ratio = r - r_low;\n    float g_ratio = g - g_low;\n    float b_ratio = b - b_low;\n\n    for (int channel = 0; channel < 3; channel++) {\n        float c000 = lut[((r_low * N + g_low) * N + b_low) * 3 + channel];\n        float c001 = lut[((r_low * N + g_low) * N + b_high) * 3 + channel];\n        float c010 = lut[((r_low * N + g_high) * N + b_low) * 3 + channel];\n        float c011 = lut[((r_low * N + g_high) * N + b_high) * 3 + channel];\n        float c100 = lut[((r_high * N + g_low) * N + b_low) * 3 + channel];\n        float c101 = lut[((r_high * N + g_low) * N + b_high) * 3 + channel];\n        float c110 = lut[((r_high * N + g_high) * N + b_low) * 3 + channel];\n        float c111 = lut[((r_high * N + g_high) * N + b_high) * 3 + channel];\n\n        float c00 = c000 * (1 - r_ratio) + c100 * r_ratio;\n        float c01 = c001 * (1 - r_ratio) + c101 * r_ratio;\n        float c10 = c010 * (1 - r_ratio) + c110 * r_ratio;\n        float c11 = c011 * (1 - r_ratio) + c111 * r_ratio;\n\n        float c0 = c00 * (1 - g_ratio) + c10 * g_ratio;\n        float c1 = c01 * (1 - g_ratio) + c11 * g_ratio;\n\n        float c = c0 * (1 - b_ratio) + c1 * b_ratio;\n\n        result[frame_rgb_index + channel] = c;\n    }\n}\n\n'
