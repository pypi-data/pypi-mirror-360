"""
MareArts XColor - Advanced Color Extraction and Similarity Analysis

A robust, modern color extraction library for extracting dominant colors from images 
with support for mask-based region selection, advanced preprocessing, and color similarity analysis.

Key Features:
- Modern algorithms (K-means, DBSCAN) with LAB color space
- Color similarity analysis with query-based matching
- Mask support for region-specific extraction
- Robust preprocessing for lighting/noise invariance
- Multiple input formats (file paths, OpenCV, PIL, numpy)
- Fast performance with configurable accuracy levels

Example usage:
    from marearts_xcolor import ColorExtractor
    
    # Basic color extraction
    extractor = ColorExtractor(n_colors=5)
    colors = extractor.extract_colors('image.jpg')
    
    # Color similarity analysis
    target_colors = {'red': (255, 0, 0), 'blue': (0, 0, 255)}
    results = extractor.analyze_color_similarity('image.jpg', target_colors)
"""

from .color_extractor import ColorExtractor

__version__ = "1.0.0"
__author__ = "MareArts"
__email__ = "contact@marearts.com"
__license__ = "MIT"

__all__ = ["ColorExtractor"]