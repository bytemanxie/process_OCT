import cv2
import numpy as np
import os
from pathlib import Path

def enhance_image(image_path, output_path=None):
    # Read the image
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read the image: {image_path}")

    # Step 1: Apply initial contrast normalization
    normalized = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    # Step 2: Apply CLAHE with moderate settings to enhance local contrast
    clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(8,8))
    clahe_result = clahe.apply(normalized)
    
    # Step 3: Apply gamma correction to boost dark regions
    gamma = 0.6  # Moderate gamma to avoid overexposure
    gamma_corrected = np.array(255 * (clahe_result / 255) ** gamma, dtype=np.uint8)
    
    # Step 4: Apply bilateral filter to reduce noise while preserving edges
    filtered = cv2.bilateralFilter(gamma_corrected, 9, 75, 75)
    
    # Step 5: Create a mask for very dark regions (below threshold 80)
    very_dark_mask = cv2.threshold(filtered, 80, 255, cv2.THRESH_BINARY_INV)[1]
    
    # Create a mask for moderately dark regions (below threshold 120)
    moderately_dark_mask = cv2.threshold(filtered, 120, 255, cv2.THRESH_BINARY_INV)[1]
    
    # Create a mask for bright regions (above threshold 180)
    bright_mask = cv2.threshold(filtered, 180, 255, cv2.THRESH_BINARY)[1]
    
    # Create a mask for mid-tone regions
    mid_mask = cv2.bitwise_xor(cv2.bitwise_or(moderately_dark_mask, bright_mask), 
                               np.ones_like(moderately_dark_mask) * 255)
    
    # Dilate the masks to include surrounding areas
    kernel = np.ones((5, 5), np.uint8)
    dilated_very_dark = cv2.dilate(very_dark_mask, kernel, iterations=1)
    dilated_mid = cv2.dilate(mid_mask, kernel, iterations=1)
    
    # Step 6: Apply targeted brightness enhancement with different levels
    # Strong brightness boost for very dark regions
    very_dark_boost = cv2.add(filtered, np.ones_like(filtered) * 60)
    
    # Moderate brightness boost for mid-tone regions
    mid_boost = cv2.add(filtered, np.ones_like(filtered) * 30)
    
    # No boost for bright regions, keep them as is to avoid overexposure
    
    # Apply the boosts to their respective regions
    enhanced_very_dark = cv2.bitwise_and(very_dark_boost, very_dark_boost, mask=dilated_very_dark)
    enhanced_mid = cv2.bitwise_and(mid_boost, mid_boost, mask=dilated_mid)
    enhanced_bright = cv2.bitwise_and(filtered, filtered, mask=bright_mask)
    
    # Combine the enhanced regions
    combined = np.zeros_like(filtered)
    combined = cv2.add(combined, enhanced_very_dark)
    combined = cv2.add(combined, enhanced_mid)
    combined = cv2.add(combined, enhanced_bright)
    
    # Step 7: Apply a second CLAHE pass with conservative settings
    second_clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    second_clahe_result = second_clahe.apply(combined)
    
    # Step 8: Apply contrast stretching with controlled limits to avoid overexposure
    # Use percentiles to avoid outliers affecting the stretching
    p2 = np.percentile(second_clahe_result, 2)  # 2nd percentile for black point
    p98 = np.percentile(second_clahe_result, 98)  # 98th percentile for white point
    
    # Apply contrast stretching with controlled limits
    stretched = np.clip((second_clahe_result - p2) * (230.0 / (p98 - p2)), 0, 255).astype(np.uint8)
    
    # Step 9: Apply moderate edge enhancement
    blurred = cv2.GaussianBlur(stretched, (0, 0), 3)
    edge_enhanced = cv2.addWeighted(stretched, 1.7, blurred, -0.7, 0)
    
    # Step 10: Apply a final bilateral filter to smooth the result while preserving edges
    final_enhanced = cv2.bilateralFilter(edge_enhanced, 5, 50, 50)
    
    # Save the result if output path is provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(str(output_path), final_enhanced)
    
    return final_enhanced

def process_directory(input_dir, output_dir):
    """
    Process all images in the input directory and save enhanced versions to the output directory
    """
    # Convert string paths to Path objects
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
    
    # Counter for processed images
    processed = 0
    errors = 0
    
    # Process all images in the directory
    for img_file in input_path.iterdir():
        if img_file.suffix.lower() in image_extensions:
            try:
                # Create output path maintaining the same filename
                output_file = output_path / img_file.name
                
                # Process the image
                enhance_image(img_file, output_file)
                processed += 1
                print(f"Processed: {img_file.name}")
            
            except Exception as e:
                errors += 1
                print(f"Error processing {img_file.name}: {str(e)}")
    
    return processed, errors

if __name__ == "__main__":
    # Example usage
    input_dir = "./images"  # Replace with your input directory
    output_dir = "enhanced_images"  # Replace with your output directory
    
    try:
        processed, errors = process_directory(input_dir, output_dir)
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {processed} images")
        if errors > 0:
            print(f"Errors encountered: {errors} images")
    except Exception as e:
        print(f"Error: {e}")
