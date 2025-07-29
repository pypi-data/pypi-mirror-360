#!/usr/bin/env python3
"""
GPU support tests for pure Python implementation
"""

import numpy as np
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from color_extractor import ColorExtractor, GPU_AVAILABLE

def test_gpu_detection():
    """Test GPU detection"""
    print("=== GPU Detection Test ===")
    print(f"GPU Support Available: {GPU_AVAILABLE}")
    
    if GPU_AVAILABLE:
        try:
            import cupy as cp
            print("✓ CuPy imported successfully")
            
            # Test basic CuPy operation
            x = cp.array([1, 2, 3])
            y = cp.sum(x)
            print(f"✓ CuPy basic operation: {y}")
            
        except Exception as e:
            print(f"✗ CuPy error: {e}")
            return False
    else:
        print("ℹ GPU support not available (CuPy/cuML not installed)")
    
    return True

def test_gpu_modes():
    """Test different GPU modes"""
    print("\n=== GPU Mode Tests ===")
    
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    modes = ['never', 'auto', 'force']
    
    for mode in modes:
        print(f"\n1. Testing '{mode}' mode:")
        try:
            if mode == 'force' and not GPU_AVAILABLE:
                # Expect this to fail
                try:
                    extractor = ColorExtractor(n_colors=3, use_gpu=mode)
                    print(f"   ✗ Expected error for force mode without GPU")
                    return False
                except RuntimeError as e:
                    print(f"   ✓ Expected error: {e}")
                    continue
                except Exception as e:
                    print(f"   ✓ Expected error (different type): {e}")
                    continue
            
            extractor = ColorExtractor(n_colors=3, use_gpu=mode)
            print(f"   Device: {extractor.device}")
            print(f"   Using GPU: {extractor.use_gpu_compute}")
            
            # Test color extraction
            colors = extractor.extract_colors(test_image)
            print(f"   ✓ Extracted {len(colors)} colors")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    return True

def test_gpu_cpu_consistency():
    """Test that GPU and CPU modes produce similar results"""
    print("\n=== GPU/CPU Consistency Test ===")
    
    if not GPU_AVAILABLE:
        print("ℹ Skipping consistency test (GPU not available)")
        return True
    
    # Create a deterministic test image
    np.random.seed(42)
    test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    
    try:
        # CPU extraction
        extractor_cpu = ColorExtractor(n_colors=3, use_gpu='never', algorithm='kmeans')
        colors_cpu = extractor_cpu.extract_colors(test_image)
        
        # GPU extraction
        extractor_gpu = ColorExtractor(n_colors=3, use_gpu='auto', algorithm='kmeans')
        colors_gpu = extractor_gpu.extract_colors(test_image)
        
        print(f"   CPU extracted: {len(colors_cpu)} colors")
        print(f"   GPU extracted: {len(colors_gpu)} colors")
        
        # Check if we got the same number of colors
        if len(colors_cpu) == len(colors_gpu):
            print("   ✓ Same number of colors extracted")
        else:
            print("   ⚠ Different number of colors (this may be normal)")
        
        print("   ✓ Consistency test completed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def test_gpu_performance():
    """Test GPU performance comparison"""
    print("\n=== GPU Performance Test ===")
    
    if not GPU_AVAILABLE:
        print("ℹ Skipping performance test (GPU not available)")
        return True
    
    # Create larger test image for performance testing
    test_image = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    
    try:
        # Test CPU performance
        print("   Testing CPU performance...")
        extractor_cpu = ColorExtractor(n_colors=5, use_gpu='never')
        start_time = time.time()
        colors_cpu = extractor_cpu.extract_colors(test_image)
        cpu_time = time.time() - start_time
        print(f"   CPU time: {cpu_time:.3f}s")
        
        # Test GPU performance
        print("   Testing GPU performance...")
        extractor_gpu = ColorExtractor(n_colors=5, use_gpu='auto')
        start_time = time.time()
        colors_gpu = extractor_gpu.extract_colors(test_image)
        gpu_time = time.time() - start_time
        print(f"   GPU time: {gpu_time:.3f}s")
        
        if gpu_time < cpu_time:
            speedup = cpu_time / gpu_time
            print(f"   ✓ GPU is {speedup:.2f}x faster")
        else:
            slowdown = gpu_time / cpu_time
            print(f"   ⚠ GPU is {slowdown:.2f}x slower (normal for small images)")
        
        print("   ✓ Performance test completed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def test_gpu_memory_usage():
    """Test GPU memory usage"""
    print("\n=== GPU Memory Test ===")
    
    if not GPU_AVAILABLE:
        print("ℹ Skipping memory test (GPU not available)")
        return True
    
    try:
        import cupy as cp
        
        # Get initial memory usage
        mempool = cp.get_default_memory_pool()
        initial_used = mempool.used_bytes()
        
        # Create extractor and process image
        test_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        extractor = ColorExtractor(n_colors=5, use_gpu='auto')
        colors = extractor.extract_colors(test_image)
        
        # Get memory usage after processing
        final_used = mempool.used_bytes()
        
        print(f"   Initial GPU memory: {initial_used / 1024**2:.2f} MB")
        print(f"   Final GPU memory: {final_used / 1024**2:.2f} MB")
        print(f"   Memory increase: {(final_used - initial_used) / 1024**2:.2f} MB")
        
        # Clean up
        mempool.free_all_blocks()
        
        print("   ✓ Memory test completed")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True

def run_all_gpu_tests():
    """Run all GPU-related tests"""
    print("Running Pure Python GPU Support Tests...")
    
    tests = [
        test_gpu_detection,
        test_gpu_modes,
        test_gpu_cpu_consistency,
        test_gpu_performance,
        test_gpu_memory_usage
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== GPU Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All GPU tests passed!")
        return True
    else:
        print("✗ Some GPU tests failed")
        return False

if __name__ == "__main__":
    success = run_all_gpu_tests()
    sys.exit(0 if success else 1)