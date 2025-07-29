from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import hashlib as hashlib
import os as os
from platformdirs import user_cache_dir
__all__ = ['cp', 'hashlib', 'os', 'read_lut', 'user_cache_dir']
def read_lut(file_path: str, use_cache: bool = True) -> cp.ndarray:
    """
    
        Read a 3D LUT Cube file and return the LUT data as a CuPy ndarray.
    
        Parameters
        ----------
        file_path : str
            The path to the LUT file. Must be a .cube file.
        use_cache : bool, optional
            Whether to use the cache, by default True
    
        Returns
        -------
        lut_data : cp.ndarray
            The LUT data. The shape is (N, N, N, 3). dtype is float32.
    
        
    """
__test__: dict = {}
