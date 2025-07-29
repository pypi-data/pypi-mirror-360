"""Matplotlib colormap utilities.

This module provides functions to retrieve and register colormaps in a format suitable for use with Matplotlib.
It can convert colormap arrays from various sources into Matplotlib Colormap objects and register them
with the matplotlib.colormaps registry.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np

from colormap_tool._cmps import CMPSPACE

if TYPE_CHECKING:
    from matplotlib.colors import Colormap

_cached_colormaps: dict[str, dict[str, Colormap]] = defaultdict(dict)

_is_registered = False

__all__ = ["get_mpl_colormaps", "register_all_cmps2mpl", "uint8_rgb_arr2mpl_cmp"]


def register_all_cmps2mpl() -> None:
    """Register all available colormaps with the matplotlib.colormaps registry.

    This function iterates through all namespaces and colormap names in CMPSPACE
    and registers each colormap with matplotlib. After calling this function,
    all colormaps can be accessed directly through matplotlib.colormaps.

    Examples
    --------
    >>> register_all_cmps2mpl()
    >>> import matplotlib.pyplot as plt
    >>> plt.imshow(data, cmap="cv.VIRIDIS")

    """
    try:
        import matplotlib as mpl
    except ImportError as err:
        raise ImportError("Missing optional dependency: matplotlib", name="matplotlib") from err
    global _is_registered
    if _is_registered:
        return
    for namespace in CMPSPACE:
        if namespace == "mpl":
            continue
        for name in CMPSPACE[namespace]:
            cmp = get_mpl_colormaps(name, namespace)
            mpl.colormaps.register(cmp)
    _is_registered = True


def get_mpl_colormaps(name: str, namespace: str | None = None) -> Colormap:
    """Get a colormap in Matplotlib format.

    Parameters
    ----------
    name : str
        The name of the colormap. If namespace is None, this should be in the format
        "namespace.name" (e.g., "cv.VIRIDIS", "mpl.viridis").
    namespace : Optional[str], optional
        The namespace of the colormap ("cv", "mpl"). If provided, the name
        parameter should not include the namespace prefix.

    Returns
    -------
    matplotlib.colors.Colormap
        A Matplotlib Colormap object that can be used with matplotlib plotting functions.
        For matplotlib colormaps (namespace="mpl"), returns the built-in colormap.
        For other colormaps, converts the numpy array to a Matplotlib ListedColormap.

    Raises
    ------
    AssertionError
        If the namespace is not recognized or the colormap name is not found in the namespace.

    Examples
    --------
    >>> # Get a matplotlib built-in colormap
    >>> cmap = get_mpl_colormaps("viridis", "mpl")
    >>> # Or equivalently
    >>> cmap = get_mpl_colormaps("mpl.viridis")
    >>> plt.imshow(data, cmap=cmap)

    >>> # Get an OpenCV colormap for use with matplotlib
    >>> cmap = get_mpl_colormaps("VIRIDIS", "cv")
    >>> # Or equivalently
    >>> cmap = get_mpl_colormaps("cv.VIRIDIS")
    >>> plt.imshow(data, cmap=cmap)

    """
    try:
        import matplotlib as mpl
    except ImportError as err:
        raise ImportError("Missing optional dependency: matplotlib", name="matplotlib") from err
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

    if namespace == "mpl":
        return mpl.colormaps[name]
    else:
        if name not in _cached_colormaps[namespace]:
            _cached_colormaps[namespace][name] = uint8_rgb_arr2mpl_cmp(
                CMPSPACE[namespace][name],
                f"{namespace}.{name}",
                alpha=1.0,
                mode="listed",
            )
        return _cached_colormaps[namespace][name]


def uint8_rgb_arr2mpl_cmp(
    arr: np.ndarray,
    name: str,
    alpha: float = 1.0,
    mode: Literal["listed", "linear"] = "listed",
) -> Colormap:
    """Convert a uint8 RGB array to a Matplotlib Colormap object.

    Parameters
    ----------
    arr : numpy.ndarray
        A numpy array of RGB values with shape (N, 3) or (N, 1, 3) and dtype uint8.
        Values should be in the range [0, 255].
    name : str
        The name to give to the colormap.
    alpha : float, optional
        The alpha (opacity) value for the colormap, by default 1.0 (fully opaque).
    mode : {"listed", "linear"}, optional
        The type of colormap to create:
        - "listed": Creates a ListedColormap (discrete colors)
        - "linear": Creates a LinearSegmentedColormap (interpolated colors)
        Default is "listed".

    Returns
    -------
    matplotlib.colors.Colormap
        A Matplotlib Colormap object (either ListedColormap or LinearSegmentedColormap
        depending on the mode parameter).

    Raises
    ------
    AssertionError
        If the input array has an invalid shape or dtype.
    ValueError
        If the mode parameter is not "listed" or "linear".

    Notes
    -----
    The function converts the uint8 values [0-255] to float values [0-1] required by Matplotlib.

    """
    try:
        from matplotlib.colors import LinearSegmentedColormap, ListedColormap
    except ImportError as err:
        raise ImportError("Missing optional dependency: matplotlib", name="matplotlib") from err
    if arr.ndim == 2 and arr.shape[1] != 3:
        raise ValueError(f"The shape of the input array {arr.shape} is not (N, 3).")
    if arr.ndim == 3:
        if arr.shape[1] != 1:
            raise ValueError(f"The shape of the input array {arr.shape} is not (N, 1, 3).")
        if arr.shape[2] != 3:
            raise ValueError(f"The shape of the input array {arr.shape} is not (N, 1, 3).")
        arr = arr.squeeze(1)

    if arr.dtype != np.uint8:
        raise ValueError(f"The dtype of the input array {arr.dtype} is not uint8.")

    # convert [0-255] uint8 to [0-1] float
    arr = arr.astype(np.float64) / 255.0

    alpha = np.full((arr.shape[0], 1), alpha)

    arr = np.concatenate((arr, alpha), axis=1)

    if mode == "listed":
        return ListedColormap(arr, name=name)
    elif mode == "linear":
        return LinearSegmentedColormap.from_list(name, arr)
    else:
        raise ValueError("mode must be 'listed' or 'linear'")
