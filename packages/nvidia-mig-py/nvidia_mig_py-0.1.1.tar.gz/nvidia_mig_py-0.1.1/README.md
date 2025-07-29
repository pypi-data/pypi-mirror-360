# NVIDIA MIG Manager

A Python library for managing NVIDIA GPU Multi-Instance GPU (MIG) partitions and resources. This library provides a simple interface to create, list, and destroy MIG partitions, as well as monitor their resource usage. **Only tested with NVIDIA A30 GPUs.**

---

## Features

- **MIG Partition Management**: Create, list, and destroy MIG partitions on NVIDIA GPUs that support MIG.
- **Resource Allocator**: Automatically create MIG partitions based on workload memory requirements.
- **Resource Monitoring**: Track memory, compute utilization, temperature, and power usage for each MIG partition to maintain optimal performance and prevent bottlenecks.

---

## Installation

### Requirements

- **Python**: >= 3.7
- **NVIDIA GPU with MIG support**
- **NVIDIA Driver and DCGM Python bindings**

### Install via pip

To install the library, simply clone the repository and install dependencies:

```bash
git clone git@github.com:MoonOoOoO/nvidia-mig-py.git
pip install .
```
