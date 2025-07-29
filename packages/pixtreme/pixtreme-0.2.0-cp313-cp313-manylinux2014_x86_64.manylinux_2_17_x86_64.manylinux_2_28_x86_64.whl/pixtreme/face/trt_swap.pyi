from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.color.bgr import rgb_to_bgr
from pixtreme.face.emap import load_emap
from pixtreme.face.schema import PxFace
from pixtreme.transform.resize import resize
from pixtreme.utils.blob import to_blob
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dlpack import to_numpy
import tensorrt as trt
import typing
__all__ = ['INTER_AUTO', 'PxFace', 'TrtFaceSwap', 'bgr_to_rgb', 'cp', 'load_emap', 'np', 'resize', 'rgb_to_bgr', 'to_blob', 'to_cupy', 'to_numpy', 'trt']
class TrtFaceSwap:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0) -> None:
        """
        
                Initialize the TrtFaceSwap.
        
                Args:
                    model_path (str): Path to the TensorRT engine file.
                    model_bytes (bytes): TensorRT engine bytes.
                    device_id (int): CUDA device ID.
                Raises:
                    FileNotFoundError: If the specified path does not exist.
                
        """
    def forward(self, img: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        Forward pass using TensorRT
        """
    def get(self, target_face: PxFace, source_face: PxFace) -> cp.ndarray:
        """
        Perform face swap
        """
    def initialize(self):
        """
        Initialize processing
        """
INTER_AUTO: int = -1
__test__: dict = {}
