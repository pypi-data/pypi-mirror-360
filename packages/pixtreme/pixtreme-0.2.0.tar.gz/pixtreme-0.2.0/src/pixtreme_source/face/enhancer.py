import cupy as cp
import numpy as np
import onnxruntime

from ..color.bgr import bgr_to_rgb, rgb_to_bgr
from ..transform.resize import INTER_AUTO, resize
from ..utils.blob import to_blob
from ..utils.dlpack import to_cupy, to_numpy
from ..utils.dtypes import to_float32
from .schema import PxFace


class GFPGAN:
    def __init__(self, model_file, *args, **kwargs):
        self.session = onnxruntime.InferenceSession(model_file, **kwargs)
        self.input_size = 512

    def forward(self, image: cp.ndarray, density: int = 1) -> np.ndarray:
        image = to_float32(image)

        image_input_size = image.shape[1]
        image = bgr_to_rgb(image)
        if density > 1:
            image = resize(image, (image_input_size // density, image_input_size // density), interpolation=INTER_AUTO)
        image = resize(image, (self.input_size, self.input_size), interpolation=INTER_AUTO)

        image = (image - 0.5) * 2
        blob = cp.expand_dims(image, axis=0).transpose(0, 3, 1, 2)
        blob = to_numpy(blob)

        net_outs = self.session.run(None, {self.session.get_inputs()[0].name: blob})
        assert isinstance(net_outs[0], np.ndarray), "Output of the model is not a numpy array."
        net_out = net_outs[0][0]

        net_out = to_cupy(net_out)
        net_out = net_out.transpose(1, 2, 0)
        net_out = cp.clip(net_out, -1, 1)
        net_out = net_out / 2 + 0.5
        result = rgb_to_bgr(net_out)
        result = to_float32(result)

        return result
