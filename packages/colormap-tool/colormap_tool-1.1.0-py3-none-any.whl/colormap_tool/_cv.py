"""OpenCV colormap utilities.

This module provides functions to retrieve colormaps in a format suitable for use with OpenCV.
It can return both built-in OpenCV colormaps (as integer constants) and custom colormaps
from other sources (as numpy arrays).
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from colormap_tool._cmps import CMPSPACE

__all__ = ["get_cv_colormaps"]


def get_cv_colormaps(name: str, namespace: str | None = None) -> int | np.ndarray:
    """Return a colormap suitable for OpenCV's cv2.applyColorMap.

    Parameters
    ----------
    name : str
        Colormap name. If namespace is None, use "namespace.name" format (e.g., "cv.jet", "mpl.viridis").
    namespace : str, optional
        "cv" for OpenCV, "mpl" for Matplotlib. If provided, name should not include a dot.

    Returns
    -------
    int or np.ndarray
        OpenCV colormap constant or a (256, 1, 3) uint8 LUT in BGR order.

    Raises
    ------
    ValueError
        If the colormap or namespace is not found.

    Examples
    --------
    >>> lut = get_cv_colormaps("mpl.viridis")
    >>> img_color = cv2.applyColorMap(gray_img, lut)
    >>> lut2 = get_cv_colormaps("jet", "cv")
    >>> img_color2 = cv2.applyColorMap(gray_img, lut2)

    """
    if namespace is not None:
        if "." in name:
            raise ValueError(f"Namespace {namespace} is provided, so name {name} should not include a dot.")
    else:
        namespace, name = name.split(".")

    namespace = namespace.lower()
    name = name.lower()
    if namespace not in CMPSPACE:
        raise ValueError(f"Namespace {namespace} is not recognized.")
    if name not in CMPSPACE[namespace]:
        raise ValueError(f"Colormap {name} is not found in namespace {namespace}.")

    rgb_arr = CMPSPACE[namespace][name]
    bgr_arr = rgb_arr[:, :, ::-1]
    return bgr_arr


def apply_colormap_with_numpy(src: np.ndarray, cmp: np.ndarray, dst: np.ndarray | None = None) -> np.ndarray:
    """Apply a colormap to an image using numpy instead of OpenCV.

    Parameters
    ----------
    src : numpy.ndarray
        The image to apply the colormap to.
    cmp : numpy.ndarray
        The colormap to apply. Should have shape (256, 1, 3) and dtype uint8.
    dst : numpy.ndarray, optional
        The output array to store the result. If None, a new array will be created.

    Returns
    -------
    numpy.ndarray
        The output array with the colormap applied.

    """
    if dst is None:
        dst = np.zeros_like(src)
    else:
        if dst.shape != src.shape:
            raise ValueError(
                f"The shape of the output array {dst.shape} does not match the shape of the input array {src.shape}.",
            )

    if src.dtype != np.uint8:
        raise ValueError(f"The dtype of the input array {src.dtype} is not uint8.")
    if cmp.shape != (256, 1, 3):
        raise ValueError(f"The shape of the colormap array {cmp.shape} is not (256, 1, 3).")
    if cmp.dtype != np.uint8:
        raise ValueError(f"The dtype of the colormap array {cmp.dtype} is not uint8.")

    dst = cmp.copy().squeeze()
    dst = dst[src]

    return dst
