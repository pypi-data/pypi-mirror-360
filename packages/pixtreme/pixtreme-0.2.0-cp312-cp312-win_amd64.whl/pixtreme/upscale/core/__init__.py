from .onnx import OnnxUpscaler
from .torch import TorchUpscaler
from .trt import TrtUpscaler

__all__ = [
    "OnnxUpscaler",
    "TorchUpscaler",
    "TrtUpscaler",
]
