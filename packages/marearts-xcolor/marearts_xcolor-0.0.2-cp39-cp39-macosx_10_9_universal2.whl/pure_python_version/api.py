#!/usr/bin/env python3

from typing import List, Dict, Optional, Union
import json
from color_extractor import ColorExtractor


def extract_colors_from_image(image_path: str, 
                            mask_path: Optional[str] = None,
                            n_colors: int = 5,
                            algorithm: str = 'kmeans',
                            preprocessing: bool = True,
                            output_format: str = 'json') -> Union[List[Dict], str]:
    """
    Simple API function to extract colors from an image.
    
    Args:
        image_path: Path to the input image
        mask_path: Optional path to mask image (white areas will be analyzed)
        n_colors: Number of dominant colors to extract (default: 5)
        algorithm: 'kmeans' or 'dbscan' (default: 'kmeans')
        preprocessing: Apply noise reduction and lighting normalization (default: True)
        output_format: 'json' or 'dict' (default: 'json')
        
    Returns:
        Color extraction results as list of dictionaries or JSON string
    """
    try:
        # Create extractor
        extractor = ColorExtractor(
            n_colors=n_colors,
            algorithm=algorithm,
            preprocessing=preprocessing,
            lab_space=True  # Use LAB space for better perceptual accuracy
        )
        
        # Extract colors
        colors = extractor.extract_colors(image_path, mask_path)
        
        # Format output
        if output_format == 'json':
            return json.dumps(colors, indent=2)
        else:
            return colors
            
    except Exception as e:
        error_result = {'error': str(e)}
        if output_format == 'json':
            return json.dumps(error_result, indent=2)
        else:
            return [error_result]


def extract_colors_fast(image_path: str, n_colors: int = 3) -> List[Dict]:
    """
    Fast color extraction with minimal preprocessing.
    
    Args:
        image_path: Path to the input image
        n_colors: Number of colors to extract (default: 3)
        
    Returns:
        List of color dictionaries
    """
    extractor = ColorExtractor(
        n_colors=n_colors,
        algorithm='kmeans',
        preprocessing=False,  # Skip preprocessing for speed
        lab_space=False       # Use RGB for speed
    )
    
    return extractor.extract_colors(image_path)


def extract_colors_robust(image_path: str, 
                         mask_path: Optional[str] = None,
                         n_colors: int = 8) -> List[Dict]:
    """
    Robust color extraction with full preprocessing.
    
    Args:
        image_path: Path to the input image
        mask_path: Optional path to mask image
        n_colors: Number of colors to extract (default: 8)
        
    Returns:
        List of color dictionaries
    """
    extractor = ColorExtractor(
        n_colors=n_colors,
        algorithm='kmeans',
        preprocessing=True,   # Full preprocessing
        lab_space=True        # Use LAB space for accuracy
    )
    
    return extractor.extract_colors(image_path, mask_path)


def main():
    """Command line interface for MareArts XColor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MareArts XColor - Extract dominant colors from images')
    parser.add_argument('image', help='Path to input image')
    parser.add_argument('--mask', help='Path to mask image (optional)')
    parser.add_argument('--colors', type=int, default=5, help='Number of colors to extract')
    parser.add_argument('--algorithm', choices=['kmeans', 'dbscan'], default='kmeans',
                       help='Clustering algorithm to use')
    parser.add_argument('--fast', action='store_true', help='Use fast extraction (less preprocessing)')
    parser.add_argument('--output', choices=['json', 'dict'], default='json',
                       help='Output format')
    parser.add_argument('--visualize', help='Save visualization to file')
    
    args = parser.parse_args()
    
    try:
        if args.fast:
            colors = extract_colors_fast(args.image, args.colors)
        else:
            colors = extract_colors_from_image(
                args.image,
                args.mask,
                args.colors,
                args.algorithm,
                preprocessing=True,
                output_format='dict'
            )
        
        # Print results
        if args.output == 'json':
            print(json.dumps(colors, indent=2))
        else:
            for i, color_info in enumerate(colors):
                color = color_info['color']
                percentage = color_info['percentage']
                print(f"Color {i+1}: RGB{color} - {percentage}%")
        
        # Create visualization if requested
        if args.visualize:
            from color_extractor import ColorExtractor
            extractor = ColorExtractor()
            extractor.visualize_colors(colors, args.visualize)
            print(f"Visualization saved to {args.visualize}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())