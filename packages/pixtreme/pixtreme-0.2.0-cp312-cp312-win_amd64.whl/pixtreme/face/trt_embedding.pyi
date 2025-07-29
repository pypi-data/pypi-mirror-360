from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
from pixtreme.color.bgr import bgr_to_rgb
from pixtreme.face.schema import PxFace
from pixtreme.utils.blob import to_blobs
from pixtreme.utils.dlpack import to_cupy
from pixtreme.utils.dtypes import to_float32
import tensorrt as trt
import typing
__all__ = ['PxFace', 'TrtFaceEmbedding', 'bgr_to_rgb', 'cp', 'np', 'to_blobs', 'to_cupy', 'to_float32', 'trt']
class TrtFaceEmbedding:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0) -> None:
        """
        
                Initialize the TrtFaceEmbedding.
        
                Args:
                    model_path (str): Path to the TensorRT engine file.
                    model_bytes (bytes): TensorRT engine bytes.
                    device_id (int): CUDA device ID.
                Raises:
                    FileNotFoundError: If the specified path does not exist.
                
        """
    def forward(self, batch_data: cp.ndarray) -> cp.ndarray:
        """
        Forward pass using TensorRT
        """
    def get(self, face: PxFace) -> PxFace:
        """
        Extract embedding for a single face
        """
    def get_feat(self, imgs: list[cp.ndarray] | cp.ndarray) -> cp.ndarray:
        """
        Extract features from image(s)
        """
    def initialize(self):
        """
        Initialize processing
        """
__test__: dict = {}
