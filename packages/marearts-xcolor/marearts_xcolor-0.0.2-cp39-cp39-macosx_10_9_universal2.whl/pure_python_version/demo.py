#!/usr/bin/env python3

import cv2
import numpy as np
from color_extractor import ColorExtractor


def create_sample_image():
    """Create a sample image for testing."""
    # Create a 300x300 image with different colored regions
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Add different colored regions
    image[0:100, 0:100] = [255, 0, 0]      # Red
    image[0:100, 100:200] = [0, 255, 0]    # Green
    image[0:100, 200:300] = [0, 0, 255]    # Blue
    image[100:200, 0:150] = [255, 255, 0]  # Yellow
    image[100:200, 150:300] = [255, 0, 255] # Magenta
    image[200:300, 0:300] = [128, 128, 128] # Gray
    
    # Add some noise
    noise = np.random.randint(0, 30, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)
    
    return image


def create_sample_mask():
    """Create a sample mask for testing."""
    # Create a mask that excludes the bottom gray area
    mask = np.ones((300, 300), dtype=np.uint8) * 255
    mask[200:300, 0:300] = 0  # Exclude gray area
    
    return mask


def main():
    print("MareArts XColor Demo")
    print("=" * 50)
    
    # Create sample image and mask
    sample_image = create_sample_image()
    sample_mask = create_sample_mask()
    
    # Save sample files
    cv2.imwrite('sample_image.jpg', sample_image)
    cv2.imwrite('sample_mask.jpg', sample_mask)
    
    print("Created sample_image.jpg and sample_mask.jpg")
    
    # Test 1: Extract colors without mask
    print("\n1. Extracting colors without mask...")
    extractor = ColorExtractor(n_colors=6, algorithm='kmeans', preprocessing=True)
    colors = extractor.extract_colors(sample_image)
    
    print("Extracted colors:")
    for i, color_info in enumerate(colors):
        color = color_info['color']
        percentage = color_info['percentage']
        print(f"  Color {i+1}: RGB{color} - {percentage}%")
    
    # Visualize results
    extractor.visualize_colors(colors, 'colors_without_mask.png')
    
    # Test 2: Extract colors with mask
    print("\n2. Extracting colors with mask...")
    colors_masked = extractor.extract_colors(sample_image, sample_mask)
    
    print("Extracted colors (with mask):")
    for i, color_info in enumerate(colors_masked):
        color = color_info['color']
        percentage = color_info['percentage']
        print(f"  Color {i+1}: RGB{color} - {percentage}%")
    
    # Visualize results
    extractor.visualize_colors(colors_masked, 'colors_with_mask.png')
    
    # Test 3: Compare algorithms
    print("\n3. Comparing K-means vs DBSCAN...")
    
    # K-means
    extractor_kmeans = ColorExtractor(n_colors=5, algorithm='kmeans')
    colors_kmeans = extractor_kmeans.extract_colors(sample_image)
    print(f"K-means found {len(colors_kmeans)} colors")
    
    # DBSCAN
    extractor_dbscan = ColorExtractor(n_colors=5, algorithm='dbscan')
    colors_dbscan = extractor_dbscan.extract_colors(sample_image)
    print(f"DBSCAN found {len(colors_dbscan)} colors")
    
    # Test 4: Real image example (if available)
    print("\n4. Testing with real image (if available)...")
    try:
        # Try to load a real image
        real_image = cv2.imread('test_image.jpg')
        if real_image is not None:
            print("Found test_image.jpg, extracting colors...")
            extractor_real = ColorExtractor(n_colors=8, preprocessing=True)
            colors_real = extractor_real.extract_colors(real_image)
            
            print("Real image colors:")
            for i, color_info in enumerate(colors_real):
                color = color_info['color']
                percentage = color_info['percentage']
                print(f"  Color {i+1}: RGB{color} - {percentage}%")
            
            extractor_real.visualize_colors(colors_real, 'real_image_colors.png')
        else:
            print("No test_image.jpg found. Place an image named 'test_image.jpg' to test with real images.")
    except Exception as e:
        print(f"Could not process real image: {e}")
    
    print("\nDemo completed! Check the generated visualization files.")


if __name__ == "__main__":
    main()