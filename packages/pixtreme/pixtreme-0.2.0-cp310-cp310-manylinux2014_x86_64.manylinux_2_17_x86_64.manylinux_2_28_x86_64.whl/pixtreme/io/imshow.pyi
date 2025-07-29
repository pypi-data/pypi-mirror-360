from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cv2 as cv2
import numpy as np
from nvidia import nvimgcodec
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.transform.resize import resize
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
from pixtreme.utils.dtypes import to_float32
from pixtreme.utils.dtypes import to_uint8
import torch as torch
import typing
__all__ = ['cp', 'cv2', 'destroy_all_windows', 'imshow', 'np', 'nvimgcodec', 'resize', 'rgb_to_bgr', 'to_cupy', 'to_float32', 'to_numpy', 'to_uint8', 'torch', 'waitkey']
def destroy_all_windows() -> None:
    """
    
        Destroy all windows.
        
    """
def imshow(title: str, image: np.ndarray | cp.ndarray | nvimgcodec.Image, scale: float = 1.0, is_rgb: bool = False) -> None:
    """
    
        Image show function for numpy and cupy arrays. in RGB format.
    
        Parameters
        ----------
        title : str
            Window title
        image : np.ndarray | cp.ndarray | nvimgcodec.Image
            Image to show
        scale : float, optional
            Scale factor, by default 1.0
        is_rgb : bool, optional
            If True, the image will be shown in RGB format, by default False
    
        Raises
        ------
        KeyboardInterrupt
            If the user presses the ESC key, the window will close and the KeyboardInterrupt will be raised.
        
    """
def waitkey(delay: int) -> int:
    """
    
        Wait for a pressed key.
    
        Parameters
        ----------
        delay : int, optional
            Delay in milliseconds, by default 0
    
        Returns
        -------
        int
            Key code
        
    """
__test__: dict = {}
