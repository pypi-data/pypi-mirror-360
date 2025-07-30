import copy

import cv2
import numpy as np
from KUtils.Typing import *
from functools import wraps
from skimage.draw import polygon
import matplotlib.pyplot as plt

def showable(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        show = kwargs.pop('show', False)
        image = func(cls, *args, **kwargs)
        if show:
            imshow(img=image)
        return image
    return wrapper

def cv2norm(img: np.ndarray)->np.ndarray:
    assert img.max() > 1
    return img.astype(float) / 255.0

def imshow(img: np.ndarray, scale=1, wname=None) -> None:
    if scale != 1:
        h, w = img.shape[:2]
        h *= scale
        w *= scale
        img = cv2.resize(img, [int(w * scale), int(h * scale)])

    # img = cv2norm(img)
    # plt.imshow(img)
    # plt.waitforbuttonpress()
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow(wname or 'yeet', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def add_points(img: np.ndarray, pnts: np.ndarray, color=(0, 255, 0), radius=5, thickness=-1, show=False) -> np.ndarray:

    pnts = pnts.astype(int)

    # Draw each point on the image
    for point in pnts:
        cv2.circle(img, tuple(point), radius, color, thickness)

    if show: imshow(img)


    return img

def add_box(img: np.ndarray, x0y0, x1y1, color=(0, 255, 0), thickness=1, show=False) -> np.ndarray:
    # Start coordinate, here (5, 5)
    # represents the top left corner of rectangle
    # start_point = box[0]
    #
    # # Ending coordinate, here (220, 220)
    # # represents the bottom right corner of rectangle
    # end_point = box[1]

    # Using cv2.rectangle() method
    # Draw a rectangle with blue line borders of thickness of 2 px
    # color = (int(item) for item in color)
    img = cv2.rectangle(img=img, pt1=x0y0, pt2=x1y1, color=color, thickness=thickness)
    # img = cv2.rectangle(img=img, pt1=(0, 0), pt2=(100, 100), color=(0, 255, 0), thickness=4)

    # Displaying the image
    if show: imshow(img)
    return img

def draw_lines(img: np.ndarray, pnts_x: np.ndarray, pnts_y: np.ndarray, color = (0, 255, 0), thickness =2)->np.ndarray:
    _pnts_x = pnts_x.astype(int)
    _pnts_y = pnts_y.astype(int)

    total = pnts_x.shape[0]

    for i in range(total):
        img = cv2.line(img, _pnts_x[i], _pnts_y[i], color, thickness)

    return img

def tensor2img(tensor: 'torch.Tensor')->np.ndarray:
    img = tensor.cpu().numpy()
    return np.transpose(img, (1, 2, 0))

def add_texts(img: np.ndarray, poss: List[np.ndarray], texts: List[str], font=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255, 0, 0), thickness=1)->np.ndarray:

    for i in range(len(texts)):
        pos = poss[i].astype(int)
        img = cv2.putText(img, texts[i], pos, fontFace=font, fontScale=fontScale, color=color, thickness=thickness, lineType=cv2.LINE_AA)

    return img

def add_polygon(img: np.ndarray, vertices: np.ndarray, fill=1)->np.ndarray:
    _vertices = vertices.astype(int)
    rr, cc = polygon(_vertices[:, 1], _vertices[:, 0], img.shape)
    img[rr, cc] = fill
    return img

def add_polyline(img: np.ndarray, vertices: np.ndarray, isClosed=True, color=(0, 255, 0), thickness=2)->np.ndarray:
    _vertices = vertices.astype(np.int32).reshape(-1, 2)
    _vertices = [_vertices]
    _img = np.copy(img)
    img = cv2.polylines(_img, _vertices, isClosed=isClosed, color=color, thickness=thickness)
    return img

def layer_img(bottom: np.ndarray, top: np.ndarray, ratio: float = 0.5)->np.ndarray:
    assert .0 <= ratio <= 1.0
    assert bottom.shape == top.shape

    layered = cv2.addWeighted(bottom.astype(float), 1 - ratio,
                              top.astype(float), ratio,
                              gamma=0)

    return layered.astype(bottom.dtype)

def concat_masks(masks: np.ndarray, merge=True)->np.ndarray:
    assert len(masks.shape) == 4
    return np.sum(masks, axis=0).squeeze()

def add_boxes_xyxy(image: np.ndarray, boxes: np.ndarray)->np.ndarray:
    boxes = boxes.reshape([-1, 2, 2]).astype(np.uint8)
    for box in boxes:
        image = add_box(image, box)
    return image