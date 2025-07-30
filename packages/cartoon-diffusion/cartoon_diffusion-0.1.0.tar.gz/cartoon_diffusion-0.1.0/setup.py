from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cartoon-diffusion",
    version="0.1.0",
    author="wizcodes12",
    author_email="",
    description="AI-powered image to cartoon conversion using diffusion models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wizcodes12/cartoon-diffusion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "diffusers>=0.20.0",
        "transformers>=4.20.0",
        "huggingface-hub>=0.15.0",
        "Pillow>=8.0.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "mediapipe>=0.10.0",
    ],
    keywords="ai, machine learning, diffusion, cartoon, image processing",
)