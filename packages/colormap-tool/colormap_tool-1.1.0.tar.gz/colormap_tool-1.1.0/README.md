# colormap-tool

[![Release](https://img.shields.io/github/v/release/MeridianInnovation/colormap-tool)](https://img.shields.io/github/v/release/MeridianInnovation/colormap-tool)
[![Commit activity](https://img.shields.io/github/commit-activity/m/MeridianInnovation/colormap-tool)](https://img.shields.io/github/commit-activity/m/MeridianInnovation/colormap-tool)
[![License](https://img.shields.io/github/license/MeridianInnovation/colormap-tool)](https://img.shields.io/github/license/MeridianInnovation/colormap-tool)
[![Python](https://img.shields.io/badge/python-%3E%3D3.9%2C%3C%3D3.13-blue)](https://img.shields.io/badge/python-%3E%3D3.9%2C%3C%3D3.13-blue)

A Colormap Tool package to convert cmps between cv and mpl.

- **Github repository**: <https://github.com/MeridianInnovation/colormap-tool/>
- **Documentation** <https://MeridianInnovation.github.io/colormap-tool/>

## Overview

This package can let users use cv's built-in colormap in matplotlib, or use matplotlib's colormap in cv.

## Features

- Convert colormaps between matplotlib and OpenCV formats
- Access colormaps from matplotlib and OpenCVs through a common interface
- Convert between numpy arrays, matplotlib Colormap objects, and OpenCV constants
- Register external colormaps with matplotlib

## Installation

To install the project, run the following command:

```bash
python -m pip install colormap-tool
```

## Usage

### 1. Basic Import

```python
import cv2
import matplotlib.pyplot as plt
import numpy as np
import colormap_tool
```

### 2. Core Recipes

This library provides simple, one-line solutions for common colormap conversion tasks.

#### Recipe 1: Use a Matplotlib Colormap in OpenCV

To apply a Matplotlib colormap (e.g., `viridis`) to an image using `cv2.applyColorMap`, use `get_cv_colormaps`.

This function automatically handles the conversion to the BGR format required by OpenCV.

```python
# Get the 'viridis' colormap in a format suitable for OpenCV
lut = colormap_tool.get_cv_colormaps("mpl.viridis")

# Apply it to a grayscale image
gray_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
colored_img = cv2.applyColorMap(gray_img, lut)

# Display the result
cv2.imshow("Matplotlib's Viridis in OpenCV", colored_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

#### Recipe 2: Use an OpenCV Colormap in Matplotlib

To use an OpenCV colormap (e.g., `jet`) in a Matplotlib plot, use `get_mpl_colormaps`.

This function returns a `matplotlib.colors.Colormap` object that `matplotlib` understands.

```python
# Get the OpenCV 'jet' colormap as a Matplotlib Colormap object
cmap = colormap_tool.get_mpl_colormaps("cv.jet")

# Use it in a plot
data = np.random.rand(20, 20)
plt.imshow(data, cmap=cmap)
plt.title("OpenCV's Jet in Matplotlib")
plt.colorbar()
plt.show()
```

#### Recipe 3: Get Raw Colormap Data (RGB)

If you need the raw RGB color data for a colormap, use `get_colormaps`. This is useful for custom processing, analysis, or creating custom visualizations.

You can also specify the number of entries (`n`) to resample the colormap.

```python
# Get the 'viridis' colormap as a 256-entry RGB array
rgb_lut = colormap_tool.get_colormaps("mpl.viridis", n=256)

# rgb_lut is a (256, 3) numpy array with dtype=uint8
print(rgb_lut.shape)
print(rgb_lut.dtype)
```

### 3. Advanced Usage

#### Registering All Colormaps with Matplotlib

For maximum convenience, you can register all available colormaps with Matplotlib at the start of your script. This allows you to use them by name in any Matplotlib function.

```python
# Register all colormaps
colormap_tool.register_all_cmps2mpl()

# Now, you can use OpenCV colormaps directly by name
data = np.random.rand(20, 20)
plt.imshow(data, cmap="cv.jet")
plt.title("Using a Registered OpenCV Colormap")
plt.show()
```

#### Custom LUT Resampling

The `resample_lut` function can resize any custom LUT to a desired length while preserving its format.

```python
# Create a simple 2-color LUT (black to white)
my_lut = np.array([[0, 0, 0], [255, 255, 255]], dtype=np.uint8)

# Resample it to 10 entries
resampled_lut = colormap_tool.resample_lut(my_lut, 10)
print(resampled_lut.shape)  # Output: (10, 3)
```

#### Converting a Custom RGB Array to a Matplotlib Colormap

If you have your own colormap data as an RGB array, you can convert it into a Matplotlib `Colormap` object.

```python
# Create a custom gradient from blue to yellow
custom_rgb = np.zeros((256, 3), dtype=np.uint8)
custom_rgb[:, 0] = np.linspace(0, 255, 256)      # R
custom_rgb[:, 1] = np.linspace(0, 255, 256)      # G
custom_rgb[:, 2] = np.linspace(255, 0, 256)      # B

# Convert it to a Matplotlib Colormap object
custom_cmap = colormap_tool.uint8_rgb_arr2mpl_cmp(custom_rgb, name="blue_yellow")

# Use it in a plot
plt.imshow(data, cmap=custom_cmap)
plt.title("Custom Blue-Yellow Colormap")
plt.show()
```

## License

This project is licensed under the MIT license license.

## Contributing

Please follow the [Contributing Guide](./CONTRIBUTING.md) to contribute to this project.

## Contact

For support or inquiries, please contact:

- Email: info@meridianinno.com
