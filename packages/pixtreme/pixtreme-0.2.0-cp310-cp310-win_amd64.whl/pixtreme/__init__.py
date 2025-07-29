import cupy as cp

from .color import (
    aces2065_1_to_acescct,
    aces2065_1_to_acescg,
    aces2065_1_to_rec709,
    acescct_to_aces2065_1,
    acescg_to_aces2065_1,
    apply_lut,
    apply_lut_cp,
    bgr_to_grayscale,
    bgr_to_hsv,
    bgr_to_rgb,
    bgr_to_ycbcr,
    hsv_to_bgr,
    hsv_to_rgb,
    ndi_uyvy422_to_ycbcr444,
    ndi_uyvy422_to_ycbcr444_cp,
    read_lut,
    rec709_to_aces2065_1,
    rgb_to_bgr,
    rgb_to_grayscale,
    rgb_to_hsv,
    rgb_to_ycbcr,
    uyvy422_to_ycbcr444,
    uyvy422_to_ycbcr444_cp,
    ycbcr_full_to_legal,
    ycbcr_legal_to_full,
    ycbcr_to_bgr,
    ycbcr_to_grayscale,
    ycbcr_to_rgb,
    yuv420p_to_ycbcr444,
    yuv420p_to_ycbcr444_cp,
    yuv422p10le_to_ycbcr444,
    yuv422p10le_to_ycbcr444_cp,
)
from .draw import circle, create_rounded_mask, rectangle
from .face import (
    GFPGAN,
    FaceDetection,
    FaceEmbedding,
    FaceSwap,
    PasteBack,
    PxFace,
    TrtFaceDetection,
    TrtFaceEmbedding,
    TrtFaceSwap,
    paste_back,
)
from .filter import GaussianBlur, gaussian_blur, get_gaussian_kernel
from .io import destroy_all_windows, imread, imshow, imwrite, waitkey
from .transform import (
    INTER_AREA,
    INTER_AUTO,
    INTER_B_SPLINE,
    INTER_CATMULL_ROM,
    INTER_CUBIC,
    INTER_LANCZOS2,
    INTER_LANCZOS3,
    INTER_LANCZOS4,
    INTER_LINEAR,
    INTER_MITCHELL,
    INTER_NEAREST,
    _resize,
    affine_transform,
    create_erode_kernel,
    crop_from_kps,
    erode,
    get_inverse_matrix,
    resize,
)
from .upscale import (
    OnnxUpscaler,
    TorchUpscaler,
    TrtUpscaler,
    add_padding,
    batch_to_tile,
    check_onnx_model,
    check_torch_model,
    create_gaussian_weights,
    merge_tiles,
    onnx_to_trt,
    onnx_to_trt_dynamic_shape,
    onnx_to_trt_fixed_shape,
    tile_image,
    to_batch,
    torch_to_onnx,
)
from .utils import to_blob, to_cupy, to_dtype, to_float16, to_float32, to_float64, to_numpy, to_tensor, to_uint8, to_uint16

get_device_id = cp.cuda.device.get_device_id
get_device_count = cp.cuda.runtime.getDeviceCount
Device = cp.cuda.Device

modules = []
color_modules = [
    aces2065_1_to_acescct,
    aces2065_1_to_acescg,
    aces2065_1_to_rec709,
    acescct_to_aces2065_1,
    acescg_to_aces2065_1,
    rec709_to_aces2065_1,
    apply_lut,
    apply_lut_cp,
    bgr_to_rgb,
    rgb_to_bgr,
    bgr_to_grayscale,
    rgb_to_grayscale,
    bgr_to_hsv,
    hsv_to_bgr,
    hsv_to_rgb,
    rgb_to_hsv,
    bgr_to_ycbcr,
    rgb_to_ycbcr,
    ndi_uyvy422_to_ycbcr444,
    ndi_uyvy422_to_ycbcr444_cp,
    uyvy422_to_ycbcr444,
    uyvy422_to_ycbcr444_cp,
    read_lut,
    ycbcr_full_to_legal,
    ycbcr_legal_to_full,
    ycbcr_to_bgr,
    ycbcr_to_grayscale,
    ycbcr_to_rgb,
    yuv420p_to_ycbcr444,
    yuv420p_to_ycbcr444_cp,
    yuv422p10le_to_ycbcr444,
    yuv422p10le_to_ycbcr444_cp,
]

draw_modules = [
    create_rounded_mask,
    circle,
    rectangle,
]
face_modules = [
    GFPGAN,
    FaceDetection,
    FaceEmbedding,
    FaceSwap,
    PasteBack,
    PxFace,
    TrtFaceDetection,
    TrtFaceEmbedding,
    TrtFaceSwap,
    paste_back,
]
filter_modules = [
    GaussianBlur,
    gaussian_blur,
    get_gaussian_kernel,
]
io_modules = [
    destroy_all_windows,
    imread,
    imshow,
    imwrite,
    waitkey,
]
transform_modules = [
    _resize,
    affine_transform,
    create_erode_kernel,
    crop_from_kps,
    erode,
    get_inverse_matrix,
    resize,
]
upscale_modules = [
    OnnxUpscaler,
    TorchUpscaler,
    TrtUpscaler,
    add_padding,
    batch_to_tile,
    check_onnx_model,
    check_torch_model,
    create_gaussian_weights,
    merge_tiles,
    onnx_to_trt,
    onnx_to_trt_dynamic_shape,
    onnx_to_trt_fixed_shape,
    tile_image,
    to_batch,
    torch_to_onnx,
]
utils_modules = [
    to_blob,
    to_cupy,
    to_numpy,
    to_tensor,
    to_dtype,
    to_float16,
    to_float32,
    to_float64,
    to_uint8,
    to_uint16,
]
modules.extend(color_modules)
modules.extend(draw_modules)
modules.extend(face_modules)
modules.extend(filter_modules)
modules.extend(io_modules)
modules.extend(transform_modules)
modules.extend(upscale_modules)
modules.extend(utils_modules)

MODULE_MAPPINGS = {}
for module in modules:
    if isinstance(module, int):
        continue

    module_name = module.__name__
    if hasattr(module, "__all__"):
        for name in module.__all__:
            MODULE_MAPPINGS[name] = getattr(module, name)
    else:
        MODULE_MAPPINGS[module_name] = module


__all__ = [
    "MODULE_MAPPINGS",
    "get_device_id",
    "get_device_count",
    "Device",
    "INTER_AREA",
    "INTER_AUTO",
    "INTER_B_SPLINE",
    "INTER_CATMULL_ROM",
    "INTER_CUBIC",
    "INTER_LANCZOS2",
    "INTER_LANCZOS3",
    "INTER_LANCZOS4",
    "INTER_LINEAR",
    "INTER_MITCHELL",
    "INTER_NEAREST",
]
