"""
MareArts XColor - Advanced Color Extraction and Similarity Analysis

A robust, modern color extraction library for extracting dominant colors from images 
with support for mask-based region selection, advanced preprocessing, and color similarity analysis.
"""

# Import version information
from ._version import __version__

# Import the main class
from .color_extractor import ColorExtractor

# Print version on import (like marearts-anpr)
print(f"MareArts XColor v{__version__} - Advanced Color Extraction and Similarity Analysis")

__all__ = [
    "__version__",
    "ColorExtractor"
]