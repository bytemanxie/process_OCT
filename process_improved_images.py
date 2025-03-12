import os
import cv2
import numpy as np
from pathlib import Path
import re
from split_and_enhance import split_image
from reassemble_images import reassemble_tiles

def process_improved_images(input_dir, output_split_dir, output_reassembled_dir, tile_size=1024):
    """
    Process all improved enhanced images:
    1. Split them into tiles
    2. Reassemble the tiles
    
    Args:
        input_dir (str or Path): Directory containing the improved enhanced images
        output_split_dir (str or Path): Directory to save the split tiles
        output_reassembled_dir (str or Path): Directory to save the reassembled images
        tile_size (int): Size of the square tiles (width and height)
    """
    # Convert to Path objects
    input_dir = Path(input_dir)
    output_split_dir = Path(output_split_dir)
    output_reassembled_dir = Path(output_reassembled_dir)
    
    # Create output directories
    output_split_dir.mkdir(parents=True, exist_ok=True)
    output_reassembled_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG files in the input directory
    png_files = list(input_dir.glob("*_enhanced.png"))
    total_files = len(png_files)
    
    print(f"Found {total_files} improved enhanced images to process")
    
    # Process each image
    for i, img_path in enumerate(png_files, 1):
        print(f"Processing image {i}/{total_files}: {img_path.name}")
        
        # Create subdirectory for this image's tiles
        img_split_dir = output_split_dir / img_path.stem
        
        # Split the image
        tile_paths = split_image(img_path, img_split_dir, tile_size)
        print(f"  Split into {len(tile_paths)} tiles")
    
    # Reassemble the tiles
    reassemble_tiles(output_split_dir, output_reassembled_dir, tile_size)
    
    print("\nProcessing complete!")
    print(f"Split tiles saved to: {output_split_dir}")
    print(f"Reassembled images saved to: {output_reassembled_dir}")

if __name__ == "__main__":
    # Input directory containing the improved enhanced images
    input_dir = "/Users/xiezhijie/GML/split_512/improved_enhanced_images"
    
    # Output directories
    output_split_dir = "/Users/xiezhijie/GML/split_512/improved_split_tiles"
    output_reassembled_dir = "/Users/xiezhijie/GML/split_512/final_reassembled_images"
    
    # Tile size
    tile_size = 1024
    
    # Process all images
    process_improved_images(input_dir, output_split_dir, output_reassembled_dir, tile_size)
