import os
import timeit

import cupy as cp

import pixtreme_source as px


def test_trt_face():
    face_detection_onnx_path = "models/face/detection.onnx"
    face_detection_trt_path = "models/face/detection.trt"
    face_embedding_onnx_path = "models/face/embedding.onnx"
    face_embedding_trt_path = "models/face/embedding.trt"
    face_swap_onnx_path = "models/face/swap.onnx"
    face_swap_trt_path = "models/face/swap.trt"
    # px.onnx_to_trt_fixed_shape(
    #    onnx_path=face_detection_onnx_path, engine_path=face_detection_trt_path, fixed_shape=(1, 3, 640, 640)
    # )
    # px.onnx_to_trt_fixed_shape(
    #    onnx_path=face_embedding_onnx_path, engine_path=face_embedding_trt_path, fixed_shape=(1, 3, 112, 112)
    # )
    # px.onnx_to_trt_fixed_shape(onnx_path=face_swap_onnx_path, engine_path=face_swap_trt_path, fixed_shape=(1, 3, 128, 128))
    # return

    enhancer = px.GFPGAN(model_file="models/face/GFPGANv1.4.onnx")

    source_image_path = "examples/example2.png"
    if not os.path.exists(source_image_path):
        raise FileNotFoundError(f"Source image not found: {source_image_path}")
    source_image = px.imread(source_image_path)
    source_image = px.to_float32(source_image)

    target_image_path = "examples/example3.png"
    if not os.path.exists(target_image_path):
        raise FileNotFoundError(f"Target image not found: {target_image_path}")
    target_image = px.imread(target_image_path)
    target_image = px.to_float32(target_image)

    itr = 100

    # detector = px.FaceDetection(model_path=face_detection_onnx_path)
    detector = px.TrtFaceDetection(model_path=face_detection_trt_path)
    # embedding = px.FaceEmbedding(model_path=face_embedding_onnx_path)
    embedding = px.TrtFaceEmbedding(model_path=face_embedding_trt_path)
    # swapper = px.FaceSwap(model_path=face_swap_onnx_path)
    swapper = px.TrtFaceSwap(model_path=face_swap_trt_path)

    pth_model_path = "models/4xNomos2_hq_dat2.pth"
    trt_model_path = "models/4x-nomos2-hq-dat2.trt"

    if not os.path.exists(trt_model_path):
        if not os.path.exists(pth_model_path):
            raise FileNotFoundError(f"Model file not found: {pth_model_path}")
        px.torch_to_onnx(
            model_path=pth_model_path,
            onnx_path="models/upscale/4x-nomos2-hq-dat2.onnx",
            input_shape=(1, 3, 128, 128),
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        )
        px.onnx_to_trt_dynamic_shape(
            onnx_path="models/upscale/4x-nomos2-hq-dat2.onnx",
            engine_path=trt_model_path,
        )

    upscaler = px.TrtUpscaler(model_path="models/upscale/2x-spanx2-ch48.trt", device_id=0)

    source_faces = detector.get(source_image)
    source_face = source_faces[0] if source_faces else None
    assert source_face is not None, "No face detected in source image."
    source_face = embedding.get(source_face)
    # print(f"Embedding shape: {face.embedding}")

    start = timeit.default_timer()
    pasted_image = None

    mask = px.create_rounded_mask(dsize=(512, 512), mask_offsets=(0.2, 0.2, 0.2, 0.2), density=1, blur_size=51, sigma=16.0)
    px.imshow("Mask", mask)

    for _ in range(itr):
        target_faces = detector.get(target_image)
        target_face = target_faces[0] if target_faces else None
        assert target_face is not None, "No face detected in target image."
        target_face = embedding.get(target_face)

        swapped_face_image: cp.ndarray = swapper.get(target_face, source_face)
        swapped_face_image = enhancer.forward(swapped_face_image, density=1)
        pasted_image = px.paste_back(
            target_image=target_image, paste_image=swapped_face_image, M=target_face.matrix, mask=mask
        )

    end = timeit.default_timer()
    fps = itr / (end - start)
    per_time = (end - start) / itr
    print(f"Processed {itr} iterations in {end - start:.2f} seconds.")
    print(f"FPS: {fps:.2f}, Time per iteration: {per_time:.4f} seconds.")

    assert pasted_image is not None, "Face swap failed."
    px.imshow("Swapped Face", pasted_image)
    px.waitkey(0)
    px.destroy_all_windows()
