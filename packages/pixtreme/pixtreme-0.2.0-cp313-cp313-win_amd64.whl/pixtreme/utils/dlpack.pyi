from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
from nvidia import nvimgcodec
import torch as torch
import typing
__all__ = ['cp', 'np', 'nvimgcodec', 'to_cupy', 'to_numpy', 'to_tensor', 'torch']
def to_cupy(image: np.ndarray | torch.Tensor | nvimgcodec.Image) -> cp.ndarray:
    ...
def to_numpy(image: cp.ndarray | torch.Tensor | nvimgcodec.Image) -> np.ndarray:
    ...
def to_tensor(image: np.ndarray | cp.ndarray | nvimgcodec.Image, device: str | torch.device | None = None) -> torch.Tensor:
    ...
__test__: dict = {}
