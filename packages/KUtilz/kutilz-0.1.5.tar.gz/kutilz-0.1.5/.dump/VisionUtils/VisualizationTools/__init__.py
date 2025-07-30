from ._common import *
from .ImageVisualizer import *


class KeyPointsVis:
    @classmethod
    def gt_v_pred(cls,
                  img: np.ndarray,
                  gt: np.ndarray,
                  pred: np.ndarray,
                  config = 'default',
                  show = False,
                  threshold=None,
                  radius=10,
                  names:List[str]=None)->np.ndarray:
        if config == 'default':
            gt_to_draw = gt
            pred_to_draw = pred
            names_to_draw = names
        elif config == 'above_threshold':
            assert threshold is not None, 'You must provide a threshold'
            dists = mgu.pnts_dists(pred, gt)
            to_draw = dists > threshold

            gt_to_draw = gt[to_draw]
            pred_to_draw = pred[to_draw]
            names_to_draw = names if names is None else np.array(names, dtype=str)[to_draw].tolist()

            bad_count = np.count_nonzero(to_draw)

        else: raise NotImplementedError()

        img = add_points(img, gt_to_draw, ct.Color.Green, radius=radius)
        img = add_points(img, pred_to_draw, ct.Color.Red, radius=radius)
        img = draw_lines(img, gt_to_draw, pred_to_draw, ct.Color.Green, thickness=2)

        text_offset = np.array([-10, -10])
        img = add_texts(img, gt_to_draw + text_offset, names_to_draw, color=ct.Color.Blue, fontScale=3, thickness=2)


        if show: imshow(img)
        return img

