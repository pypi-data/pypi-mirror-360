# Python wrapper for Cython module
try:
    from .color_extractor_cy import ColorExtractor
except ImportError:
    # Fallback to pure Python if Cython module not available
    raise ImportError(
        "Cython module not found. Please install with: pip install marearts-xcolor"
    )