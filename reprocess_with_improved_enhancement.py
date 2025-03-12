import os
import cv2
import numpy as np
from pathlib import Path
from enhance_image import enhance_image

def reprocess_images(input_dir, output_dir):
    """
    Reprocess all images in the input directory using the improved enhancement algorithm
    
    Args:
        input_dir (str or Path): Directory containing the original extracted images
        output_dir (str or Path): Directory to save the reprocessed images
    """
    # Convert to Path objects
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG files in the input directory
    png_files = list(input_dir.glob("*.png"))
    total_files = len(png_files)
    
    print(f"Found {total_files} PNG files to reprocess")
    
    # Process each image
    for i, img_path in enumerate(png_files, 1):
        print(f"Processing image {i}/{total_files}: {img_path.name}")
        
        # Create output path
        output_path = output_dir / img_path.name.replace('.png', '_enhanced.png')
        
        # Enhance the image with the improved algorithm
        enhance_image(img_path, output_path)
        
        print(f"  Enhanced: {output_path}")
    
    print("\nReprocessing complete!")
    print(f"Enhanced images saved to: {output_dir}")

if __name__ == "__main__":
    # Input directory containing the extracted src.png files
    input_dir = "/Users/xiezhijie/GML/split_512/extracted_src_png"
    
    # Output directory for enhanced images
    output_dir = "/Users/xiezhijie/GML/split_512/improved_enhanced_images"
    
    # Reprocess all images with the improved enhancement
    reprocess_images(input_dir, output_dir)
