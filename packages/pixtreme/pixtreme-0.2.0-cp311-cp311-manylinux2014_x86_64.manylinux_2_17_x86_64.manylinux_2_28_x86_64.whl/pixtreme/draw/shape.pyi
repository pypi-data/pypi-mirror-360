from __future__ import annotations
import builtins as __builtins__
import cupy as cp
__all__ = ['circle', 'cp', 'rectangle']
def circle(image: cp.ndarray, center_x, center_y, radius, color = (1.0, 1.0, 1.0)) -> cp.ndarray:
    """
    
        Draw a circle on the image using CuPy.
    
        Args:
            image: cp.ndarray
                Target image array (H, W, C)
            center_x: int
                Pixel X coordinate of the circle center
            center_y: int
                Pixel Y coordinate of the circle center
            radius: int
                Circle radius
            color: tuple, optional
                Circle color (R, G, B), by default (1.0, 1.0, 1.0)
        
    """
def rectangle(image: cp.ndarray, top_left_x, top_left_y, bottom_right_x, bottom_right_y, color = (1.0, 1.0, 1.0)) -> cp.ndarray:
    """
    
        Draw a rectangle on the image using CuPy.
    
        Args:
            image: cp.ndarray
                Target image array (H, W, C)
            top_left_x: int
                Pixel X coordinate of the top-left corner
            top_left_y: int
                Pixel Y coordinate of the top-left corner
            bottom_right_x: int
                Pixel X coordinate of the bottom-right corner
            bottom_right_y: int
                Pixel Y coordinate of the bottom-right corner
            color: tuple, optional
                Rectangle color (R, G, B), by default (1.0, 1.0, 1.0)
        
    """
__test__: dict = {}
