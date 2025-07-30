from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 定义具体版本的依赖
install_requires = [
    "numpy>=1.21.0,<1.25.0",
    "pandas>=1.5.0,<2.1.0",
    "packaging>=21.0",
    "PyYAML>=5.4.0,<7.0.0",
    "pydantic>=1.8.0,<2.0.0",
    "scipy>=1.8.0,<1.11.0",
    "matplotlib>=3.5.0,<3.8.0",
    "rdkit-pypi",
    "networkx>=2.8.0,<4.0.0",
    "psutil>=5.8.0,<6.0.0",
    "tqdm>=4.60.0,<5.0.0",
    "scikit-learn>=1.1.0,<1.4.0",
    "biopython>=1.79,<2.0.0",
    "charset-normalizer==3.1.0",
    "requests>=2.25.0,<3.0.0"
]

# 可选依赖
extras_require = {
    "gpu": [
        "torch>=1.12.1,<1.13.0",
        "torchvision>=0.13.1,<0.14.0",
        "torchaudio>=0.12.1,<0.13.0",
        "dgl>=1.0.2,<1.1.0"
    ],
    "cpu": [
        "torch>=1.12.1,<1.13.0",
        "torchvision>=0.13.1,<0.14.0",
        "torchaudio>=0.12.1,<0.13.0",
        "dgl>=1.0.2,<1.1.0"
    ],
    "dev": [
        "pytest>=7.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.950"
    ]
}

setup(
    name="pbcnet",
    version="2.0.2",
    author="Jie Yu, Xia Sheng",
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
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.8,<3.12",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    package_data={
        "pbcnet": ["*.pth", "case/toy_data/*"],
    },
    entry_points={
        "console_scripts": [
            "pbcnet=pbcnet.cli:main",
        ],
    },
    zip_safe=False,
)