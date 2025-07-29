from __future__ import annotations
import builtins as __builtins__
import cupy as cp
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.transform.resize import resize
__all__ = ['bgr_to_rgb', 'cp', 'resize', 'to_blob', 'to_blobs']
def to_blob(image: cp.ndarray, scalefactor: float = 1.0, size = None, mean = (0, 0, 0), swapRB: bool = False, fp16: bool = False) -> cp.ndarray:
    """
    
        Convert an image to a blob.
    
        Parameters
        ----------
        image : cp.ndarray
            The input image in RGB format.
        scalefactor : float (optional)
            The scale factor to apply. by default 1.0
        size : tuple (optional)
            The size of the output image. by default None
        mean : tuple (optional)
            The mean value to subtract. by default (0, 0, 0)
        swapRB : bool (optional)
            Swap the R and B channels. by default False
    
        Returns
        -------
        cp.ndarray
            The blob image in CHW format.
        
    """
def to_blobs(images: list[cp.ndarray], scalefactor: float = 1.0, size = None, mean = (0, 0, 0), swapRB: bool = False, fp16: bool = False) -> cp.ndarray:
    """
    
        Convert a list of images to blobs.
        
    """
__test__: dict = {}
