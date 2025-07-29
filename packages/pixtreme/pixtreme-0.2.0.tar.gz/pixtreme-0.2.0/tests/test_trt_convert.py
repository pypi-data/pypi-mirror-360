import os
import timeit

import pixtreme_source as px


def test_trt_convert():
    # Test ONNX to TRT conversion with fixed shape
    pth_path = "models/4xNomos2_hq_dat2.pth"
    onnx_path = "models/4xNomos2_hq_dat2.onnx"
    trt_path = "models/4xNomos2_hq_dat2.trt"

    if not os.path.exists(pth_path):
        raise FileNotFoundError(f"Model file not found: {pth_path}")

    if not os.path.exists(onnx_path):
        px.torch_to_onnx(model_path=pth_path, onnx_path=onnx_path, device="cpu", precision="fp32")

    """
    if not os.path.exists(trt_path) and os.path.exists(onnx_path):
        px.onnx_to_trt_dynamic_shape(
            onnx_path=onnx_path,
            engine_path=trt_path,
            precision="tf32",
        )
    """


def test_check_torch_model():
    pth_path = "models/4xNomos2_hq_dat2.pth"

    px.upscale.check_torch_model(model_path=pth_path)


def test_check_onnx_model():
    onnx_path = "models/4xNomos2_hq_dat2.onnx"

    if not os.path.exists(onnx_path):
        raise FileNotFoundError(f"ONNX model file not found: {onnx_path}")

    px.upscale.check_onnx_model(model_path=onnx_path)


def test_infer_torch():
    itr = 100
    pth_path = "models/4xNomos2_hq_dat2.pth"

    if not os.path.exists(pth_path):
        raise FileNotFoundError(f"Model file not found: {pth_path}")

    upscaler = px.TorchUpscaler(model_path=pth_path, device="cuda")

    source_image_path = "examples/example.png"
    if not os.path.exists(source_image_path):
        raise FileNotFoundError(f"Source image not found: {source_image_path}")

    source_image = px.imread(source_image_path)
    source_image = px.to_float32(source_image)

    enhanced_image = None
    start = timeit.default_timer()
    for _ in range(itr):
        enhanced_image = upscaler.get(source_image)
    end = timeit.default_timer()
    print(f"Torch Upscaler inference time: {(end - start) / itr:.4f} seconds per iteration")
    print(f"Torch Upscaler FPS: {itr / (end - start):.2f}")
    print(f"Torch Upscaler total time: {end - start:.4f} seconds")

    assert enhanced_image is not None, "Enhanced image is None"
    px.imshow("Enhanced Image", enhanced_image)
    px.waitkey(0)
    px.destroy_all_windows()


def test_infer_onnx():
    itr = 100
    onnx_path = "models/4xNomos2_hq_dat2.onnx"
    if not os.path.exists(onnx_path):
        raise FileNotFoundError(f"ONNX model file not found: {onnx_path}")

    upscaler = px.OnnxUpscaler(model_path=onnx_path)

    source_image_path = "examples/example.png"
    if not os.path.exists(source_image_path):
        raise FileNotFoundError(f"Source image not found: {source_image_path}")

    source_image = px.imread(source_image_path)
    source_image = px.to_float32(source_image)

    enhanced_image = None
    start = timeit.default_timer()
    for _ in range(itr):
        enhanced_image = upscaler.get(source_image)
    end = timeit.default_timer()
    print(f"ONNX Upscaler inference time: {(end - start) / itr:.4f} seconds per iteration")
    print(f"ONNX Upscaler FPS: {itr / (end - start):.2f}")
    print(f"ONNX Upscaler total time: {end - start:.4f} seconds")

    assert enhanced_image is not None, "Enhanced image is None"
    px.imshow("Enhanced Image", enhanced_image)
    px.waitkey(0)
    px.destroy_all_windows()
