"""Colormap storage and loading module.

This module loads colormap data from pickle files stored in the resources directory.
Each colormap is stored as a numpy array with shape (256, 1, 3) and dtype uint8.
The module provides access to colormaps from different sources (matplotlib, OpenCV).

The colormaps are loaded at import time and stored in dictionaries for easy access.
"""

from __future__ import annotations

import importlib.resources
import pickle

import numpy as np

RESOURCES_DIR = importlib.resources.files("colormap_tool").joinpath("resources")

with (RESOURCES_DIR / "mpl_colormaps.pickle").open("rb") as f:
    MPL_COLORMAPS: dict[str, np.ndarray] = pickle.load(f)


with (RESOURCES_DIR / "cv_colormaps.pickle").open("rb") as f:
    CV_COLORMAPS: dict[str, np.ndarray] = pickle.load(f)


CMPSPACE = {
    "cv": CV_COLORMAPS,
    "mpl": MPL_COLORMAPS,
}


def resample_lut(lut: np.ndarray, n: int) -> np.ndarray:
    """Resample a LUT to a new length.

    Accepts (m, 3) or (m, 1, 3) uint8 arrays. Returns the same format with length n.

    Parameters
    ----------
    lut : np.ndarray
        Input LUT, shape (m, 3) or (m, 1, 3), dtype uint8.
    n : int
        Target length.

    Returns
    -------
    np.ndarray
        Resampled LUT, same format as input, length n.

    Raises
    ------
    TypeError, ValueError
        If input is not a valid LUT.

    Examples
    --------
    >>> lut = np.array([[0, 0, 0], [255, 255, 255]], dtype=np.uint8)
    >>> resample_lut(lut, 5).shape
    (5, 3)

    """
    msg = "The shape of the lut must be (n, 3) or (n, 1, 3)."

    if lut.ndim == 2:
        if lut.shape[1] != 3:
            raise ValueError(msg)
        lut2d = lut
        out_shape = (n, 3)
    elif lut.ndim == 3:
        if lut.shape[1] != 1 or lut.shape[2] != 3:
            raise ValueError(msg)
        lut2d = lut.reshape(-1, 3)
        out_shape = (n, 1, 3)
    else:
        raise ValueError(msg)

    m = lut2d.shape[0]
    if n == m:
        return lut.copy() if lut.shape[0] == n else lut2d.reshape(out_shape)

    x_old = np.linspace(0, 1, m)
    x_new = np.linspace(0, 1, n)
    resampled = np.empty((n, 3), dtype=np.float32)
    for c in range(3):
        resampled[:, c] = np.interp(x_new, x_old, lut2d[:, c])
    resampled = np.clip(resampled, 0, 255).astype(np.uint8)
    return resampled.reshape(out_shape)


def get_colormaps(name: str, namespace: str | None = None, n: int | None = None) -> np.ndarray:
    """Return a colormap as an RGB LUT array.

    Returns a (n, 3) uint8 array in RGB order, resampled to length n if specified.
    Useful for custom visualization, further conversion, or as a base for other formats.

    Parameters
    ----------
    name : str
        Colormap name. If namespace is None, use "namespace.name" format.
    namespace : str, optional
        "cv" for OpenCV, "mpl" for Matplotlib.
    n : int, optional
        Number of LUT entries. If None, defaults to 256.

    Returns
    -------
    np.ndarray
        (n, 3) uint8 RGB LUT.

    Raises
    ------
    ValueError
        If the colormap or namespace is not found.

    Examples
    --------
    >>> lut = get_colormaps("mpl.viridis", n=128)
    >>> plt.imshow(data, cmap=colormap_tools.uint8_rgb_arr2mpl_cmp(lut))

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

    # Get the original LUT
    lut = CMPSPACE[namespace][name]

    # Reshape to (256, 3)
    lut = lut.reshape(-1, 3)

    # Resample if requested
    if n is not None and n != lut.shape[0]:
        lut = resample_lut(lut, n)

    return lut
