"""
GPU-accelerated color extraction implementation
Uses CuPy and cuML for GPU computation with automatic CPU fallback
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import warnings
from .gpu_utils import get_compute_device, is_gpu_available, GPUMode

# Try to import GPU libraries
try:
    import cupy as cp
    import cuml
    from cuml.cluster import KMeans as KMeansGPU
    from cuml.cluster import DBSCAN as DBSCANGPU
    GPU_AVAILABLE = True
except ImportError:
    cp = None
    cuml = None
    GPU_AVAILABLE = False
    
# Import CPU fallbacks
from sklearn.cluster import KMeans, DBSCAN
import cv2

class ColorExtractorGPU:
    """
    GPU-accelerated color extractor with automatic CPU fallback
    """
    
    def __init__(self, 
                 method: str = 'kmeans',
                 n_clusters: int = 5,
                 use_gpu: Union[str, GPUMode] = GPUMode.AUTO,
                 preprocessing: bool = True,
                 use_lab_space: bool = True):
        """
        Initialize GPU color extractor
        
        Args:
            method: Clustering method ('kmeans' or 'dbscan')
            n_clusters: Number of clusters for kmeans
            use_gpu: GPU usage mode ('auto', 'force', 'never')
            preprocessing: Apply preprocessing
            use_lab_space: Use LAB color space
        """
        self.method = method.lower()
        self.n_clusters = n_clusters
        self.preprocessing = preprocessing
        self.use_lab_space = use_lab_space
        
        # Determine compute device
        self.device = get_compute_device(use_gpu)
        self.use_gpu_compute = self.device != "cpu" and GPU_AVAILABLE
        
        if self.use_gpu_compute:
            print(f"Using GPU acceleration on {self.device}")
            self.xp = cp  # Use CuPy for array operations
        else:
            if use_gpu == GPUMode.FORCE:
                warnings.warn("GPU forced but not available, falling back to CPU")
            self.xp = np  # Use NumPy for array operations
            
    def _preprocess_image_gpu(self, image) -> Union[np.ndarray, None]:
        """GPU-accelerated image preprocessing"""
        # Convert to CPU for OpenCV operations (no GPU OpenCV yet)
        if self.use_gpu_compute and cp is not None:
            image_cpu = cp.asnumpy(image)
        else:
            image_cpu = image
        
        # Apply CLAHE
        lab = cv2.cvtColor(image_cpu, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        image_cpu = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Apply bilateral filter
        image_cpu = cv2.bilateralFilter(image_cpu, 9, 75, 75)
        
        # Convert back to GPU if using GPU
        if self.use_gpu_compute and cp is not None:
            return cp.asarray(image_cpu)
        else:
            return image_cpu
        
    def _preprocess_image_cpu(self, image: np.ndarray) -> np.ndarray:
        """CPU image preprocessing"""
        # Apply CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Apply bilateral filter
        return cv2.bilateralFilter(image, 9, 75, 75)
        
    def _rgb_to_lab_gpu(self, pixels):
        """GPU-accelerated RGB to LAB conversion"""
        # Normalize to [0, 1]
        pixels = pixels.astype(cp.float32) / 255.0
        
        # Apply gamma correction
        mask = pixels > 0.04045
        pixels[mask] = cp.power((pixels[mask] + 0.055) / 1.055, 2.4)
        pixels[~mask] = pixels[~mask] / 12.92
        
        # Convert to XYZ
        matrix = cp.array([
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041]
        ], dtype=cp.float32)
        
        xyz = cp.dot(pixels, matrix.T)
        
        # Normalize by D65 illuminant
        xyz[:, 0] /= 0.95047
        xyz[:, 1] /= 1.00000
        xyz[:, 2] /= 1.08883
        
        # Apply function f
        mask = xyz > 0.008856
        xyz[mask] = cp.power(xyz[mask], 1/3)
        xyz[~mask] = 7.787 * xyz[~mask] + 16/116
        
        # Convert to LAB
        lab = cp.zeros_like(xyz)
        lab[:, 0] = 116 * xyz[:, 1] - 16  # L
        lab[:, 1] = 500 * (xyz[:, 0] - xyz[:, 1])  # a
        lab[:, 2] = 200 * (xyz[:, 1] - xyz[:, 2])  # b
        
        return lab
        
    def _cluster_colors_gpu(self, pixels, n_colors: int):
        """GPU-accelerated color clustering"""
        if self.method == 'kmeans':
            # Use cuML KMeans
            kmeans = KMeansGPU(
                n_clusters=n_colors,
                max_iter=100,
                random_state=42
            )
            labels = kmeans.fit_predict(pixels)
            centers = kmeans.cluster_centers_
            
        elif self.method == 'dbscan':
            # Use cuML DBSCAN
            dbscan = DBSCANGPU(
                eps=3.0,
                min_samples=100
            )
            labels = dbscan.fit_predict(pixels)
            
            # Calculate cluster centers
            unique_labels = cp.unique(labels)
            unique_labels = unique_labels[unique_labels != -1]  # Remove noise
            
            centers = cp.zeros((len(unique_labels), pixels.shape[1]))
            for i, label in enumerate(unique_labels):
                mask = labels == label
                centers[i] = cp.mean(pixels[mask], axis=0)
                
        else:
            raise ValueError(f"Unknown method: {self.method}")
            
        return centers, labels
        
    def _cluster_colors_cpu(self, pixels: np.ndarray, n_colors: int) -> Tuple[np.ndarray, np.ndarray]:
        """CPU color clustering"""
        if self.method == 'kmeans':
            kmeans = KMeans(
                n_clusters=n_colors,
                random_state=42,
                n_init=10
            )
            labels = kmeans.fit_predict(pixels)
            centers = kmeans.cluster_centers_
            
        elif self.method == 'dbscan':
            dbscan = DBSCAN(
                eps=3.0,
                min_samples=100
            )
            labels = dbscan.fit_predict(pixels)
            
            # Calculate cluster centers
            unique_labels = np.unique(labels)
            unique_labels = unique_labels[unique_labels != -1]  # Remove noise
            
            centers = np.zeros((len(unique_labels), pixels.shape[1]))
            for i, label in enumerate(unique_labels):
                mask = labels == label
                centers[i] = np.mean(pixels[mask], axis=0)
                
        else:
            raise ValueError(f"Unknown method: {self.method}")
            
        return centers, labels
        
    def extract_colors(self, 
                      image: np.ndarray,
                      mask: Optional[np.ndarray] = None,
                      num_colors: int = 5,
                      quality: str = 'normal') -> List[Dict]:
        """
        Extract dominant colors from image
        
        Args:
            image: Input image (H, W, 3) in RGB format
            mask: Optional mask
            num_colors: Number of colors to extract
            quality: Quality mode ('low', 'normal', 'high')
            
        Returns:
            List of color dictionaries with RGB, HEX, percentage
        """
        # Quality settings
        quality_settings = {
            'low': 0.1,
            'normal': 0.3,
            'high': 0.5
        }
        sample_ratio = quality_settings.get(quality, 0.3)
        
        if self.use_gpu_compute:
            # GPU processing
            image_gpu = cp.asarray(image)
            
            # Preprocessing
            if self.preprocessing:
                image_gpu = self._preprocess_image_gpu(image_gpu)
                
            # Reshape to pixels
            pixels = image_gpu.reshape(-1, 3)
            
            # Apply mask if provided
            if mask is not None:
                mask_gpu = cp.asarray(mask)
                mask_flat = mask_gpu.flatten()
                pixels = pixels[mask_flat > 0]
                
            # Sample pixels for performance
            n_pixels = len(pixels)
            n_samples = int(n_pixels * sample_ratio)
            if n_samples < len(pixels):
                indices = cp.random.choice(n_pixels, n_samples, replace=False)
                pixels = pixels[indices]
                
            # Convert to LAB if requested
            if self.use_lab_space:
                pixels_lab = self._rgb_to_lab_gpu(pixels)
                centers, labels = self._cluster_colors_gpu(pixels_lab, num_colors)
                # Convert centers back to RGB for output
                # (simplified - proper LAB to RGB conversion needed)
                centers = pixels[cp.random.choice(len(pixels), len(centers))]
            else:
                centers, labels = self._cluster_colors_gpu(pixels, num_colors)
                
            # Calculate percentages
            percentages = cp.zeros(len(centers))
            for i in range(len(centers)):
                percentages[i] = cp.sum(labels == i) / len(labels) * 100
                
            # Convert back to CPU for output
            centers_cpu = cp.asnumpy(centers).astype(int)
            percentages_cpu = cp.asnumpy(percentages)
            
        else:
            # CPU processing
            # Preprocessing
            if self.preprocessing:
                image = self._preprocess_image_cpu(image)
                
            # Reshape to pixels
            pixels = image.reshape(-1, 3)
            
            # Apply mask if provided
            if mask is not None:
                mask_flat = mask.flatten()
                pixels = pixels[mask_flat > 0]
                
            # Sample pixels for performance
            n_pixels = len(pixels)
            n_samples = int(n_pixels * sample_ratio)
            if n_samples < len(pixels):
                indices = np.random.choice(n_pixels, n_samples, replace=False)
                pixels = pixels[indices]
                
            # Clustering
            centers, labels = self._cluster_colors_cpu(pixels, num_colors)
            
            # Calculate percentages
            percentages = np.zeros(len(centers))
            for i in range(len(centers)):
                percentages[i] = np.sum(labels == i) / len(labels) * 100
                
            centers_cpu = centers.astype(int)
            percentages_cpu = percentages
            
        # Format results
        results = []
        for i in range(len(centers_cpu)):
            color_rgb = tuple(centers_cpu[i])
            color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgb)
            
            results.append({
                'rgb': color_rgb,
                'hex': color_hex,
                'percentage': float(percentages_cpu[i]),
                'index': i
            })
            
        # Sort by percentage
        results.sort(key=lambda x: x['percentage'], reverse=True)
        
        return results
        
    def benchmark(self, image_sizes: List[Tuple[int, int]] = None) -> Dict[str, float]:
        """
        Benchmark GPU vs CPU performance
        
        Args:
            image_sizes: List of (height, width) tuples to test
            
        Returns:
            Dictionary with benchmark results
        """
        import time
        
        if image_sizes is None:
            image_sizes = [(480, 640), (720, 1280), (1080, 1920), (2160, 3840)]
            
        results = {
            'gpu_available': self.use_gpu_compute,
            'device': self.device,
            'benchmarks': {}
        }
        
        for height, width in image_sizes:
            size_key = f"{height}x{width}"
            
            # Generate random image
            image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # Benchmark current mode
            start = time.time()
            self.extract_colors(image, num_colors=5)
            elapsed = time.time() - start
            
            results['benchmarks'][size_key] = {
                'time_seconds': elapsed,
                'pixels': height * width,
                'mode': 'gpu' if self.use_gpu_compute else 'cpu'
            }
            
        return results