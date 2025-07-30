# SHINKA Upscaler

This repository provides a Python API for high-quality image upscaling using a specialized, genetically-evolved algorithm. The upscaler is designed for both grayscale and color images, and can be used as a drop-in replacement for traditional interpolation-based upscaling methods.

## Features

- Upscales images by a specified factor (e.g., 2x, 4x)
- Supports input as file path, PIL Image, or NumPy array
- Outputs as PIL Image or NumPy array
- Optionally saves the upscaled image to disk

## Benchmark Results

SHINKA demonstrates state-of-the-art perceptual quality on real-world images. In a benchmark on 1,000 images from the takara-ai/image_captions dataset, SHINKA achieved the highest SSIM (Structural Similarity Index) among common upscaling methods:

| Method   | SSIM   | PSNR (dB) |
| -------- | ------ | --------- |
| SHINKA   | 0.9459 | 35.32     |
| Lanczos  | 0.9432 | 36.07     |
| Bicubic  | 0.9376 | 35.54     |
| Bilinear | 0.9206 | 34.16     |
| Nearest  | 0.9145 | 32.01     |

## How to Use

### Installation

Install from PyPI:

```bash
pip install shinka
```

### Basic Usage

```python
from shinka import upscale

# Upscale an image from file and save the result
result = upscale("input.jpg", scale=2, save_path="upscaled.png")

# Upscale a NumPy array and get a PIL Image
import numpy as np
from PIL import Image
arr = np.array(Image.open("input.jpg"))
result = upscale(arr, scale=2, output_type="PIL")

# Upscale and get a NumPy array
result = upscale("input.jpg", scale=2, output_type="np")
```

### Command-Line Example

A minimal test script is provided:

```python
# test_shinka.py
from shinka import upscale

upscale("DSC00183.jpeg", scale=4, save_path="test_evolved_upscaled.png")
print("Saved test_evolved_upscaled.png")
```

## How the Algorithm Was Created

The upscaling algorithm was developed using a genetic optimization process. A population of image processing pipelines was evolved over multiple generations to maximize perceptual quality (measured by SSIM and sharpness) on a diverse set of images. The best-performing pipeline was selected and implemented in `shinka` for efficient, non-ML upscaling.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
