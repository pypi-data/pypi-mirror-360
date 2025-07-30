from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gpu-benchmark-tool",  # Change if taken: gpu-health-monitor, cloud-gpu-benchmark
    version="0.2.0",  # Bumped version for multi-vendor support
    author="Yousuf Rajput",
    author_email="ywrajput@gmail.com",
    description="Multi-vendor GPU health monitoring and workload optimization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gpu-benchmark-tool",  # UPDATE THIS
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "Topic :: System :: Hardware",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "psutil>=5.8.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "nvidia": [
            "torch>=2.0.0",
            "nvidia-ml-py>=11.450.51",
        ],
        "amd": [
            "torch>=2.0.0",  # ROCm version
        ],
        "intel": [
            "torch>=2.0.0",
            "intel-extension-for-pytorch>=2.0.0",
        ],
        "all": [
            "torch>=2.0.0",
            "nvidia-ml-py>=11.450.51",
            "intel-extension-for-pytorch>=2.0.0",
            "docker>=6.0.0",
        ],
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "build>=0.10.0",
            "twine>=4.0.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "gpu-benchmark=gpu_benchmark.cli:main",
        ],
    },
    keywords="gpu benchmark monitoring cuda rocm intel nvidia amd health performance cloud optimization",
)
