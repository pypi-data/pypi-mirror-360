import numpy as np
from pathlib import Path
import KUtils.Utils.ListUtils as liu
import KUtils.Utils.FileUtils as fu
import cv2 as cv
from skimage.draw import polygon
from KUtils.Typing import *
from PIL import Image
import matplotlib.pyplot as plt

def imread(path: str)->np.ndarray:
    return fu.imread(path)

def imsave(img: np.ndarray, path: Union[Path, str])->None:
    plt.imsave(str(path), img)

def pnts_dists(pnts0: np.ndarray, pnts1: np.ndarray)->np.ndarray:
    diff = pnts1 - pnts0
    dists = np.linalg.norm(diff, axis=-1)
    return dists

def polygon2mask(img: np.ndarray, vertices: np.ndarray, fill=1)->np.ndarray:
    _vertices = vertices.astype(int)
    rr, cc = polygon(_vertices[:, 1], _vertices[:, 0], img.shape)
    img[rr, cc] = fill
    return img

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
    topleft = [min(pnts[:, 0]), min(pnts[:, 1])]
    botright = [max(pnts[:, 0]), max(pnts[:, 1])]
    return np.array([topleft, botright], dtype=pnts.dtype)

def polys2bbox(polys: List[np.ndarray])->np.ndarray:
    boxes = [pnts2bbox(poly) for poly in polys]
    return np.array(boxes)

def batched_pnts2bbox(pntss: List[np.ndarray])->np.ndarray:
    bs = len(pntss)
    boxes = np.zeros((bs, 2, 2))
    for i in range(bs):
        boxes[i] = pnts2bbox(pntss[i])

    return boxes

def reshape2torch(array: np.ndarray)->np.ndarray:
    return np.transpose(array, (2, 0, 1))

def reshape2img(array: np.ndarray)->np.ndarray:
    return np.transpose(array, (1, 2, 0))

def crop_path(img: np.ndarray, xyxy: np.ndarray, normalized=True)->np.ndarray:
    xyxy = xyxy.copy()
    xyxy = xyxy.reshape(2, 2)
    if normalized:
        xyxy *= img.shape[:2][::-1]
    xyxy = xyxy.astype(int).reshape([-1])
    patch = img[xyxy[1]: xyxy[3], xyxy[0]: xyxy[2]]
    return patch

def crop_patches(img: np.ndarray, xyxys: np.ndarray, normalized=True)->List[np.ndarray]:
    patches = []
    for xyxy in xyxys:
        patches.append(crop_path(img, xyxy, normalized))
    return patches

def tensor2img(img: 'torch.Tensor')->np.ndarray:
    # assert isinstance(img, 'torch.Tensor')

    return img.permute(1, 2, 0).detach().cpu().numpy()