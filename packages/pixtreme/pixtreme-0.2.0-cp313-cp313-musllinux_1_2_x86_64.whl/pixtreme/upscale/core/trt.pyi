from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import tensorrt as trt
import typing
__all__ = ['TrtUpscaler', 'cp', 'trt']
class TrtUpscaler:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0) -> None:
        """
        
                Initialize the TrtUpscaler.
        
                Args:
                    model_path (str): Path to the TensorRT engine file or ONNX model.
                Raises:
                    FileNotFoundError: If the specified path does not exist.
                
        """
    def _get(self, input_frame: cp.ndarray) -> cp.ndarray:
        ...
    def get(self, input_frame: cp.ndarray | list[cp.ndarray]) -> cp.ndarray | list[cp.ndarray]:
        ...
    def initialize(self):
        """
        Initialize processing
        """
    def post_process(self, output_frame: cp.ndarray) -> cp.ndarray:
        """
        Optimized post-processing
        """
    def pre_process(self, input_frame: cp.ndarray) -> cp.ndarray:
        """
        Execute preprocessing in-place
        """
__test__: dict = {}
