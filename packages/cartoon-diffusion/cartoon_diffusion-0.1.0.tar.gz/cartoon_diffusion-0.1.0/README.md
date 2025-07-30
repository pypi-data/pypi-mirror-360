# Cartoon Diffusion

AI-powered image to cartoon conversion using diffusion models.

## Installation

```bash
pip install cartoon-diffusion
```

## Usage

```python
from cartoon_diffusion import CartoonifyDiffusionPipeline

# Load the pipeline
pipeline = CartoonifyDiffusionPipeline.from_pretrained("wizcodes12/image_to_cartoonify")

# Convert image to cartoon
cartoon = pipeline("path/to/selfie.jpg")
cartoon.save("cartoon_output.png")

# Or use with PIL Image
from PIL import Image
image = Image.open("selfie.jpg")
cartoon = pipeline(image)
cartoon.save("cartoon_output.png")
```

## Requirements

- Python 3.8+
- PyTorch
- CUDA (optional, for GPU acceleration)

## Model

This package uses the pre-trained model from `wizcodes12/image_to_cartoonify` on Hugging Face.

## License

MIT License