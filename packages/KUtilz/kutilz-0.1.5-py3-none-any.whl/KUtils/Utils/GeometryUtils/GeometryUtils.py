import numpy as np
import KUtils.Utils.ListUtils as liu
import cv2 as cv


def pnts_dists(pnts0: np.ndarray, pnts1: np.ndarray)->np.ndarray:
    diff = pnts1 - pnts0
    dists = np.linalg.norm(diff, axis=-1)
    return dists

def mask2polyon(mask: np.ndarray)->np.ndarray:
    contours, _ = cv.findContours(mask.astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    polygons = []

    for obj in contours:
        coords = []

        for point in obj:
            coords.append([int(point[0][0]), int(point[0][1])])

        polygons.append(coords)

    longest = liu.lensort(polygons)[0]
    return np.asarray(longest)

def pnts2bbox(pnts: np.ndarray)->np.ndarray:
    topleft = [pnts.min(axis=0), pnts.min(axis=1)]
    botright = [pnts.max(axis=0), pnts.max(axis=1)]
    return np.array([topleft, botright], dtype=pnts.dtype)