from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import typing
__all__ = ['bgr_to_rgb', 'cp', 'np', 'rgb_to_bgr']
def bgr_to_rgb(image: np.ndarray | cp.ndarray) -> np.ndarray | cp.ndarray:
    """
    
        Convert BGR to RGB
    
        Parameters
        ----------
        image : np.ndarray | cp.ndarray
            Input image. Shape 3D array (height, width, 3) in BGR format.
    
        Returns
        -------
        image : np.ndarray | cp.ndarray
            Output image. Shape 3D array (height, width, 3) in RGB format.
        
    """
def rgb_to_bgr(image: np.ndarray | cp.ndarray) -> np.ndarray | cp.ndarray:
    """
    
        Convert RGB to BGR
    
        Parameters
        ----------
        image : np.ndarray | cp.ndarray
            Input image. Shape 3D array (height, width, 3) in RGB format.
    
        Returns
        -------
        image : np.ndarray | cp.ndarray
            Output image. Shape 3D array (height, width, 3) in BGR format.
        
    """
__test__: dict = {}
