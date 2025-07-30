import copy
import math

import PIL.Image
import cv2
import numpy as np
from KUtils.Typing import *
from functools import wraps
from skimage.draw import polygon

from ._common import *
class ImageVisualizer:
    def open_blank(self, resolution=(256, 256)):
        self._buffer = np.full((*resolution, 3), 122, dtype=np.uint8)

    def open(self, path: str) -> Self:
        self._buffer = np.array(PIL.Image.open(path), dtype=np.uint8)
        return self

    def load_tensor(self, tensor: 'torch.Tensor'):
        arr = np.asarray(tensor)
        arr = imt.reshape2img(arr)
        self.load_numpy(arr)

    def load_numpy(self, array: np.ndarray)->Self:
        factor = 1
        if array.max() <= 1:
            factor = 255

        self._buffer = np.copy(array * factor).astype(np.uint8)
        return self

    def __init__(self, img: np.ndarray = None):
        if img is not None:
            self.load_numpy(img)

    def clear(self):
        self._buffer = None

    def pop(self)->np.ndarray:
        temp = self._buffer
        self._buffer = None
        return temp

    def peek(self, scale=1, wname='yeet')->None:
        imshow(self._buffer, scale=scale, wname=wname)

    def see(self, scale=1)->np.ndarray:
        self.peek(scale=scale)
        return self.pop()

    def normalize(self):
        if self._buffer.max() > 1:
            self._buffer /= 255.0

    def start(self, image: np.ndarray)->None:
        self._buffer = copy.deepcopy(image)

    def overlay(self, mask: np.ndarray, alpha: float = 0.5):
        # mask = (mask * 255 * alpha).astype(int)
        # mask = np.repeat(mask[..., np.newaxis], 3, axis=-1)

        self._buffer[mask > 0] = (mask[mask > 0] * alpha).astype(np.uint8)

    def resize(self, shape: Tuple[int, int]):
        h, w = shape
        self._buffer = cv2.resize(self._buffer, (w, h))

    def add_bbox_named(self, bbox: np.ndarray, tag: str, **kwargs)->None:
        x0y0 = bbox[:2]
        x1y1 = bbox[2:4]
        self._buffer = add_box(self._buffer, x0y0, x1y1, **kwargs)
        self._buffer = add_texts(self._buffer, [x0y0] , [tag])

    def add_circles(self, points: np.ndarray, **kwargs)->None:
        points = points.reshape([-1, 2])
        self._buffer = add_points(self._buffer, points, **kwargs)

    def add_boxes(self, bboxes: np.ndarray, color: Tuple[int, ...]=(0, 255, 0), normalized=True, names=None)->None:
        bboxes = bboxes.copy().reshape(-1, 4)
        shape = self._buffer.shape
        if bboxes.max() <= 1 or normalized:
            hwhw = np.array([*shape[:2], *shape[:2]])[::-1]
            bboxes *= hwhw

        bboxes = bboxes.reshape([-1, 4]).astype(int)
        for i in range(bboxes.shape[0]):
            box = bboxes[i]
            x0y0 = box[:2]
            x1y1 = box[2:4]
            if names is None:
                self._buffer = add_box(self._buffer, x0y0, x1y1, color=color)
            else:
                assert len(names) == len(bboxes)
                self.add_bbox_named(box, names[i], color=color)
        # self._buffer = add_boxes_xyxy(self._buffer, bboxes)

    def save(self, path: str)->None:
        normed = cv2norm(self._buffer)
        plt.imsave(path, normed)

    def add_contour(self, vertices: np.ndarray, normalized=True, **kwargs)->None:
        if normalized:
            vertices *= self._buffer.shape[:2][::-1]
        vertices = vertices.astype(int)
        self._buffer = add_polyline(self._buffer, vertices, **kwargs)

    def add_contours(self, vertices_list: List[np.ndarray], normalized=True, **kwargs)->None:
        for vertices in vertices_list:
            self.add_contour(vertices, normalized, **kwargs)

    def add_mask(self, mask: np.ndarray)->None:
        if len(mask.shape) == 2:
            mask = np.expand_dims(mask, axis=-1)

        mask *= 255

        assert len(mask.shape) == 3

        if mask.shape[-1] == 1:
            mask = np.repeat(mask, 3, axis=-1)

        self.overlay(mask)
    
    def add_masks(self, masks: np.ndarray)->None:
        for mask in masks:
            self.add_mask(mask)

    def add_texts(self, texts: List[str], poss: np.ndarray, **kwargs)->None:
        self._buffer = add_texts(self._buffer, poss=poss, texts=texts, **kwargs)

    def add_patch(self, patch: np.ndarray, pos: np.ndarray)->None:
        pos = np.array(pos, dtype=int)[::-1]
        # self.add_circles(pos)
        im_hw = np.array(self._buffer.shape[:2])#[::-1]  # Height and width of the image
        hw = np.array(patch.shape[:2]) # Height and width of the patch
        # pos[1] = im_hw[1] - pos[1]
        # Compute the top-left and bottom-right corners
        diff = hw / 2
        tl = pos - np.floor(diff).astype(int)
        br = pos + np.ceil(diff).astype(int)

        patch_tl = np.array([0, 0])
        patch_br = np.array(patch.shape[:2])

        # print('patch position', pos)
        # print('tl and br', tl, br)
        # print('patch tl and br', patch_tl, patch_br)
        # Clip the top-left and bottom-right coordinates to the image dimensions
        tl = np.clip(tl, 0, im_hw)
        br = np.clip(br, 0, im_hw)

        # Calculate the region in the patch to use
        patch_tl = np.clip(-tl, 0, hw)
        patch_br = hw - np.clip(br - im_hw, 0, hw)

        # Apply the patch
        self._buffer[tl[0]:br[0], tl[1]:br[1], :] = patch[patch_tl[0]:patch_br[0], patch_tl[1]:patch_br[1], :]
        # self._buffer[tl[1]:br[1], tl[0]:br[0], :] = patch.transpose()

class SegmentationVis(ImageVisualizer):
    def add_contour(self, vertices: np.ndarray, **kwargs):
        self._buffer = add_polyline(self._buffer, vertices, **kwargs)

    def add_mask(self, mask: np.ndarray):
        if len(mask.shape) == 2:
            mask = np.expand_dims(mask, axis=-1)

        mask *= 255

        assert len(mask.shape) == 3

        if mask.shape[-1] == 1:
            mask = np.repeat(mask, 3, axis=-1)

        self.overlay(mask)


