from typing import List, Optional, Union

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from skimage.filters import sobel
from skimage.transform import resize as sk_resize


def _edge_sharpen(
    image: np.ndarray, sigma: float, amount: float, thr: float
) -> np.ndarray:
    detail: np.ndarray = image - gaussian_filter(image, sigma)
    mask: np.ndarray = sobel(image) > thr
    return np.clip(image + amount * detail * mask, 0, 1)

def _normalize_and_resize(arr: np.ndarray, scale: int) -> np.ndarray:
    arr = arr.astype(np.float32) / 255.0 if arr.max() > 1.0 else arr.astype(np.float32)
    new_shape: tuple[int, int] = (arr.shape[0] * scale, arr.shape[1] * scale)
    arr = np.asarray(
        sk_resize(arr, new_shape, order=2, mode="symmetric", anti_aliasing=True)
    )
    return arr

def _to_pil_and_save(arr: np.ndarray, save_path: Optional[str] = None) -> Image.Image:
    arr255: np.ndarray = (arr * 255).clip(0, 255).astype("uint8")
    if arr255.ndim == 2:
        out_img: Image.Image = Image.fromarray(arr255, mode="L")
    else:
        mode: Optional[str] = (
            "RGB" if arr255.shape[2] == 3 else "RGBA" if arr255.shape[2] == 4 else None
        )
        if mode is None:
            raise ValueError("Unsupported channel count for PIL output.")
        out_img = Image.fromarray(arr255, mode=mode)
    if save_path:
        out_img.save(save_path)
    return out_img

def upscale(
    img: Union[str, Image.Image, np.ndarray],
    scale: int = 2,
    output_type: str = "PIL",
    save_path: Optional[str] = None,
) -> Union[Image.Image, np.ndarray]:
    arr: np.ndarray
    if isinstance(img, str):
        arr = np.asarray(Image.open(img))
    elif isinstance(img, Image.Image):
        arr = np.asarray(img)
    elif isinstance(img, np.ndarray):
        arr = img
    else:
        raise TypeError(
            f"Input must be a file path (str), PIL.Image, or numpy.ndarray, not {type(img).__name__}."
        )
    if isinstance(arr, np.ndarray) and arr.size == 0:
        raise ValueError("Input array is empty.")
    if not hasattr(arr, "ndim"):
        raise TypeError("Input must be an image-like object with 'ndim' attribute.")
    if arr.ndim == 2:
        arr = _normalize_and_resize(arr, scale)
        out_arr: np.ndarray = _edge_sharpen(arr, sigma=0.676, amount=1.571, thr=0.0113)
    elif arr.ndim == 3:
        out_channels: List[np.ndarray] = []
        for c in range(arr.shape[2]):
            chan: np.ndarray = arr[..., c]
            chan = _normalize_and_resize(chan, scale)
            chan = _edge_sharpen(chan, sigma=0.676, amount=1.571, thr=0.0113)
            out_channels.append(chan)
        out_arr: np.ndarray = np.stack(out_channels, axis=-1)
    else:
        raise ValueError(
            f"Unsupported image shape for upscaling: ndim={arr.ndim}, shape={arr.shape}."
        )
    if output_type == "PIL":
        return _to_pil_and_save(out_arr, save_path)
    elif output_type == "np":
        if save_path:
            _to_pil_and_save(out_arr, save_path)
        return out_arr
    else:
        raise ValueError("output_type must be 'PIL' or 'np'.") 