"""
GPU detection and management utilities for marearts-xcolor
Provides automatic GPU detection and fallback mechanisms
"""

import os
import sys
import warnings
from typing import Dict, Optional, Tuple, Union
from enum import Enum

class GPUMode(Enum):
    """GPU usage modes"""
    AUTO = "auto"      # Automatically detect and use GPU if available
    FORCE = "force"    # Force GPU usage, error if not available
    NEVER = "never"    # Never use GPU, always use CPU
    
class GPUBackend(Enum):
    """Available GPU backends"""
    CUDA = "cuda"
    OPENCL = "opencl"
    MPS = "mps"  # Apple Metal Performance Shaders
    CPU = "cpu"

class GPUDetector:
    """GPU detection and management class"""
    
    def __init__(self):
        self._gpu_available = None
        self._gpu_info = None
        self._backend = None
        
    def detect_gpu(self) -> Dict[str, Union[bool, str, int]]:
        """
        Detect available GPU hardware and libraries
        
        Returns:
            dict: GPU information including availability, type, memory, etc.
        """
        gpu_info = {
            "available": False,
            "backend": "cpu",
            "device_count": 0,
            "device_name": None,
            "memory_gb": 0,
            "cuda_available": False,
            "opencl_available": False,
            "mps_available": False,
            "cupy_available": False,
            "cuml_available": False,
        }
        
        # Check CUDA availability
        gpu_info["cuda_available"] = self._check_cuda()
        
        # Check OpenCL availability
        gpu_info["opencl_available"] = self._check_opencl()
        
        # Check Apple Metal (MPS) availability
        gpu_info["mps_available"] = self._check_mps()
        
        # Check CuPy availability
        gpu_info["cupy_available"] = self._check_cupy()
        
        # Check cuML availability
        gpu_info["cuml_available"] = self._check_cuml()
        
        # Determine best available backend
        if gpu_info["cuda_available"] and gpu_info["cupy_available"]:
            gpu_info["available"] = True
            gpu_info["backend"] = "cuda"
            gpu_info.update(self._get_cuda_device_info())
        elif gpu_info["mps_available"]:
            gpu_info["available"] = True
            gpu_info["backend"] = "mps"
            gpu_info.update(self._get_mps_device_info())
        elif gpu_info["opencl_available"]:
            gpu_info["available"] = True
            gpu_info["backend"] = "opencl"
            gpu_info.update(self._get_opencl_device_info())
            
        self._gpu_info = gpu_info
        self._gpu_available = gpu_info["available"]
        self._backend = gpu_info["backend"]
        
        return gpu_info
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            # Check NVIDIA driver
            import subprocess
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode != 0:
                return False
                
            # Check PyTorch CUDA (lightweight check)
            try:
                import torch
                return torch.cuda.is_available()
            except ImportError:
                pass
                
            # Check TensorFlow GPU
            try:
                import tensorflow as tf
                return len(tf.config.list_physical_devices('GPU')) > 0
            except ImportError:
                pass
                
            return True  # nvidia-smi worked
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
            
    def _check_opencl(self) -> bool:
        """Check if OpenCL is available"""
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            return len(platforms) > 0
        except ImportError:
            return False
            
    def _check_mps(self) -> bool:
        """Check if Apple Metal Performance Shaders is available"""
        if sys.platform != "darwin":
            return False
            
        try:
            import torch
            return torch.backends.mps.is_available()
        except ImportError:
            return False
            
    def _check_cupy(self) -> bool:
        """Check if CuPy is available"""
        try:
            import cupy as cp
            # Try to create a small array to verify it works
            test_array = cp.array([1, 2, 3])
            del test_array
            return True
        except (ImportError, Exception):
            return False
            
    def _check_cuml(self) -> bool:
        """Check if cuML is available"""
        try:
            import cuml
            return True
        except ImportError:
            return False
            
    def _get_cuda_device_info(self) -> Dict[str, Union[str, int]]:
        """Get CUDA device information"""
        info = {}
        try:
            import cupy as cp
            device = cp.cuda.Device(0)
            info["device_count"] = cp.cuda.runtime.getDeviceCount()
            info["device_name"] = device.name.decode('utf-8')
            info["memory_gb"] = device.mem_info[1] / (1024**3)  # Total memory in GB
        except Exception:
            try:
                import torch
                if torch.cuda.is_available():
                    info["device_count"] = torch.cuda.device_count()
                    info["device_name"] = torch.cuda.get_device_name(0)
                    info["memory_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            except Exception:
                pass
        return info
        
    def _get_opencl_device_info(self) -> Dict[str, Union[str, int]]:
        """Get OpenCL device information"""
        info = {}
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            if platforms:
                devices = platforms[0].get_devices()
                if devices:
                    device = devices[0]
                    info["device_count"] = len(devices)
                    info["device_name"] = device.name
                    info["memory_gb"] = device.global_mem_size / (1024**3)
        except Exception:
            pass
        return info
        
    def _get_mps_device_info(self) -> Dict[str, Union[str, int]]:
        """Get Apple Metal device information"""
        info = {
            "device_count": 1,
            "device_name": "Apple Metal GPU",
            "memory_gb": 0  # Hard to get exact memory on MPS
        }
        return info
        
    @property
    def is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        if self._gpu_available is None:
            self.detect_gpu()
        return self._gpu_available
        
    @property
    def backend(self) -> str:
        """Get the available GPU backend"""
        if self._backend is None:
            self.detect_gpu()
        return self._backend
        
    def get_compute_device(self, mode: Union[str, GPUMode] = GPUMode.AUTO) -> str:
        """
        Get the compute device based on mode and availability
        
        Args:
            mode: GPU usage mode (auto, force, never)
            
        Returns:
            str: Device to use ('cuda', 'mps', 'cpu', etc.)
            
        Raises:
            RuntimeError: If mode is 'force' but no GPU is available
        """
        if isinstance(mode, str):
            mode = GPUMode(mode.lower())
            
        if mode == GPUMode.NEVER:
            return "cpu"
            
        if not self.is_gpu_available:
            if mode == GPUMode.FORCE:
                raise RuntimeError("GPU requested but not available. "
                                 "Install CUDA and CuPy/cuML for GPU support.")
            return "cpu"
            
        return self.backend
        
    def validate_gpu_libraries(self) -> Dict[str, bool]:
        """
        Validate all GPU-related libraries
        
        Returns:
            dict: Status of each GPU library
        """
        if self._gpu_info is None:
            self.detect_gpu()
            
        return {
            "cuda": self._gpu_info.get("cuda_available", False),
            "cupy": self._gpu_info.get("cupy_available", False),
            "cuml": self._gpu_info.get("cuml_available", False),
            "opencl": self._gpu_info.get("opencl_available", False),
            "mps": self._gpu_info.get("mps_available", False),
        }
        
    def print_gpu_info(self):
        """Print detailed GPU information"""
        if self._gpu_info is None:
            self.detect_gpu()
            
        print("=== GPU Detection Results ===")
        print(f"GPU Available: {self._gpu_info['available']}")
        print(f"Backend: {self._gpu_info['backend']}")
        
        if self._gpu_info['available']:
            print(f"Device Count: {self._gpu_info['device_count']}")
            print(f"Device Name: {self._gpu_info['device_name']}")
            print(f"Memory: {self._gpu_info['memory_gb']:.2f} GB")
        else:
            print("\n=== Installation Instructions ===")
            print("To enable GPU acceleration, install GPU dependencies:")
            print("  pip install marearts-xcolor[gpu]")
            print("  # or")
            print("  pip install cupy-cuda12x cuml  # for CUDA 12.x")
            print("  pip install cupy-cuda11x cuml  # for CUDA 11.x")
            
        print("\n=== Library Status ===")
        libraries = self.validate_gpu_libraries()
        for lib, available in libraries.items():
            status = "✓" if available else "✗"
            print(f"{status} {lib}")
            
# Global detector instance
_gpu_detector = GPUDetector()

def get_gpu_info() -> Dict[str, Union[bool, str, int]]:
    """Get GPU information"""
    return _gpu_detector.detect_gpu()

def is_gpu_available() -> bool:
    """Check if GPU is available"""
    return _gpu_detector.is_gpu_available

def get_compute_device(mode: Union[str, GPUMode] = "auto") -> str:
    """Get compute device based on mode"""
    return _gpu_detector.get_compute_device(mode)

def print_gpu_info():
    """Print GPU information"""
    _gpu_detector.print_gpu_info()

def get_installation_instructions() -> Dict[str, Dict[str, str]]:
    """Get installation instructions for different user types"""
    return {
        "cpu_only": {
            "command": "pip install marearts-xcolor",
            "description": "Basic installation for CPU-only usage"
        },
        "gpu_cuda12": {
            "command": "pip install marearts-xcolor[gpu]",
            "description": "GPU acceleration with CUDA 12.x support",
            "alternative": "pip install marearts-xcolor cupy-cuda12x cuml"
        },
        "gpu_cuda11": {
            "command": "pip install marearts-xcolor cupy-cuda11x cuml",
            "description": "GPU acceleration with CUDA 11.x support"
        },
        "check_cuda": {
            "command": "nvidia-smi",
            "description": "Check CUDA version and GPU availability"
        }
    }

def print_installation_guide():
    """Print installation guide for different user types"""
    instructions = get_installation_instructions()
    
    print("=== MareArts XColor Installation Guide ===")
    print()
    print("1. CPU-only users (no GPU acceleration):")
    print(f"   {instructions['cpu_only']['command']}")
    print(f"   {instructions['cpu_only']['description']}")
    print()
    print("2. GPU users (CUDA 12.x):")
    print(f"   {instructions['gpu_cuda12']['command']}")
    print(f"   {instructions['gpu_cuda12']['description']}")
    print(f"   Alternative: {instructions['gpu_cuda12']['alternative']}")
    print()
    print("3. GPU users (CUDA 11.x):")
    print(f"   {instructions['gpu_cuda11']['command']}")
    print(f"   {instructions['gpu_cuda11']['description']}")
    print()
    print("4. Check your CUDA version:")
    print(f"   {instructions['check_cuda']['command']}")
    print(f"   {instructions['check_cuda']['description']}")
    print()
    print("=== Usage Examples ===")
    print("# CPU mode (always works)")
    print("extractor = ColorExtractor(use_gpu='never')")
    print()
    print("# Auto mode (uses GPU if available, fallback to CPU)")
    print("extractor = ColorExtractor(use_gpu='auto')")
    print()
    print("# Force GPU mode (fails if GPU not available)")
    print("extractor = ColorExtractor(use_gpu='force')")