import numpy as np
import cv2
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from typing import List, Tuple, Optional, Union, Dict
from PIL import Image
import matplotlib.pyplot as plt
import warnings

# Try to import GPU support
try:
    import cupy as cp
    from cuml.cluster import KMeans as KMeansGPU
    from cuml.cluster import DBSCAN as DBSCANGPU
    GPU_AVAILABLE = True
    
    # Simple GPU detection function
    def get_compute_device(mode):
        if mode == 'never':
            return 'cpu'
        if mode == 'force' and not GPU_AVAILABLE:
            raise RuntimeError("GPU forced but not available")
        return 'cuda' if GPU_AVAILABLE else 'cpu'
    
except ImportError:
    GPU_AVAILABLE = False
    cp = None
    KMeansGPU = None
    DBSCANGPU = None
    
    def get_compute_device(mode):
        if mode == 'force':
            raise RuntimeError("GPU forced but not available")
        return 'cpu'


class ColorExtractor:
    def __init__(self, n_colors: int = 5, algorithm: str = 'kmeans', 
                 preprocessing: bool = True, lab_space: bool = True,
                 use_gpu: str = 'auto'):
        """
        Initialize ColorExtractor with robust color extraction capabilities.
        
        Args:
            n_colors: Number of dominant colors to extract
            algorithm: 'kmeans' or 'dbscan' for clustering
            preprocessing: Apply noise reduction and lighting normalization
            lab_space: Use LAB color space for perceptual accuracy
            use_gpu: GPU usage mode ('auto', 'force', 'never')
        """
        self.n_colors = n_colors
        self.algorithm = algorithm
        self.preprocessing = preprocessing
        self.lab_space = lab_space
        
        # GPU configuration
        self.use_gpu_param = use_gpu
        if use_gpu == 'force' and not GPU_AVAILABLE:
            raise RuntimeError("GPU forced but not available")
        elif GPU_AVAILABLE and use_gpu != 'never':
            try:
                self.device = get_compute_device(use_gpu)
                self.use_gpu_compute = self.device != "cpu"
                self.xp = cp if self.use_gpu_compute else np
            except Exception as e:
                if use_gpu == 'force':
                    raise RuntimeError(f"GPU forced but not available: {e}")
                warnings.warn(f"GPU not available, falling back to CPU: {e}")
                self.use_gpu_compute = False
                self.xp = np
                self.device = "cpu"
        else:
            self.use_gpu_compute = False
            self.xp = np
            self.device = "cpu"
        
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply preprocessing for robustness against noise and lighting."""
        if not self.preprocessing:
            return image
            
        # Convert to LAB for better lighting invariance
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel for adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Apply bilateral filter for noise reduction while preserving edges
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        return filtered
    
    def _convert_to_feature_space(self, image: np.ndarray) -> np.ndarray:
        """Convert image to appropriate color space for clustering."""
        if self.lab_space:
            # LAB space is more perceptually uniform
            return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        else:
            # Use RGB for standard processing
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def _apply_mask(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply mask to limit color extraction to specific areas."""
        if mask is None:
            return image
            
        # Ensure mask is binary
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        
        # Normalize mask to 0-255 range
        mask = ((mask > 128) * 255).astype(np.uint8)
        
        # Apply mask
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        
        return masked_image
    
    def _extract_pixels(self, image: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """Extract valid pixels for clustering."""
        if mask is not None:
            # Apply mask and get only non-zero pixels
            masked_image = self._apply_mask(image, mask)
            mask_binary = mask > 128 if len(mask.shape) == 3 else mask > 128
            if len(mask.shape) == 3:
                mask_binary = cv2.cvtColor(mask.astype(np.uint8) * 255, cv2.COLOR_BGR2GRAY) > 128
            
            pixels = masked_image[mask_binary]
        else:
            # Use all pixels
            pixels = image.reshape(-1, 3)
        
        # Remove pure black pixels (likely from masking)
        pixels = pixels[~np.all(pixels == 0, axis=1)]
        
        return pixels
    
    def _cluster_colors_kmeans(self, pixels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract colors using K-means clustering."""
        if len(pixels) < self.n_colors:
            # Not enough pixels for requested number of colors
            if self.use_gpu_compute:
                unique_colors = cp.unique(pixels.reshape(-1, 3), axis=0)
                labels = cp.arange(len(unique_colors))
                return cp.asnumpy(unique_colors), cp.asnumpy(labels)
            else:
                unique_colors = np.unique(pixels.reshape(-1, 3), axis=0)
                labels = np.arange(len(unique_colors))
                return unique_colors, labels
        
        # Apply K-means clustering
        if self.use_gpu_compute:
            # GPU version
            pixels_gpu = cp.asarray(pixels) if not isinstance(pixels, cp.ndarray) else pixels
            kmeans = KMeansGPU(n_clusters=self.n_colors, random_state=42, max_iter=100)
            labels = kmeans.fit_predict(pixels_gpu)
            colors = kmeans.cluster_centers_
            return cp.asnumpy(colors), cp.asnumpy(labels)
        else:
            # CPU version
            kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
            labels = kmeans.fit_predict(pixels)
            colors = kmeans.cluster_centers_
            return colors, labels
    
    def _cluster_colors_dbscan(self, pixels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract colors using DBSCAN clustering."""
        if self.use_gpu_compute:
            # GPU version
            pixels_gpu = cp.asarray(pixels) if not isinstance(pixels, cp.ndarray) else pixels
            
            # Normalize for DBSCAN - manual scaling for GPU
            mean = cp.mean(pixels_gpu, axis=0)
            std = cp.std(pixels_gpu, axis=0)
            pixels_scaled = (pixels_gpu - mean) / (std + 1e-8)
            
            # Apply DBSCAN
            dbscan = DBSCANGPU(eps=0.5, min_samples=max(50, len(pixels) // 100))
            labels = dbscan.fit_predict(pixels_scaled)
            
            # Get cluster centers
            unique_labels = cp.unique(labels)
            colors = []
            
            for label in cp.asnumpy(unique_labels):
                if label != -1:  # Skip noise points
                    mask = labels == label
                    cluster_pixels = pixels_gpu[mask]
                    center = cp.mean(cluster_pixels, axis=0)
                    colors.append(cp.asnumpy(center))
            
            colors = np.array(colors) if colors else np.array([])
            return colors, cp.asnumpy(labels)
        else:
            # CPU version
            # Normalize pixels for DBSCAN
            scaler = StandardScaler()
            pixels_scaled = scaler.fit_transform(pixels)
            
            # Apply DBSCAN
            dbscan = DBSCAN(eps=0.5, min_samples=max(50, len(pixels) // 100))
            labels = dbscan.fit_predict(pixels_scaled)
            
            # Get cluster centers
            unique_labels = np.unique(labels)
            colors = []
            
            for label in unique_labels:
                if label == -1:  # Skip noise points
                    continue
                cluster_pixels = pixels[labels == label]
                color = np.mean(cluster_pixels, axis=0)
                colors.append(color)
        
        colors = np.array(colors)
        
        # Limit to requested number of colors
        if len(colors) > self.n_colors:
            # Sort by cluster size and take top n_colors
            cluster_sizes = [np.sum(labels == label) for label in unique_labels if label != -1]
            sorted_indices = np.argsort(cluster_sizes)[::-1][:self.n_colors]
            colors = colors[sorted_indices]
        
        return colors, labels
    
    def _calculate_percentages(self, labels: np.ndarray) -> List[float]:
        """Calculate color percentages."""
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        # Filter out noise points (-1 labels from DBSCAN)
        valid_mask = unique_labels != -1
        valid_counts = counts[valid_mask]
        
        total_pixels = np.sum(valid_counts)
        percentages = (valid_counts / total_pixels * 100).tolist()
        
        return percentages
    
    def extract_colors(self, image: Union[str, np.ndarray], 
                      mask: Optional[Union[str, np.ndarray]] = None) -> List[dict]:
        """
        Extract dominant colors from image.
        
        Args:
            image: Path to image file or numpy array
            mask: Optional mask image (white areas will be analyzed)
            
        Returns:
            List of dictionaries with color info: {'color': (R,G,B), 'percentage': float}
        """
        # Load image
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise ValueError(f"Could not load image from {image}")
        
        # Load mask if provided
        if isinstance(mask, str):
            mask = cv2.imread(mask)
            if mask is None:
                raise ValueError(f"Could not load mask from {mask}")
        
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Convert to feature space
        feature_image = self._convert_to_feature_space(processed_image)
        
        # Extract pixels
        pixels = self._extract_pixels(feature_image, mask)
        
        if len(pixels) == 0:
            return []
        
        # Cluster colors
        if self.algorithm == 'kmeans':
            colors, labels = self._cluster_colors_kmeans(pixels)
        elif self.algorithm == 'dbscan':
            colors, labels = self._cluster_colors_dbscan(pixels)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        # Calculate percentages
        percentages = self._calculate_percentages(labels)
        
        # Convert colors back to RGB if needed
        if self.lab_space:
            colors_rgb = []
            for color in colors:
                # Convert LAB to RGB
                lab_color = np.uint8([[color]])
                rgb_color = cv2.cvtColor(lab_color, cv2.COLOR_LAB2RGB)[0][0]
                colors_rgb.append(rgb_color)
            colors = np.array(colors_rgb)
        else:
            colors = colors.astype(np.uint8)
        
        # Create result
        result = []
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            result.append({
                'color': tuple(int(c) for c in color),
                'percentage': round(percentage, 2)
            })
        
        # Sort by percentage (descending)
        result.sort(key=lambda x: x['percentage'], reverse=True)
        
        return result
    
    def visualize_colors(self, colors: List[dict], save_path: Optional[str] = None):
        """Visualize extracted colors with percentages."""
        if not colors:
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 2))
        
        # Create color bar
        start = 0
        for color_info in colors:
            color = [c/255.0 for c in color_info['color']]  # Normalize for matplotlib
            percentage = color_info['percentage']
            width = percentage / 100.0
            
            ax.barh(0, width, left=start, height=0.8, color=color, 
                   edgecolor='white', linewidth=1)
            
            # Add percentage text
            if width > 0.05:  # Only show text if bar is wide enough
                ax.text(start + width/2, 0, f'{percentage:.1f}%', 
                       ha='center', va='center', fontweight='bold')
            
            start += width
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlabel('Color Distribution')
        ax.set_title('Extracted Colors with Percentages')
        ax.set_yticks([])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def _color_distance_lab(self, color1: np.ndarray, color2: np.ndarray) -> float:
        """Calculate perceptual distance between two colors in LAB space."""
        # Convert RGB to LAB
        lab1 = cv2.cvtColor(np.uint8([[color1]]), cv2.COLOR_RGB2LAB)[0][0]
        lab2 = cv2.cvtColor(np.uint8([[color2]]), cv2.COLOR_RGB2LAB)[0][0]
        
        # Calculate Euclidean distance in LAB space
        return np.sqrt(np.sum((lab1.astype(float) - lab2.astype(float)) ** 2))
    
    def _find_closest_color(self, target_color: Tuple[int, int, int], 
                          image_colors: List[dict]) -> Tuple[dict, float]:
        """Find the closest color in image to target color."""
        target_rgb = np.array(target_color)
        min_distance = float('inf')
        closest_color = None
        
        for color_info in image_colors:
            image_rgb = np.array(color_info['color'])
            distance = self._color_distance_lab(target_rgb, image_rgb)
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color_info
        
        return closest_color, min_distance
    
    def analyze_color_similarity(self, image: Union[str, np.ndarray], 
                               target_colors: Dict[str, Tuple[int, int, int]],
                               mask: Optional[Union[str, np.ndarray]] = None,
                               similarity_threshold: float = 50.0) -> Dict[str, dict]:
        """
        Analyze how much each target color appears in the image.
        
        Args:
            image: Path to image file or numpy array
            target_colors: Dictionary of color names and RGB values
                          e.g., {'red': (255, 0, 0), 'white': (255, 255, 255)}
            mask: Optional mask image
            similarity_threshold: Maximum LAB distance to consider colors similar
            
        Returns:
            Dictionary with color analysis results
        """
        # Extract dominant colors from image
        image_colors = self.extract_colors(image, mask)
        
        if not image_colors:
            return {}
        
        # Analyze each target color
        results = {}
        
        for color_name, target_rgb in target_colors.items():
            closest_color, distance = self._find_closest_color(target_rgb, image_colors)
            
            # Calculate similarity percentage (inverse of distance)
            if distance <= similarity_threshold:
                # Scale similarity: 0 distance = 100% similarity
                similarity = max(0, (similarity_threshold - distance) / similarity_threshold * 100)
                percentage = closest_color['percentage'] * (similarity / 100)
            else:
                # Color not similar enough
                similarity = 0
                percentage = 0
            
            results[color_name] = {
                'percentage': round(percentage, 2),
                'similarity': round(similarity, 2),
                'closest_color': closest_color['color'],
                'distance': round(distance, 2),
                'found_directly': bool(distance < 10.0)  # Very close match
            }
        
        return results
    
    def find_color_matches(self, image: Union[str, np.ndarray], 
                          target_colors: Dict[str, Tuple[int, int, int]],
                          mask: Optional[Union[str, np.ndarray]] = None) -> Dict[str, dict]:
        """
        Find how much each target color appears in the image with detailed analysis.
        
        Args:
            image: Path to image file or numpy array
            target_colors: Dictionary of color names and RGB values
            mask: Optional mask image
            
        Returns:
            Dictionary with detailed color matching results
        """
        # Get all pixels from the image
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise ValueError(f"Could not load image from {image}")
        
        # Apply preprocessing
        processed_image = self._preprocess_image(image)
        feature_image = self._convert_to_feature_space(processed_image)
        
        # Extract pixels
        pixels = self._extract_pixels(feature_image, mask)
        
        if len(pixels) == 0:
            return {}
        
        # Convert pixels to RGB for analysis
        if self.lab_space:
            pixels_rgb = []
            for pixel in pixels:
                lab_pixel = np.uint8([[pixel]])
                rgb_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2RGB)[0][0]
                pixels_rgb.append(rgb_pixel)
            pixels_rgb = np.array(pixels_rgb)
        else:
            pixels_rgb = pixels
        
        # Analyze each target color
        results = {}
        total_pixels = len(pixels_rgb)
        
        for color_name, target_rgb in target_colors.items():
            target_array = np.array(target_rgb)
            
            # Calculate distances from all pixels to target color
            distances = []
            for pixel in pixels_rgb:
                distance = self._color_distance_lab(target_array, pixel)
                distances.append(distance)
            
            distances = np.array(distances)
            
            # Find pixels within different similarity thresholds
            very_close = np.sum(distances < 15)    # Very similar
            close = np.sum(distances < 30)         # Similar
            somewhat_close = np.sum(distances < 50) # Somewhat similar
            
            # Calculate percentages
            very_close_pct = (very_close / total_pixels) * 100
            close_pct = (close / total_pixels) * 100
            somewhat_close_pct = (somewhat_close / total_pixels) * 100
            
            # Find the closest pixel
            closest_idx = np.argmin(distances)
            closest_pixel = pixels_rgb[closest_idx]
            min_distance = distances[closest_idx]
            
            results[color_name] = {
                'total_percentage': round(somewhat_close_pct, 2),
                'close_percentage': round(close_pct, 2),
                'very_close_percentage': round(very_close_pct, 2),
                'closest_pixel': tuple(int(c) for c in closest_pixel),
                'min_distance': round(min_distance, 2),
                'similarity_score': round(max(0, (50 - min_distance) / 50 * 100), 2)
            }
        
        return results