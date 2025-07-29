from __future__ import annotations
import builtins as __builtins__
import cupy as cp
from pixtreme.draw.shape import circle
from pixtreme.draw.shape import rectangle
from pixtreme.filter.gaussian import gaussian_blur
from pixtreme.transform.resize import resize
__all__ = ['INTER_AUTO', 'circle', 'cp', 'create_rounded_mask', 'gaussian_blur', 'rectangle', 'resize']
def create_rounded_mask(dsize: tuple = (512, 512), mask_offsets: tuple = (0.1, 0.1, 0.1, 0.1), radius_ratio: float = 0.1, density: int = 1, blur_size: int = 0, sigma: float = 1.0) -> cp.ndarray:
    """
    
        Create a rounded rectangle mask with anti-aliasing and optional blurring.
    
        Args:
            size: Size of the mask (height and width)
            mask_offsets: (top, left, bottom, right) offset ratios
            radius_ratio: Corner roundness ratio
            density: Scale factor for anti-aliasing
            blur_size: Blur size ratio
    
        Returns:
            cupy.ndarray: Rounded rectangle mask with anti-aliasing and optional blurring.
        
    """
INTER_AUTO: int = -1
__test__: dict = {}
