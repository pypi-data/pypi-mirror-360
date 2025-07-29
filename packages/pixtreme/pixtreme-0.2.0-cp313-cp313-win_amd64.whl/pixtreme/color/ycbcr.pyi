from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
__all__ = ['OFFS_C_CENTER', 'OFFS_Y_L', 'SCALE_C_F2L', 'SCALE_C_L2F', 'SCALE_Y_F2L', 'SCALE_Y_L2F', 'bgr_to_rgb', 'bgr_to_ycbcr', 'cp', 'rgb_to_bgr', 'rgb_to_ycbcr', 'rgb_to_ycbcr_kernel', 'rgb_to_ycbcr_kernel_code', 'ycbcr_full_to_legal', 'ycbcr_full_to_legal_kernel', 'ycbcr_full_to_legal_kernel_code', 'ycbcr_legal_to_full', 'ycbcr_legal_to_full_kernel', 'ycbcr_legal_to_full_kernel_code', 'ycbcr_to_bgr', 'ycbcr_to_grayscale', 'ycbcr_to_rgb', 'ycbcr_to_rgb_kernel', 'ycbcr_to_rgb_kernel_code']
def bgr_to_ycbcr(image: cp.ndarray) -> cp.ndarray:
    ...
def rgb_to_ycbcr(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert RGB to YCbCr
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in RGB format.
    
        Returns
        -------
        image_ycbcr : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr format.
        
    """
def ycbcr_full_to_legal(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert YCbCr full-range to legal-range
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in YCbCr full-range format.
    
        Returns
        -------
        image_ycbcr_legal : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr legal-range format.
        
    """
def ycbcr_legal_to_full(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert YCbCr legal-range to full-range
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in YCbCr legal-range format.
    
        Returns
        -------
        image_ycbcr_full : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in YCbCr full-range format.
        
    """
def ycbcr_to_bgr(image: cp.ndarray) -> cp.ndarray:
    ...
def ycbcr_to_grayscale(image: cp.ndarray) -> cp.ndarray:
    """
    
        YCbCr to Grayscale conversion
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
    
        Returns
        -------
        image_gray : cp.ndarray
            Grayscale frame. Shape 3D array (height, width, 3) in RGB 4:4:4 format.
        
    """
def ycbcr_to_rgb(image: cp.ndarray) -> cp.ndarray:
    """
    
        Convert YCbCr to RGB
    
        Parameters
        ----------
        image : cp.ndarray
            Input frame. Shape 3D array (height, width, 3) in YCbCr format.
    
        Returns
        -------
        frame_rgb : cp.ndarray
            Output frame. Shape 3D array (height, width, 3) in RGB format.
        
    """
OFFS_C_CENTER: float = 0.5
OFFS_Y_L: float = 0.06256109481915934
SCALE_C_F2L: float = 0.8758553274682307
SCALE_C_L2F: float = 1.1417410714285714
SCALE_Y_F2L: float = 0.8563049853372434
SCALE_Y_L2F: float = 1.167808219178082
__test__: dict = {}
rgb_to_ycbcr_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
rgb_to_ycbcr_kernel_code: str = '\nextern "C" __global__\nvoid rgb_to_ycbcr_kernel(const float* rgb, float* ycbcr, int width, int height) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n    float r = rgb[idx];\n    float g = rgb[idx + 1];\n    float b = rgb[idx + 2];\n\n    // --- Rec.709 full-range -------------------------------- ★\n    float y_f  = 0.2126f*r + 0.7152f*g + 0.0722f*b;\n    float cb_f = (b - y_f)/1.8556f + 0.5f;   // = (B\'-Y\')/(2*(1-K_b))+0.5\n    float cr_f = (r - y_f)/1.5748f + 0.5f;   // = (R\'-Y\')/(2*(1-K_r))+0.5\n\n    float y_component  = y_f;\n    float cb_component = cb_f;\n    float cr_component = cr_f;\n\n    ycbcr[idx] = y_component;\n    ycbcr[idx + 1] = cb_component;\n    ycbcr[idx + 2] = cr_component;\n}\n'
ycbcr_full_to_legal_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
ycbcr_full_to_legal_kernel_code: str = '\nextern "C" __global__\nvoid ycbcr_full_to_legal(const float* in, float* out,\n                         int w, int h) {{\n    int x = blockIdx.x*blockDim.x + threadIdx.x;\n    int y = blockIdx.y*blockDim.y + threadIdx.y;\n    if (x>=w || y>=h) return;\n\n    int idx = (y*w + x)*3;\n    float Y  = in[idx    ];\n    float Cb = in[idx + 1];\n    float Cr = in[idx + 2];\n\n    Y  = Y  * {SCALE_Y_F2L:f} + {OFFS_Y_L:f};\n    Cb = (Cb - {OFFS_C_CENTER:f})*{SCALE_C_F2L:f} + {OFFS_C_CENTER:f};\n    Cr = (Cr - {OFFS_C_CENTER:f})*{SCALE_C_F2L:f} + {OFFS_C_CENTER:f};\n\n    out[idx    ] = Y;\n    out[idx + 1] = Cb;\n    out[idx + 2] = Cr;\n}}\n'
ycbcr_legal_to_full_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
ycbcr_legal_to_full_kernel_code: str = '\nextern "C" __global__\nvoid ycbcr_legal_to_full(const float* in, float* out,\n                         int w, int h) {{\n    int x = blockIdx.x*blockDim.x + threadIdx.x;\n    int y = blockIdx.y*blockDim.y + threadIdx.y;\n    if (x>=w || y>=h) return;\n\n    int idx = (y*w + x)*3;\n    float Y  = in[idx    ];\n    float Cb = in[idx + 1];\n    float Cr = in[idx + 2];\n\n    Y  = (Y  - {OFFS_Y_L:f}) * {SCALE_Y_L2F:f};\n    Cb = (Cb - {OFFS_C_CENTER:f}) * {SCALE_C_L2F:f} + {OFFS_C_CENTER:f};\n    Cr = (Cr - {OFFS_C_CENTER:f}) * {SCALE_C_L2F:f} + {OFFS_C_CENTER:f};\n\n    out[idx    ] = Y;\n    out[idx + 1] = Cb;\n    out[idx + 2] = Cr;\n}}\n'
ycbcr_to_rgb_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
ycbcr_to_rgb_kernel_code: str = '\nextern "C" __global__\nvoid ycbcr_to_rgb_kernel(const float* ycbcr, float* rgb, int width, int height) {\n    int x = blockIdx.x * blockDim.x + threadIdx.x;\n    int y = blockIdx.y * blockDim.y + threadIdx.y;\n    if (x >= width || y >= height) return;\n\n    int idx = (y * width + x) * 3;\n\n    float y_component  = ycbcr[idx];\n    float cb_component = ycbcr[idx + 1] - 0.5f;\n    float cr_component = ycbcr[idx + 2] - 0.5f;\n\n    float r = y_component + 1.5748f * cr_component;\n    float g = y_component - 0.1873f * cb_component - 0.4681f * cr_component;\n    float b = y_component + 1.8556f * cb_component;\n\n    rgb[idx] = r;\n    rgb[idx + 1] = g;\n    rgb[idx + 2] = b;\n}\n'
