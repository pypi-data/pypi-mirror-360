#!/usr/bin/env python3

import cv2
import numpy as np
from color_extractor import ColorExtractor
import json


def demo_color_similarity():
    """Demo the new color similarity feature."""
    print("MareArts XColor - Color Similarity Analysis Demo")
    print("=" * 50)
    
    # Create a test image with various colors
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add colored regions
    test_image[0:100, 0:150] = [255, 255, 255]    # White
    test_image[0:100, 150:300] = [255, 0, 0]      # Red
    test_image[0:100, 300:450] = [255, 255, 0]    # Yellow
    test_image[0:100, 450:600] = [0, 255, 0]      # Green
    
    test_image[100:200, 0:150] = [0, 0, 255]      # Blue
    test_image[100:200, 150:300] = [255, 165, 0]  # Orange
    test_image[100:200, 300:450] = [128, 0, 128]  # Purple
    test_image[100:200, 450:600] = [255, 192, 203] # Pink
    
    test_image[200:300, 0:300] = [139, 69, 19]    # Brown
    test_image[200:300, 300:600] = [128, 128, 128] # Gray
    
    test_image[300:400, 0:600] = [0, 0, 0]        # Black
    
    # Add some noise for realism
    noise = np.random.randint(0, 20, test_image.shape, dtype=np.uint8)
    test_image = cv2.add(test_image, noise)
    
    # Save test image
    cv2.imwrite('color_test_image.jpg', test_image)
    print("Created color_test_image.jpg")
    
    # Define target colors to search for
    target_colors = {
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (139, 69, 19),
        'gray': (128, 128, 128),
        'black': (0, 0, 0),
        'navy': (0, 0, 128),      # Not in image
        'lime': (0, 255, 0),      # Similar to green
        'gold': (255, 215, 0),    # Similar to yellow
    }
    
    # Create color extractor
    extractor = ColorExtractor(n_colors=10, preprocessing=True)
    
    # Test 1: Basic color similarity analysis
    print("\n1. Basic Color Similarity Analysis")
    print("-" * 40)
    
    similarity_results = extractor.analyze_color_similarity(
        test_image, 
        target_colors, 
        similarity_threshold=50.0
    )
    
    for color_name, result in similarity_results.items():
        print(f"{color_name:8}: {result['percentage']:6.2f}% "
              f"(similarity: {result['similarity']:5.1f}%, "
              f"distance: {result['distance']:5.1f})")
    
    # Test 2: Detailed color matching
    print("\n2. Detailed Color Matching")
    print("-" * 40)
    
    detailed_results = extractor.find_color_matches(test_image, target_colors)
    
    for color_name, result in detailed_results.items():
        print(f"{color_name:8}: Total {result['total_percentage']:5.1f}%, "
              f"Close {result['close_percentage']:5.1f}%, "
              f"Very close {result['very_close_percentage']:5.1f}% "
              f"(Score: {result['similarity_score']:5.1f})")
    
    # Test 3: With mask (only analyze top half)
    print("\n3. With Mask (Top Half Only)")
    print("-" * 40)
    
    # Create mask for top half
    mask = np.zeros((400, 600), dtype=np.uint8)
    mask[0:200, :] = 255  # Only top half
    
    masked_results = extractor.analyze_color_similarity(
        test_image, 
        target_colors, 
        mask=mask
    )
    
    for color_name, result in masked_results.items():
        print(f"{color_name:8}: {result['percentage']:6.2f}% "
              f"(similarity: {result['similarity']:5.1f}%)")
    
    # Test 4: Brand color analysis example
    print("\n4. Brand Color Analysis Example")
    print("-" * 40)
    
    brand_colors = {
        'brand_blue': (0, 123, 255),
        'brand_red': (220, 53, 69),
        'brand_green': (40, 167, 69),
        'brand_yellow': (255, 193, 7),
        'brand_purple': (102, 16, 242),
    }
    
    brand_results = extractor.analyze_color_similarity(test_image, brand_colors)
    
    print("Brand color presence in image:")
    for color_name, result in brand_results.items():
        status = "✓ Found" if result['found_directly'] else "≈ Similar"
        print(f"{color_name:12}: {result['percentage']:6.2f}% {status}")
    
    # Test 5: Save results to JSON
    print("\n5. Saving Results to JSON")
    print("-" * 40)
    
    all_results = {
        'basic_similarity': similarity_results,
        'detailed_matching': detailed_results,
        'masked_analysis': masked_results,
        'brand_analysis': brand_results
    }
    
    with open('color_analysis_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("Results saved to color_analysis_results.json")
    
    return all_results


def demo_real_world_example():
    """Demo with a more realistic example."""
    print("\n" + "=" * 50)
    print("Real World Example: Product Color Analysis")
    print("=" * 50)
    
    # Create a product-like image (e.g., a shirt)
    product_image = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Main product color (blue shirt)
    product_image[50:250, 100:300] = [30, 144, 255]  # Dodger blue
    
    # Add some variations (shadows, highlights, fabric texture)
    # Shadows
    product_image[180:250, 120:280] = [20, 100, 200]  # Darker blue
    # Highlights
    product_image[60:120, 120:180] = [100, 180, 255]  # Lighter blue
    
    # Background
    product_image[0:50, :] = [245, 245, 245]   # Light gray background
    product_image[250:300, :] = [245, 245, 245]
    product_image[:, 0:100] = [245, 245, 245]
    product_image[:, 300:400] = [245, 245, 245]
    
    # Add realistic noise
    noise = np.random.randint(0, 15, product_image.shape, dtype=np.uint8)
    product_image = cv2.add(product_image, noise)
    
    cv2.imwrite('product_example.jpg', product_image)
    print("Created product_example.jpg")
    
    # Define colors we want to check for
    query_colors = {
        'navy_blue': (0, 0, 128),
        'royal_blue': (65, 105, 225),
        'light_blue': (173, 216, 230),
        'white': (255, 255, 255),
        'gray': (128, 128, 128),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
    }
    
    # Create mask to exclude background
    mask = np.zeros((300, 400), dtype=np.uint8)
    mask[50:250, 100:300] = 255  # Only the product area
    
    extractor = ColorExtractor(n_colors=5, preprocessing=True)
    
    # Analyze product colors
    results = extractor.analyze_color_similarity(
        product_image, 
        query_colors, 
        mask=mask
    )
    
    print("\nProduct Color Analysis:")
    print("Color          | Percentage | Similarity | Status")
    print("-" * 50)
    
    for color_name, result in results.items():
        status = "Direct match" if result['found_directly'] else "Similar color"
        if result['percentage'] == 0:
            status = "Not found"
        
        print(f"{color_name:12} | {result['percentage']:8.2f}% | "
              f"{result['similarity']:8.1f}% | {status}")
    
    return results


if __name__ == "__main__":
    demo_color_similarity()
    demo_real_world_example()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("Files created:")
    print("- color_test_image.jpg")
    print("- product_example.jpg")
    print("- color_analysis_results.json")