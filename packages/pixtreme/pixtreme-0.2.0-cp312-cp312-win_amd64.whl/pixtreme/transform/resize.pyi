from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
from pixtreme.utils.dtypes import to_float32
import typing
__all__ = ['INTER_AREA', 'INTER_AUTO', 'INTER_B_SPLINE', 'INTER_CATMULL_ROM', 'INTER_CUBIC', 'INTER_LANCZOS2', 'INTER_LANCZOS3', 'INTER_LANCZOS4', 'INTER_LINEAR', 'INTER_MITCHELL', 'INTER_NEAREST', 'area_kernel', 'bicubic_kernel', 'bilinear_kernel', 'cp', 'lanczos_kernel', 'mitchell_kernel', 'nearest_kernel', 'resize', 'to_float32']
def _resize(src: cp.ndarray, dsize: tuple[int, int] | None = None, fx: float | None = None, fy: float | None = None, interpolation: int = -1) -> cp.ndarray:
    """
    
        Resize the input image to the specified size.
    
        Parameters
        ----------
        image : cp.ndarray
            The input image in RGB or any channels format.
        dsize : tuple[int, int] | None (optional)
            The output image size. The format is (width, height). by default None.
        fx : float | None (optional)
            The scaling factor along the horizontal axis. by default None.
        fy : float | None (optional)
            The scaling factor along the vertical axis. by default None.
        interpolation : int (optional)
            The interpolation method to use. by default 1, options are: 0 for nearest neighbor, 1 for bilinear, 2 for bicubic, 3 for area, 4 for Lanczos4.
    
        Returns
        -------
        image_resized : cp.ndarray
            The resized image. The shape is (height, width, channels). dtype is float32.
    
        
    """
def resize(src: cp.ndarray | list[cp.ndarray], dsize: tuple[int, int] | None = None, fx: float | None = None, fy: float | None = None, interpolation: int = -1) -> cp.ndarray | list[cp.ndarray]:
    """
    
        Resize the input image or list of images to the specified size.
    
        Parameters
        ----------
        src : np.ndarray | cp.ndarray | list[np.ndarray | cp.ndarray]
            The input image or list of images in RGB or any channels format.
        dsize : tuple[int, int] | None (optional)
            The output image size. The format is (width, height). by default None.
        fx : float | None (optional)
            The scaling factor along the horizontal axis. by default None.
        fy : float | None (optional)
            The scaling factor along the vertical axis. by default None.
        interpolation : int (optional)
            The interpolation method to use. by default 1, options are: 0 for nearest neighbor, 1 for bilinear, 2 for bicubic, 3 for area, 4 for Lanczos4.
    
        Returns
        -------
        np.ndarray | cp.ndarray | list[np.ndarray | cp.ndarray]
            The resized image or list of resized images. The shape is (height, width, channels). dtype is float32.
    
        
    """
INTER_AREA: int = 3
INTER_AUTO: int = -1
INTER_B_SPLINE: int = 23
INTER_CATMULL_ROM: int = 22
INTER_CUBIC: int = 2
INTER_LANCZOS2: int = 10
INTER_LANCZOS3: int = 11
INTER_LANCZOS4: int = 4
INTER_LINEAR: int = 1
INTER_MITCHELL: int = 21
INTER_NEAREST: int = 0
__test__: dict = {}
area_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
bicubic_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
bilinear_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
lanczos_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
mitchell_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
nearest_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
