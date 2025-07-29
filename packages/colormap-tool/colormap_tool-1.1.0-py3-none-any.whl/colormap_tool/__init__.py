"""Colormap Tools - A library for working with colormaps across different visualization libraries.

This package provides utilities for loading, converting, and using colormaps from various sources
(matplotlib, OpenCV) in a consistent way. It allows using colormaps from one library in another,
for example using a matplotlib colormap in OpenCV or vice versa.

The package loads colormaps from pickle files that store them as numpy arrays with shape (256, 1, 3)
and dtype uint8. These colormaps can then be converted to the appropriate format for each visualization
library.

Main components:

  - _cmps.py: Loads and stores colormap data from pickle files, provides RGB format colormaps and resampling utilities
  - _cv.py: Provides colormaps in OpenCV format (BGR)
  - _mpl.py: Provides colormaps in Matplotlib format
"""

from colormap_tool._cmps import CMPSPACE, CV_COLORMAPS, MPL_COLORMAPS, get_colormaps, resample_lut
from colormap_tool._cv import apply_colormap_with_numpy, get_cv_colormaps
from colormap_tool._mpl import get_mpl_colormaps, register_all_cmps2mpl, uint8_rgb_arr2mpl_cmp

__all__ = [
    "CMPSPACE",
    "CV_COLORMAPS",
    "MPL_COLORMAPS",
    "apply_colormap_with_numpy",
    "get_colormaps",
    "get_cv_colormaps",
    "get_mpl_colormaps",
    "register_all_cmps2mpl",
    "resample_lut",
    "uint8_rgb_arr2mpl_cmp",
]
