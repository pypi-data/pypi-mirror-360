#!/usr/bin/env python3
"""
Basic functionality tests for pure Python implementation
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from color_extractor import ColorExtractor

def test_basic_color_extraction():
    """Test basic color extraction functionality"""
    print("=== Basic Color Extraction Test ===")
    
    # Create a simple 4-color test image
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    test_image[:100, :100] = [255, 0, 0]    # Red
    test_image[:100, 100:] = [0, 255, 0]    # Green  
    test_image[100:, :100] = [0, 0, 255]    # Blue
    test_image[100:, 100:] = [255, 255, 0]  # Yellow
    
    # Test CPU mode
    print("\n1. Testing CPU mode:")
    try:
        extractor = ColorExtractor(n_colors=4, use_gpu='never')
        colors = extractor.extract_colors(test_image)
        
        print(f"   ✓ Extracted {len(colors)} colors")
        for i, color in enumerate(colors):
            print(f"   Color {i+1}: RGB{color['color']} - {color['percentage']}%")
        
        assert len(colors) == 4, f"Expected 4 colors, got {len(colors)}"
        print("   ✓ Basic extraction test passed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def test_different_algorithms():
    """Test different clustering algorithms"""
    print("\n=== Algorithm Test ===")
    
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    algorithms = ['kmeans', 'dbscan']
    
    for algorithm in algorithms:
        print(f"\n1. Testing {algorithm} algorithm:")
        try:
            extractor = ColorExtractor(
                n_colors=3, 
                algorithm=algorithm, 
                use_gpu='never'
            )
            colors = extractor.extract_colors(test_image)
            
            print(f"   ✓ {algorithm}: Extracted {len(colors)} colors")
            
        except Exception as e:
            print(f"   ✗ {algorithm} error: {e}")
            return False
    
    return True

def test_preprocessing_options():
    """Test preprocessing options"""
    print("\n=== Preprocessing Options Test ===")
    
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    options = [
        {'preprocessing': True, 'lab_space': True},
        {'preprocessing': True, 'lab_space': False},
        {'preprocessing': False, 'lab_space': True},
        {'preprocessing': False, 'lab_space': False}
    ]
    
    for i, opts in enumerate(options):
        print(f"\n{i+1}. Testing preprocessing={opts['preprocessing']}, lab_space={opts['lab_space']}:")
        try:
            extractor = ColorExtractor(
                n_colors=3, 
                use_gpu='never',
                **opts
            )
            colors = extractor.extract_colors(test_image)
            
            print(f"   ✓ Extracted {len(colors)} colors")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    return True

def test_mask_functionality():
    """Test mask functionality"""
    print("\n=== Mask Functionality Test ===")
    
    # Create test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:50, :] = [255, 0, 0]    # Red top half
    test_image[50:, :] = [0, 255, 0]    # Green bottom half
    
    # Create mask for top half only
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[:50, :] = 255  # White for top half
    
    try:
        extractor = ColorExtractor(n_colors=2, use_gpu='never')
        
        # Test without mask
        colors_no_mask = extractor.extract_colors(test_image)
        print(f"   Without mask: {len(colors_no_mask)} colors")
        
        # Test with mask
        colors_with_mask = extractor.extract_colors(test_image, mask)
        print(f"   With mask: {len(colors_with_mask)} colors")
        
        print("   ✓ Mask functionality test passed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def run_all_basic_tests():
    """Run all basic functionality tests"""
    print("Running Pure Python Basic Functionality Tests...")
    
    tests = [
        test_basic_color_extraction,
        test_different_algorithms,
        test_preprocessing_options,
        test_mask_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All basic functionality tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_all_basic_tests()
    sys.exit(0 if success else 1)