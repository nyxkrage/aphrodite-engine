"""Utils."""
from os import path
import enum
from platform import uname
import uuid

import psutil
import torch

from aphrodite import cuda_utils


class Device(enum.Enum):
    GPU = enum.auto()
    CPU = enum.auto()


class Counter:

    def __init__(self, start: int = 0) -> None:
        self.counter = start

    def __next__(self) -> int:
        i = self.counter
        self.counter += 1
        return i

    def reset(self) -> None:
        self.counter = 0


def get_max_shared_memory_bytes(gpu: int = 0) -> int:
    """Returns the maximum shared memory per thread block in bytes."""
    # https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html
    cudaDevAttrMaxSharedMemoryPerBlockOptin = 97  # pylint: disable=invalid-name
    max_shared_mem = cuda_utils.get_device_attribute(
        cudaDevAttrMaxSharedMemoryPerBlockOptin, gpu)
    return int(max_shared_mem)


def get_gpu_memory(gpu: int = 0) -> int:
    """Returns the total memory of the GPU in bytes."""
    return torch.cuda.get_device_properties(gpu).total_memory


def get_cpu_memory() -> int:
    """Returns the total CPU memory of the node or container in bytes."""

    memory_limit = psutil.virtual_memory().total

    for limit_file in [
            "/sys/fs/cgroup/memory/memory.limit_in_bytes",  # v1
            "/sys/fs/cgroup/memory.max"  # v2
    ]:
        if path.exists(limit_file):
            with open(limit_file) as f:
                content = f.read().strip()
                if content.isnumeric():  # v2 can have "max" as limit
                    memory_limit = min(memory_limit, int(content))

    return memory_limit


def random_uuid() -> str:
    return str(uuid.uuid4().hex)


def in_wsl() -> bool:
    # Reference: https://github.com/microsoft/WSL/issues/4071
    return "microsoft" in " ".join(uname()).lower()
