from .mig_allocator import MIGInstanceAllocator
from .mig_manager import MIGConfigManager

_MAJOR = 0  # Major version number
_MINOR = 1  # Minor version number
_PATCH = 1  # Patch version number

__version__ = f"{_MAJOR}.{_MINOR}.{_PATCH}"

__all__ = [
    "__version__",
    "MIGInstanceAllocator",
    "MIGConfigManager",
]
