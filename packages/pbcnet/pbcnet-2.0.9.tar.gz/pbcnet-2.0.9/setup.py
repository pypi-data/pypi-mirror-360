from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dependencies are now defined in pyproject.toml.
# This file is kept for compatibility with older tools.

setup(
    name="pbcnet",
    version="2.0.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="PBCNet: Deep learning framework for protein-ligand binding affinity prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pbcnet",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.8",
    # install_requires is no longer needed here as it's handled by pyproject.toml
    include_package_data=True,
    package_data={
        "pbcnet": ["*.pth", "case/toy_data/*"],
    },
    entry_points={
        "console_scripts": [
            "pbcnet=pbcnet.cli:main",
        ],
    },
)