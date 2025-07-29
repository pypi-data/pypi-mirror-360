import cupy as cp

from ..filter.gaussian import gaussian_blur
from ..transform.resize import INTER_AUTO, resize
from .shape import circle, rectangle


def create_rounded_mask(
    dsize: tuple = (512, 512),
    mask_offsets: tuple = (0.1, 0.1, 0.1, 0.1),
    radius_ratio: float = 0.1,
    density: int = 1,
    blur_size: int = 0,
    sigma: float = 1.0,
) -> cp.ndarray:
    """
    Create a rounded rectangle mask with anti-aliasing and optional blurring.

    Args:
        size: Size of the mask (height and width)
        mask_offsets: (top, left, bottom, right) offset ratios
        radius_ratio: Corner roundness ratio
        density: Scale factor for anti-aliasing
        blur_size: Blur size ratio

    Returns:
        cupy.ndarray: Rounded rectangle mask with anti-aliasing and optional blurring.
    """
    # Scale up the image dimensions by the density factor
    h, w = dsize
    scaled_h, scaled_w = h * density, w * density

    # Create a black background of scaled size
    mask = cp.zeros((scaled_h, scaled_w, 3), dtype=cp.float32)

    # Convert radius ratio and offsets to pixels on the scaled image
    scaled_radius = int(radius_ratio * min(scaled_w, scaled_h))
    scaled_offsets_px = [
        int(scaled_h * mask_offsets[0]),
        int(scaled_w * mask_offsets[1]),
        int(scaled_h * mask_offsets[2]),
        int(scaled_w * mask_offsets[3]),
    ]

    # Calculate the rectangle coordinates with offsets on the scaled image
    top_left = (scaled_offsets_px[1], scaled_offsets_px[0])
    bottom_right = (scaled_w - scaled_offsets_px[3], scaled_h - scaled_offsets_px[2])

    # Draw four filled circles at the corners for the rounded effect
    circle_centers = [
        (top_left[0] + scaled_radius, top_left[1] + scaled_radius),
        (bottom_right[0] - scaled_radius, top_left[1] + scaled_radius),
        (top_left[0] + scaled_radius, bottom_right[1] - scaled_radius),
        (bottom_right[0] - scaled_radius, bottom_right[1] - scaled_radius),
    ]

    for center_x, center_y in circle_centers:
        circle(mask, center_x, center_y, scaled_radius)

    # Draw the filled rectangles to connect the circles
    # Vertical rectangle
    rectangle(mask, top_left[0], top_left[1] + scaled_radius, bottom_right[0], bottom_right[1] - scaled_radius)

    # Horizontal rectangle
    rectangle(mask, top_left[0] + scaled_radius, top_left[1], bottom_right[0] - scaled_radius, bottom_right[1])

    # Resize the mask back to the original image size using area interpolation
    if density != 1:
        anti_aliased_mask = resize(mask, (w, h), interpolation=INTER_AUTO)
    else:
        anti_aliased_mask = mask

    # Apply blur if requested
    if blur_size > 0:
        anti_aliased_mask = gaussian_blur(anti_aliased_mask, ksize=blur_size, sigma=sigma)

    result = anti_aliased_mask
    # result.dtype is cp.float32
    return result
