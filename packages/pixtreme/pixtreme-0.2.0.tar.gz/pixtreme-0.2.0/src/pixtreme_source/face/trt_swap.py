from typing import Optional

import cupy as cp
import numpy as np
import tensorrt as trt

from ..color.bgr import bgr_to_rgb, rgb_to_bgr
from ..transform.resize import INTER_AUTO, resize
from ..utils.blob import to_blob
from ..utils.dlpack import to_cupy, to_numpy
from .emap import load_emap
from .schema import PxFace


class TrtFaceSwap:
    def __init__(self, model_path: Optional[str] = None, model_bytes: Optional[bytes] = None, device_id: int = 0) -> None:
        """
        Initialize the TrtFaceSwap.

        Args:
            model_path (str): Path to the TensorRT engine file.
            model_bytes (bytes): TensorRT engine bytes.
            device_id (int): CUDA device ID.
        Raises:
            FileNotFoundError: If the specified path does not exist.
        """

        self.device_id = device_id

        with cp.cuda.Device(self.device_id):
            # Load the TensorRT engine
            self.logger = trt.Logger(trt.Logger.WARNING)
            self.runtime = trt.Runtime(self.logger)

            if model_path is not None:
                with open(model_path, "rb") as f:
                    model_bytes = f.read()

            if model_bytes is None:
                raise ValueError("model_bytes must be provided if model_path is not specified")

            self.engine = self.runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()

            print("face swap engine loaded ✔  tensors:", self.engine)

            # Load emap for embedding transformation
            self.emap = load_emap()
            # Convert emap to CuPy array for GPU processing
            self.emap = cp.asarray(self.emap)

            self.initialize()

    def initialize(self):
        """Initialize processing"""
        # Prepare CuPy stream and device buffers
        self.stream = cp.cuda.Stream()
        self.d_inputs = {}
        self.d_outputs = {}

        # Automatically get tensor names
        input_names = []
        output_names = []

        for name in self.engine:
            shape = self.ctx.get_tensor_shape(name)
            dtype = trt.nptype(self.engine.get_tensor_dtype(name))

            # Convert TensorRT shape to list for CuPy compatibility
            shape_list = [int(dim) for dim in shape]

            # Create a CuPy array for the tensor
            d_arr = cp.empty(shape_list, dtype=dtype)

            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                self.d_inputs[name] = d_arr
                input_names.append(name)
            else:
                self.d_outputs[name] = d_arr
                output_names.append(name)

        # Store input/output names
        self.input_names = input_names
        self.output_names = output_names

        # Set tensor addresses only once during initialization
        for name in self.engine:
            if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                self.ctx.set_tensor_address(name, self.d_inputs[name].data.ptr)
            else:
                self.ctx.set_tensor_address(name, self.d_outputs[name].data.ptr)

        # Get input/output shapes
        if len(input_names) >= 1:
            self.input_shape = list(self.d_inputs[input_names[0]].shape)
            self.input_size = tuple(self.input_shape[2:4][::-1]) if len(self.input_shape) >= 4 else (128, 128)

        if len(output_names) >= 1:
            self.output_shape = list(self.d_outputs[output_names[0]].shape)

        # Set normalization parameters
        self.input_mean = 0.0
        self.input_std = 1.0

        print(f"Input names: {self.input_names}")
        print(f"Output names: {self.output_names}")
        print(f"Input shape: {self.input_shape}")
        print(f"Input size: {self.input_size}")
        print(f"Output shape: {self.output_shape}")

        # Buffer pool
        self.input_buffer = None
        self.latent_buffer = None

    def forward(self, img: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """Forward pass using TensorRT"""
        # Normalize input data
        normalized_img = (img - self.input_mean) / self.input_std

        # Copy input data to GPU buffers
        img_input = self.d_inputs[self.input_names[0]]
        latent_input = self.d_inputs[self.input_names[1]]

        # Handle dynamic shapes if needed
        if img_input.shape != normalized_img.shape:
            del self.d_inputs[self.input_names[0]]
            img_input = cp.empty(normalized_img.shape, dtype=normalized_img.dtype)
            self.d_inputs[self.input_names[0]] = img_input
            self.ctx.set_tensor_address(self.input_names[0], img_input.data.ptr)

        if latent_input.shape != latent.shape:
            del self.d_inputs[self.input_names[1]]
            latent_input = cp.empty(latent.shape, dtype=latent.dtype)
            self.d_inputs[self.input_names[1]] = latent_input
            self.ctx.set_tensor_address(self.input_names[1], latent_input.data.ptr)

        # Copy data
        img_input[:] = normalized_img
        latent_input[:] = latent

        # Execute the TensorRT engine asynchronously
        self.ctx.execute_async_v3(self.stream.ptr)

        # Wait for inference completion
        self.stream.synchronize()

        # Get output data
        out_gpu = self.d_outputs[self.output_names[0]]

        # Return a copy to avoid memory issues
        return cp.copy(out_gpu)

    def get(self, target_face: PxFace, source_face: PxFace) -> cp.ndarray:
        """Perform face swap"""
        try:
            assert target_face.image is not None
            assert source_face.normed_embedding is not None
            image = target_face.image
            normed_embedding = source_face.normed_embedding
            target_size = image.shape[:2]

            image = bgr_to_rgb(image)

            # Resize to model input size
            aimage = resize(image, (128, 128), interpolation=INTER_AUTO)

            # Convert to blob format
            blob = to_blob(aimage, 1.0 / self.input_std, (128, 128), (self.input_mean, self.input_mean, self.input_mean))

            # Transform embedding using emap
            latent = normed_embedding.reshape((1, -1))
            latent = cp.dot(latent, self.emap)
            latent = latent / cp.linalg.norm(latent)

            # Run inference
            pred = self.forward(blob, latent)

            # Post-process output
            img_fake = pred.transpose((0, 2, 3, 1))[0]
            img_fake = cp.clip(img_fake, 0, 1).astype(cp.float32)
            img_fake = rgb_to_bgr(img_fake)
            img_fake = resize(img_fake, (target_size[1], target_size[0]), interpolation=INTER_AUTO)

            return img_fake
        except Exception as e:
            raise e
