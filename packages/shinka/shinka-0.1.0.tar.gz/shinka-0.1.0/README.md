# SHINKO Upscaler

This repository provides a Python API for high-quality image upscaling using a specialized, genetically-evolved algorithm. The upscaler is designed for both grayscale and color images, and can be used as a drop-in replacement for traditional interpolation-based upscaling methods.

## Features

- Upscales images by a specified factor (e.g., 2x, 4x)
- Supports input as file path, PIL Image, or NumPy array
- Outputs as PIL Image or NumPy array
- Optionally saves the upscaled image to disk

## How to Use

### Installation

Install the required dependencies:

```bash
pip install numpy pillow scikit-image scipy
```

### Basic Usage

```python
from evolved_upscaler import evolved_upscale

# Upscale an image from file and save the result
result = evolved_upscale("input.jpg", scale=2, save_path="upscaled.png")

# Upscale a NumPy array and get a PIL Image
import numpy as np
from PIL import Image
arr = np.array(Image.open("input.jpg"))
result = evolved_upscale(arr, scale=2, output_type="PIL")

# Upscale and get a NumPy array
result = evolved_upscale("input.jpg", scale=2, output_type="np")
```

### Command-Line Example

A minimal test script is provided:

```python
# test_evolved_upscaler.py
from evolved_upscaler import evolved_upscale

evolved_upscale("DSC00183.jpeg", scale=4, save_path="test_evolved_upscaled.png")
print("Saved test_evolved_upscaled.png")
```

## How the Algorithm Was Created

The upscaling algorithm was developed using a genetic optimization process. A population of image processing pipelines was evolved over multiple generations to maximize perceptual quality (measured by SSIM and sharpness) on a diverse set of images. The best-performing pipeline was selected and implemented in `evolved_upscaler.py` for efficient, non-ML upscaling.

## License

This project is provided as-is for research and educational purposes.
