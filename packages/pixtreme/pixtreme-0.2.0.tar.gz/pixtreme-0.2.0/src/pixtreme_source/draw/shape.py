import cupy as cp


def circle(image: cp.ndarray, center_x, center_y, radius, color=(1.0, 1.0, 1.0)) -> cp.ndarray:
    """
    Draw a circle on the image using CuPy.

    Args:
        image: cp.ndarray
            Target image array (H, W, C)
        center_x: int
            Pixel X coordinate of the circle center
        center_y: int
            Pixel Y coordinate of the circle center
        radius: int
            Circle radius
        color: tuple, optional
            Circle color (R, G, B), by default (1.0, 1.0, 1.0)
    """
    h, w = image.shape[:2]
    y_coords, x_coords = cp.mgrid[0:h, 0:w]
    circle_mask = ((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2) <= radius**2
    image[circle_mask] = color
    return image


def rectangle(image: cp.ndarray, top_left_x, top_left_y, bottom_right_x, bottom_right_y, color=(1.0, 1.0, 1.0)) -> cp.ndarray:
    """
    Draw a rectangle on the image using CuPy.

    Args:
        image: cp.ndarray
            Target image array (H, W, C)
        top_left_x: int
            Pixel X coordinate of the top-left corner
        top_left_y: int
            Pixel Y coordinate of the top-left corner
        bottom_right_x: int
            Pixel X coordinate of the bottom-right corner
        bottom_right_y: int
            Pixel Y coordinate of the bottom-right corner
        color: tuple, optional
            Rectangle color (R, G, B), by default (1.0, 1.0, 1.0)
    """
    h, w = image.shape[:2]
    y_coords, x_coords = cp.mgrid[0:h, 0:w]
    rect_mask = (x_coords >= top_left_x) & (x_coords < bottom_right_x) & (y_coords >= top_left_y) & (y_coords < bottom_right_y)
    image[rect_mask] = color
    return image
