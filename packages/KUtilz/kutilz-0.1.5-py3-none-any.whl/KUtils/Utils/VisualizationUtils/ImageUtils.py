import numpy as np
from KUtils.Typing import *


def imshow(
        img: Union[Path, str, np.ndarray, 'torch.Tensor'],
        title: str = 'yeet',
        backend: Literal['cv2', 'PIL'] = 'cv2'
) -> None:
    """
    Display an image from a file path, numpy array, or PyTorch tensor.

    Args:
        img: Input image (file path, numpy array, or PyTorch tensor).
        title: Window title for display.
        backend: Library to use for displaying the image ('cv2' or 'PIL').

    Raises:
        ValueError: For invalid tensor dimensions.
        TypeError: For unsupported input types.
    """
    is_rgb = False
    img_np = None

    if isinstance(img, (Path, str)):
        # Load image using PIL (ensures RGB format)
        from PIL import Image
        img_pil = Image.open(str(img))
        img_np = np.array(img_pil)
        is_rgb = True
    elif isinstance(img, np.ndarray):
        img_np = img.copy()
        is_rgb = True
    elif isinstance(img, torch.Tensor):
        # Handle PyTorch tensor
        if img.dim() == 4:
            if img.size(0) != 1:
                raise ValueError("4D tensors must have batch size 1")
            img = img.squeeze(0)
        if img.dim() not in (2, 3):
            raise ValueError(f"Invalid tensor dimensions: {img.dim()}D")

        img = img.cpu().detach()
        img_np = img.numpy()

        # Handle channel order (C, H, W) -> (H, W, C)
        if img_np.ndim == 3 and img_np.shape[0] in (1, 3):
            img_np = np.transpose(img_np, (1, 2, 0))

        # Handle float tensors (assume 0-1 or 0-255 range)
        if np.issubdtype(img_np.dtype, np.floating):
            img_np = np.clip(img_np, 0, 1) * 255
        img_np = img_np.astype(np.uint8)
        is_rgb = True
    else:
        raise TypeError(f"Unsupported image type: {type(img)}")

    # Convert to BGR for OpenCV if needed
    if backend == 'cv2' and is_rgb and img_np.ndim == 3 and img_np.shape[-1] == 3:
        import cv2
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Squeeze grayscale channel dimension
    if img_np.ndim == 3 and img_np.shape[-1] == 1:
        img_np = img_np.squeeze(-1)

    # Display with chosen backend
    if backend == 'cv2':
        import cv2
        cv2.imshow(title, img_np)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        from PIL import Image
        mode = 'L' if img_np.ndim == 2 else 'RGB'
        Image.fromarray(img_np, mode=mode).show(title=title)