from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupy._core.raw
import numpy as np
__all__ = ['INTER_AREA', 'INTER_AUTO', 'INTER_B_SPLINE', 'INTER_CATMULL_ROM', 'INTER_CUBIC', 'INTER_LANCZOS2', 'INTER_LANCZOS3', 'INTER_LANCZOS4', 'INTER_LINEAR', 'INTER_MITCHELL', 'INTER_NEAREST', 'affine_transform', 'area_affine_kernel', 'bicubic_affine_kernel', 'bilinear_affine_kernel', 'cp', 'crop_from_kps', 'get_inverse_matrix', 'lanczos_affine_kernel', 'mitchell_affine_kernel', 'nearest_affine_kernel', 'np']
def affine_transform(src: cp.ndarray, M: cp.ndarray, dsize: tuple, flags: int = -1) -> cp.ndarray:
    """
    
        Apply an affine transformation to the input image. Using CUDA.
    
        Parameters
        ----------
        src : cp.ndarray
            The image in BGR format.
        M : cp.ndarray
            The transformation matrix. The input matrix. 2 x 3.
        dst_shape : cp.ndarray
            The shape of the destination image (height, width, channels).
    
        Returns
        -------
        cp.ndarray
            The transformed image in BGR format.
        
    """
def crop_from_kps(image: cp.ndarray, kps: cp.ndarray, size: int = 512) -> tuple[cp.ndarray, cp.ndarray]:
    """
    
        Get the affine matrix from keypoints.
    
        Parameters
        ----------
        image : cp.ndarray
            The frame, RGB format. height, width, channels.
        size : int
            The size of the output image.
        kps : cp.ndarray
            The source keypoints. left eye(top-left), right eye(top-right), nose(center), mouth left(bottom-left), mouth right(bottom-right)
    
        Returns
        -------
        cp.ndarray
            The affine matrix. 2 x 3.
        
    """
def get_inverse_matrix(M: cp.ndarray) -> cp.ndarray:
    """
    
        Get the inverse of the affine matrix.
    
        Parameters
        ----------
        M : Union[np.ndarray, cp.ndarray]
            The input matrix. 2 x 3.
    
        Returns
        -------
        Union[np.ndarray, cp.ndarray]
            The inverse matrix. 2 x 3.
        
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
area_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
bicubic_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
bilinear_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
lanczos_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
mitchell_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
nearest_affine_kernel: cupy._core.raw.RawKernel  # value = <cupy._core.raw.RawKernel object>
