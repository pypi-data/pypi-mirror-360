import seaborn as sns
import numpy as np
import cv2 as cv
from KUtils.Typing import *

class ocv:
    Red = (255, 0, 0)
    Green = (0, 255, 0)
    Blue = (0, 0, 255)

def discrete(num_colors: int, name: str = 'deep', format: Literal['ocv', 'rgb'] = 'ocv') -> List[Tuple[int, int, int]]:
    pal = sns.color_palette(name, num_colors)

    if format == 'ocv':
        return [
            tuple(int(c * 255) for c in reversed(color)) for color in pal
        ]
    elif format == 'rgb':
        return [
            tuple(color) for color in pal
        ]
    else:
        raise NotImplementedError()