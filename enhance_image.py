import cv2
import numpy as np
import os
from pathlib import Path

def enhance_image(image_path, output_path=None):
    # Read the image
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read the image: {image_path}")

    # Apply contrast enhancement using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(img)

    # Apply edge enhancement using unsharp masking
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 3)
    edge_enhanced = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)

    # Save the result if output path is provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(str(output_path), edge_enhanced)
    
    return edge_enhanced

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
