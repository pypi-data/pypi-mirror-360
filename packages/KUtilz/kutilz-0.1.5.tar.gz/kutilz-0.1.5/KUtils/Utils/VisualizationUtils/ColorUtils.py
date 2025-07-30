import numpy as np
from KUtils.Typing import *


def parse_color(inputs: str | np.ndarray | tuple | list,
                format: Literal['rgb', 'rgba', 'bgr'] = 'rgba',
                normalized: bool = True) -> Tuple[float, ...] | Tuple[int, ...]:
    """
    Parse various color input formats into a tuple in the specified color space.

    Args:
        inputs: Color input in one of these formats:
            - str: Hex color (e.g., "#RRGGBB" or "#RRGGBBAA")
            - np.ndarray: Array of 3-4 values (RGB/RGBA)
            - tuple/list: Sequence of 3-4 values (RGB/RGBA)
        format: Output color format ('rgb', 'rgba', or 'bgr')
        normalized: If True, returns values in 0-1 range, otherwise 0-255

    Returns:
        Tuple of color values in the specified format and range

    Raises:
        ValueError: If input format is invalid or values are out of range
        TypeError: If input type is not supported
    """
    # First parse into RGBA format with values in 0-1 range
    if isinstance(inputs, str):
        # Handle hex color string
        if inputs.startswith('#'):
            hex_str = inputs[1:]
            if len(hex_str) == 3:  # Short hex (e.g., #RGB)
                hex_str = ''.join([c * 2 for c in hex_str])
            if len(hex_str) == 6:  # RGB
                hex_str += 'ff'  # Add alpha if missing
            if len(hex_str) != 8:
                raise ValueError(f"Invalid hex color format: {inputs}")

            try:
                r = int(hex_str[0:2], 16) / 255.0
                g = int(hex_str[2:4], 16) / 255.0
                b = int(hex_str[4:6], 16) / 255.0
                a = int(hex_str[6:8], 16) / 255.0
                rgba = (r, g, b, a)
            except ValueError:
                raise ValueError(f"Invalid hex color: {inputs}")
        else:
            from PIL.ImageColor import getrgb
            rgba = getrgb(color=inputs)
            if len(rgba) == 3:
                rgba = (*rgba, 255)
            # raise ValueError(f"Unsupported color string format: {inputs}")

    elif isinstance(inputs, (np.ndarray, tuple, list)):
        # Handle array-like inputs
        arr = np.asarray(inputs, dtype=np.float32)

        if arr.ndim != 1:
            raise ValueError("Color input must be 1-dimensional")

        if len(arr) == 3:  # RGB
            if normalized:
                rgba = (*arr, 1.0)
            else:
                rgba = (*arr, 255.0)
        elif len(arr) == 4:  # RGBA
            rgba = tuple(arr)
        else:
            raise ValueError("Color input must have 3 (RGB) or 4 (RGBA) components")

        # Validate range
        if normalized:
            if np.any(arr < 0) or np.any(arr > 1):
                raise ValueError("Normalized color values must be in range [0, 1]")
        else:
            if np.any(arr < 0) or np.any(arr > 255):
                raise ValueError("8-bit color values must be in range [0, 255]")
    else:
        raise TypeError(f"Unsupported color input type: {type(inputs)}")

    # Convert to desired format and range
    r, g, b, a = rgba

    if not normalized:
        # Scale to 0-255 range if needed
        if normalized_input := all(0 <= x <= 1 for x in (r, g, b, a)):
            r, g, b, a = (round(x * 255) for x in (r, g, b, a))
        elif not all(0 <= x <= 255 for x in (r, g, b, a)):
            raise ValueError("Color values must be either all in [0,1] or all in [0,255]")

    # Format conversion
    if format == 'rgb':
        result = (r, g, b)
    elif format == 'rgba':
        result = (r, g, b, a)
    elif format == 'bgr':
        result = (b, g, r)
    else:
        raise ValueError(f"Unsupported format: {format}")

    # Return as integers if not normalized
    if not normalized:
        result = tuple(int(round(x)) for x in result)

    return result