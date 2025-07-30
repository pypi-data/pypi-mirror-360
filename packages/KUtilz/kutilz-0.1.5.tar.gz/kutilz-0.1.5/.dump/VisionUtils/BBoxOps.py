import numpy as np

def scale(bbox: np.ndarray, factor: float)->np.ndarray:
    factor = factor - 1
    bbox = bbox.copy()
    hw = bbox[:2] - bbox[2:]
    bbox[2:] -= factor * hw
    bbox[:2] += factor * hw
    return bbox