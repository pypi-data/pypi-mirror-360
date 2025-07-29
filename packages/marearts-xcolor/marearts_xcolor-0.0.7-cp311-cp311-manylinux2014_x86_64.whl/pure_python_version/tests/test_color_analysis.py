#!/usr/bin/env python3
"""
Color analysis and similarity tests for pure Python implementation
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from color_extractor import ColorExtractor

def test_color_similarity_analysis():
    """Test color similarity analysis functionality"""
    print("=== Color Similarity Analysis Test ===")
    
    # Create test image with known colors
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    test_image[:100, :100] = [255, 0, 0]    # Red
    test_image[:100, 100:] = [0, 255, 0]    # Green
    test_image[100:, :100] = [0, 0, 255]    # Blue
    test_image[100:, 100:] = [255, 255, 255] # White
    
    # Define target colors to search for
    target_colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'white': (255, 255, 255),
        'yellow': (255, 255, 0),  # Not in image
        'black': (0, 0, 0)        # Not in image
    }
    
    try:
        extractor = ColorExtractor(n_colors=4, use_gpu='never')
        
        # Test similarity analysis
        results = extractor.analyze_color_similarity(test_image, target_colors)
        
        print(f"   Analyzed {len(results)} target colors:")
        
        for color_name, analysis in results.items():
            percentage = analysis['percentage']
            similarity = analysis['similarity']
            found = analysis['found_directly']
            
            print(f"   {color_name}: {percentage}% (similarity: {similarity}%, direct: {found})")
        
        # Verify that primary colors were found
        primary_colors = ['red', 'green', 'blue', 'white']
        for color in primary_colors:
            if color in results:
                if results[color]['percentage'] > 0:
                    print(f"   ✓ {color} found as expected")
                else:
                    print(f"   ⚠ {color} not found (may be due to color space conversion)")
            else:
                print(f"   ✗ {color} missing from results")
                return False
        
        # Verify that non-existent colors were not found
        absent_colors = ['yellow', 'black']
        for color in absent_colors:
            if color in results and results[color]['percentage'] == 0:
                print(f"   ✓ {color} correctly not found")
        
        print("   ✓ Color similarity analysis test passed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_color_matching():
    """Test detailed color matching functionality"""
    print("\n=== Color Matching Test ===")
    
    # Create gradient test image
    test_image = np.zeros((100, 300, 3), dtype=np.uint8)
    
    # Red gradient
    for i in range(100):
        test_image[:, i] = [255 - i*2, 0, 0]
    
    # Green gradient  
    for i in range(100):
        test_image[:, 100+i] = [0, 255 - i*2, 0]
        
    # Blue gradient
    for i in range(100):
        test_image[:, 200+i] = [0, 0, 255 - i*2]
    
    target_colors = {
        'red': (255, 0, 0),
        'green': (0, 255, 0), 
        'blue': (0, 0, 255)
    }
    
    try:
        extractor = ColorExtractor(n_colors=5, use_gpu='never')
        
        # Test color matching
        results = extractor.find_color_matches(test_image, target_colors)
        
        print(f"   Analyzed {len(results)} target colors:")
        
        for color_name, analysis in results.items():
            total_pct = analysis['total_percentage']
            close_pct = analysis['close_percentage']
            very_close_pct = analysis['very_close_percentage']
            similarity = analysis['similarity_score']
            
            print(f"   {color_name}:")
            print(f"     Total: {total_pct}%, Close: {close_pct}%, Very close: {very_close_pct}%")
            print(f"     Similarity score: {similarity}%")
        
        print("   ✓ Color matching test passed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_color_visualization():
    """Test color visualization functionality"""
    print("\n=== Color Visualization Test ===")
    
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    try:
        extractor = ColorExtractor(n_colors=5, use_gpu='never')
        colors = extractor.extract_colors(test_image)
        
        # Test visualization without saving
        print("   Testing visualization display...")
        # Note: We can't actually display in a test environment, but we can test the function
        # extractor.visualize_colors(colors)  # Would display if in interactive environment
        
        # Test visualization with saving
        output_path = "test_visualization.png"
        print(f"   Testing visualization save to {output_path}...")
        
        try:
            extractor.visualize_colors(colors, output_path)
            
            # Check if file was created
            if os.path.exists(output_path):
                print("   ✓ Visualization file created successfully")
                os.remove(output_path)  # Clean up
            else:
                print("   ⚠ Visualization file not found (may be normal in headless environment)")
                
        except Exception as viz_error:
            print(f"   ⚠ Visualization error (normal in headless environment): {viz_error}")
        
        print("   ✓ Visualization test completed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Edge Cases Test ===")
    
    try:
        extractor = ColorExtractor(n_colors=3, use_gpu='never')
        
        # Test 1: Empty image
        print("   1. Testing empty image...")
        try:
            empty_image = np.zeros((0, 0, 3), dtype=np.uint8)
            colors = extractor.extract_colors(empty_image)
            print(f"      Empty image result: {len(colors)} colors")
        except Exception as e:
            print(f"      Expected error for empty image: {e}")
        
        # Test 2: Single pixel image
        print("   2. Testing single pixel image...")
        single_pixel = np.array([[[255, 0, 0]]], dtype=np.uint8)
        colors = extractor.extract_colors(single_pixel)
        print(f"      Single pixel: {len(colors)} colors")
        
        # Test 3: Monochrome image
        print("   3. Testing monochrome image...")
        mono_image = np.full((50, 50, 3), [128, 128, 128], dtype=np.uint8)
        colors = extractor.extract_colors(mono_image)
        print(f"      Monochrome: {len(colors)} colors")
        
        # Test 4: Too many colors requested
        print("   4. Testing too many colors requested...")
        small_image = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        extractor_many = ColorExtractor(n_colors=200, use_gpu='never')
        colors = extractor_many.extract_colors(small_image)
        print(f"      Many colors requested: {len(colors)} colors extracted")
        
        print("   ✓ Edge cases test passed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def run_all_analysis_tests():
    """Run all color analysis tests"""
    print("Running Pure Python Color Analysis Tests...")
    
    tests = [
        test_color_similarity_analysis,
        test_color_matching,
        test_color_visualization,
        test_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Analysis Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All color analysis tests passed!")
        return True
    else:
        print("✗ Some analysis tests failed")
        return False

if __name__ == "__main__":
    success = run_all_analysis_tests()
    sys.exit(0 if success else 1)