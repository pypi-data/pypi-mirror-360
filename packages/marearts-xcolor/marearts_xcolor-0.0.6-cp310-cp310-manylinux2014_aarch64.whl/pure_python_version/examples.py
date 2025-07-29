#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import Image
from color_extractor import ColorExtractor

try:
    import requests
    from io import BytesIO
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def example_1_file_paths():
    """Example 1: Loading from file paths (original method)"""
    print("Example 1: File paths")
    print("-" * 30)
    
    extractor = ColorExtractor(n_colors=5)
    
    # Basic file path
    colors = extractor.extract_colors('sample_image.jpg')
    print(f"Colors from file: {len(colors)} colors found")
    
    # With mask
    colors_masked = extractor.extract_colors('sample_image.jpg', 'sample_mask.jpg')
    print(f"Colors with mask: {len(colors_masked)} colors found")
    print()


def example_2_opencv_images():
    """Example 2: Using OpenCV cv2.imread() images"""
    print("Example 2: OpenCV images")
    print("-" * 30)
    
    # Load image with OpenCV
    image = cv2.imread('sample_image.jpg')
    mask = cv2.imread('sample_mask.jpg')
    
    if image is not None:
        extractor = ColorExtractor(n_colors=5)
        
        # Pass numpy arrays directly
        colors = extractor.extract_colors(image)
        print(f"Colors from cv2 image: {len(colors)} colors found")
        
        # With mask
        if mask is not None:
            colors_masked = extractor.extract_colors(image, mask)
            print(f"Colors with cv2 mask: {len(colors_masked)} colors found")
        
        # Show first few colors
        for i, color_info in enumerate(colors[:3]):
            print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
    print()


def example_3_pil_images():
    """Example 3: Using PIL/Pillow images"""
    print("Example 3: PIL/Pillow images")
    print("-" * 30)
    
    # Load image with PIL
    try:
        pil_image = Image.open('sample_image.jpg')
        pil_mask = Image.open('sample_mask.jpg')
        
        # Convert PIL to numpy array (RGB format)
        image_array = np.array(pil_image)
        mask_array = np.array(pil_mask)
        
        # Convert RGB to BGR for OpenCV compatibility
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        extractor = ColorExtractor(n_colors=5)
        
        # Extract colors from PIL-loaded image
        colors = extractor.extract_colors(image_array)
        print(f"Colors from PIL image: {len(colors)} colors found")
        
        # With mask
        colors_masked = extractor.extract_colors(image_array, mask_array)
        print(f"Colors with PIL mask: {len(colors_masked)} colors found")
        
        # Show first few colors
        for i, color_info in enumerate(colors[:3]):
            print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
    except Exception as e:
        print(f"PIL example failed: {e}")
    print()


