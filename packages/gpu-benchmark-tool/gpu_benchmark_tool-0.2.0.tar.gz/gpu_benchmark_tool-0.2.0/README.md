# GPU Benchmark Tool

A comprehensive GPU health monitoring and optimization tool.

## Installation

```bash
pip install -e .
```

For NVIDIA GPU support:
```bash
pip install -e ".[nvidia]"
```

## Usage

```bash
# List available GPUs
gpu-benchmark list

# Run benchmark
gpu-benchmark benchmark

# Run in mock mode (no GPU required)
gpu-benchmark benchmark --mock
```

## Features

- GPU health monitoring
- Stress testing
- Performance scoring
- Multi-GPU support
- Mock mode for development

## License

MIT
