"""
MareArts XColor - Advanced Color Extraction and Similarity Analysis

A robust, modern color extraction library for extracting dominant colors from images 
with support for mask-based region selection, advanced preprocessing, and color similarity analysis.
"""

# Import version information
from ._version import __version__

# Import the main class
from .color_extractor import ColorExtractor

# Import GPU utilities (optional)
try:
    from .gpu_utils import is_gpu_available, get_gpu_info, print_gpu_info
    from .color_extractor_gpu import ColorExtractorGPU
    GPU_SUPPORT = True
except ImportError:
    GPU_SUPPORT = False
    is_gpu_available = lambda: False
    get_gpu_info = lambda: {"available": False}
    print_gpu_info = lambda: print("GPU support not available")
    ColorExtractorGPU = None

# Print version on import (like marearts-anpr)
print(f"MareArts XColor v{__version__} - Advanced Color Extraction and Similarity Analysis")
if GPU_SUPPORT and is_gpu_available():
    print("GPU acceleration available")

__all__ = [
    "__version__",
    "ColorExtractor",
    "ColorExtractorGPU",
    "is_gpu_available",
    "get_gpu_info",
    "print_gpu_info",
    "GPU_SUPPORT"
]