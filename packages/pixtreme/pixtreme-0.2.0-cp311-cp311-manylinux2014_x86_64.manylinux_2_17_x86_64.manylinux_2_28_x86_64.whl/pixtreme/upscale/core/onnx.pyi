from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import onnxruntime as onnxruntime
import typing
__all__ = ['OnnxUpscaler', 'cp', 'onnxruntime']
class OnnxUpscaler:
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device_id: int = 0, provider_options: list | None = None) -> None:
        ...
    def _ensure_buffers(self, input_shape):
        """
        Ensure necessary buffers are allocated (optimized version)
        """
    def _get(self, image: cp.ndarray) -> cp.ndarray:
        ...
    def get(self, image: cp.ndarray | list[cp.ndarray]) -> cp.ndarray | list[cp.ndarray]:
        ...
    def post_process(self, output_frame: cp.ndarray) -> cp.ndarray:
        """
        Optimized post-processing
        """
    def pre_process(self, input_frame: cp.ndarray) -> cp.ndarray:
        """
        Optimized in-place preprocessing
        """
__test__: dict = {}
