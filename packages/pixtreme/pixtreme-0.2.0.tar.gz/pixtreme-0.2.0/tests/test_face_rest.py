import pixtreme_source as px


def test_face_rest():
    enhancer = px.GFPGAN(model_file="models/face/GFPGANv1.4.onnx")

    source_image_path = "examples/example2.png"

    image = px.imread(source_image_path)
    small_image = px.resize(image, (128, 128), interpolation=px.INTER_AREA)
    enhanced_image = enhancer.forward(small_image, density=1)

    px.imshow("Original Image", small_image)
    px.imshow("Enhanced Image", enhanced_image)
    px.waitkey(0)
    px.destroy_all_windows()
