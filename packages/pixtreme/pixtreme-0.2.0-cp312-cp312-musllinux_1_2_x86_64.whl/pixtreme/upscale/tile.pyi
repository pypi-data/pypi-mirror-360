from __future__ import annotations
import builtins as __builtins__
import cupy as cp
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_tensor
from pixtreme.utils.dtypes import to_float32
import torch as torch
__all__ = ['add_padding', 'batch_to_tile', 'cp', 'create_gaussian_weights', 'merge_tiles', 'tile_image', 'to_batch', 'to_cupy', 'to_float32', 'to_tensor', 'torch']
def add_padding(input_image: cp.ndarray, patch_size: int = 128, overlap: int = 16) -> cp.ndarray:
    ...
def batch_to_tile(batch: torch.Tensor) -> list[cp.ndarray]:
    """
    
        Convert a batch tensor to a list of tiles.
    
        Parameters
        ----------
        batch : torch.Tensor
            Batch tensor in the shape (N, channel, tile_size, tile_size).
    
        Returns
        -------
        list[cp.ndarray]
            List of image tiles in the shape (tile_size, tile_size, channel) in RGB format.
        
    """
def create_gaussian_weights(size: int, sigma: int) -> cp.ndarray:
    """
    
        Create a Gaussian weight map for tile blending.
    
        Parameters
        ----------
        size : int
            Size of the weight map.
        sigma : int
            Standard deviation for the Gaussian distribution.
    
        Returns
        -------
        cp.ndarray
            Gaussian weight map in the shape (size, size, 1).
        
    """
def merge_tiles(tiles: list[cp.ndarray], original_shape: tuple[int, int, int], padded_shape: tuple[int, int, int], scale: int, tile_size: int = 128, overlap: int = 16) -> cp.ndarray:
    ...
def tile_image(input_image: cp.ndarray, tile_size: int = 128, overlap: int = 16) -> tuple[list[cp.ndarray], tuple]:
    """
    
        Split the input image into overlapping tiles.
    
        Parameters
        ----------
        input_image : cp.ndarray
            Input image in the shape (height, width, channel) in RGB format.
        tile_size : int, optional
            Size of each tile, by default 128.
        overlap : int, optional
            Overlap between tiles, by default 16.
    
        Returns
        -------
        list[cp.ndarray]
            List of image tiles, each in the shape (tile_size, tile_size, channel) in RGB format.
        
    """
def to_batch(tiles: list[cp.ndarray]) -> torch.Tensor:
    """
    
        Convert a list of tiles to a batch tensor.
    
        Parameters
        ----------
        tiles : list[cp.ndarray]
            List of image tiles in the shape (tile_size, tile_size, channel) in RGB format.
    
        Returns
        -------
        torch.Tensor
            Batch tensor in the shape (N, channel, tile_size, tile_size).
        
    """
__test__: dict = {}