def example_4_numpy_arrays():
    """Example 4: Creating images from numpy arrays"""
    print("Example 4: Numpy arrays")
    print("-" * 30)
    
    # Create synthetic image with numpy
    height, width = 200, 200
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add colored regions
    image[0:100, 0:100] = [255, 0, 0]      # Red
    image[0:100, 100:200] = [0, 255, 0]    # Green
    image[100:200, 0:100] = [0, 0, 255]    # Blue
    image[100:200, 100:200] = [255, 255, 0] # Yellow
    
    # Create circular mask
    mask = np.zeros((height, width), dtype=np.uint8)
    center = (width//2, height//2)
    radius = 80
    cv2.circle(mask, center, radius, 255, -1)
    
    extractor = ColorExtractor(n_colors=4)
    
    # Extract from numpy array
    colors = extractor.extract_colors(image)
    print(f"Colors from numpy image: {len(colors)} colors found")
    
    # With numpy mask
    colors_masked = extractor.extract_colors(image, mask)
    print(f"Colors with numpy mask: {len(colors_masked)} colors found")
    
    # Show results
    for i, color_info in enumerate(colors):
        print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
    print()


def example_5_webcam_capture():
    """Example 5: Real-time webcam capture"""
    print("Example 5: Webcam capture")
    print("-" * 30)
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Webcam not available")
        return
    
    extractor = ColorExtractor(n_colors=3, preprocessing=False)  # Fast for real-time
    
    print("Press 'q' to quit, 'c' to capture and analyze colors")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Show frame
        cv2.imshow('Webcam', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Capture and analyze current frame
            colors = extractor.extract_colors(frame)
            print(f"Captured frame colors: {len(colors)} colors found")
            for i, color_info in enumerate(colors):
                print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
    
    cap.release()
    cv2.destroyAllWindows()
    print()


def example_6_url_images():
    """Example 6: Loading images from URLs"""
    print("Example 6: URL images")
    print("-" * 30)
    
    if not REQUESTS_AVAILABLE:
        print("requests module not available, skipping URL example")
        print("Install with: pip install requests")
        print()
        return
    
    # Example URL (replace with actual image URL)
    url = "https://via.placeholder.com/300x200/ff0000/ffffff?text=Red+Image"
    
    try:
        # Download image
        response = requests.get(url)
        if response.status_code == 200:
            # Load with PIL
            pil_image = Image.open(BytesIO(response.content))
            
            # Convert to numpy array
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            extractor = ColorExtractor(n_colors=5)
            colors = extractor.extract_colors(image_array)
            
            print(f"Colors from URL image: {len(colors)} colors found")
            for i, color_info in enumerate(colors[:3]):
                print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
        else:
            print(f"Failed to download image: {response.status_code}")
    except Exception as e:
        print(f"URL example failed: {e}")
    print()


def example_7_video_frames():
    """Example 7: Extracting colors from video frames"""
    print("Example 7: Video frames")
    print("-" * 30)
    
    # Create a simple test video or use existing video file
    # For demo, we'll create frames programmatically
    
    extractor = ColorExtractor(n_colors=3, preprocessing=False)
    
    # Simulate video frames
    for frame_num in range(3):
        # Create different colored frames
        frame = np.zeros((300, 400, 3), dtype=np.uint8)
        
        if frame_num == 0:
            frame[:, :] = [255, 0, 0]  # Red frame
        elif frame_num == 1:
            frame[:, :] = [0, 255, 0]  # Green frame
        else:
            frame[:, :] = [0, 0, 255]  # Blue frame
        
        # Add some noise
        noise = np.random.randint(0, 50, frame.shape, dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        # Extract colors
        colors = extractor.extract_colors(frame)
        
        print(f"Frame {frame_num + 1} colors: {len(colors)} colors found")
        for i, color_info in enumerate(colors):
            print(f"  Color {i+1}: RGB{color_info['color']} - {color_info['percentage']:.1f}%")
    print()


def example_8_batch_processing():
    """Example 8: Batch processing multiple images"""
    print("Example 8: Batch processing")
    print("-" * 30)
    
    # Create sample images
    sample_images = []
    for i in range(3):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        # Different colors for each image
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        img[:, :] = colors[i]
        sample_images.append(img)
    
    extractor = ColorExtractor(n_colors=2)
    
    # Process batch
    all_results = []
    for i, image in enumerate(sample_images):
        colors = extractor.extract_colors(image)
        all_results.append(colors)
        print(f"Image {i+1}: {len(colors)} colors found")
    
    print(f"Processed {len(all_results)} images in batch")
    print()


def example_9_mixed_inputs():
    """Example 9: Mixed input types in one function"""
    print("Example 9: Mixed input types")
    print("-" * 30)
    
    extractor = ColorExtractor(n_colors=3)
    
    # Test different input types
    inputs = [
        ('File path', 'sample_image.jpg'),
        ('OpenCV image', cv2.imread('sample_image.jpg')),
        ('PIL image', np.array(Image.open('sample_image.jpg'))),
        ('Numpy array', np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    ]
    
    for input_type, image_data in inputs:
        try:
            if isinstance(image_data, str):
                # File path
                colors = extractor.extract_colors(image_data)
            elif isinstance(image_data, np.ndarray):
                # Numpy array
                if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                    # Convert RGB to BGR if needed (for PIL images)
                    if input_type == 'PIL image':
                        image_data = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
                colors = extractor.extract_colors(image_data)
            else:
                continue
            
            print(f"{input_type}: {len(colors)} colors found")
        except Exception as e:
            print(f"{input_type}: Failed - {e}")
    print()


def main():
    """Run all examples"""
    print("MareArts XColor - Examples")
    print("=" * 50)
    
    # Create sample image if it doesn't exist
    if not cv2.imread('sample_image.jpg') is not None:
        print("Creating sample images...")
        sample_image = np.zeros((300, 300, 3), dtype=np.uint8)
        sample_image[0:150, 0:150] = [255, 0, 0]    # Red
        sample_image[0:150, 150:300] = [0, 255, 0]  # Green
        sample_image[150:300, 0:150] = [0, 0, 255]  # Blue
        sample_image[150:300, 150:300] = [255, 255, 0]  # Yellow
        cv2.imwrite('sample_image.jpg', sample_image)
        
        # Create mask
        mask = np.ones((300, 300), dtype=np.uint8) * 255
        mask[200:300, 200:300] = 0  # Exclude bottom-right corner
        cv2.imwrite('sample_mask.jpg', mask)
    
    # Run examples
    example_1_file_paths()
    example_2_opencv_images()
    example_3_pil_images()
    example_4_numpy_arrays()
    example_6_url_images()
    example_7_video_frames()
    example_8_batch_processing()
    example_9_mixed_inputs()
    
    # Skip webcam example in batch mode
    print("Note: Webcam example (5) skipped in batch mode")
    print("Run example_5_webcam_capture() separately for webcam testing")


if __name__ == "__main__":
    main()