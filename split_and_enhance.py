import os
import cv2
import numpy as np
from pathlib import Path
from enhance_image import enhance_image

def split_image(image_path, output_dir, tile_size=1024, overlap=0):
    """
    Split an image into tiles of specified size
    
    Args:
        image_path (str or Path): Path to the image to split
        output_dir (str or Path): Directory to save the split tiles
        tile_size (int): Size of the square tiles (width and height)
        overlap (int): Overlap between adjacent tiles in pixels
    
    Returns:
        list: List of paths to the generated tile images
    """
    # Convert to Path objects
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return []
    
    # Get image dimensions
    h, w = img.shape[:2]
    
    # List to store paths of generated tiles
    tile_paths = []
    
    # Split the image into tiles
    for y in range(0, h-overlap, tile_size-overlap):
        for x in range(0, w-overlap, tile_size-overlap):
            # Calculate tile coordinates
            x1 = x
            y1 = y
            x2 = min(x + tile_size, w)
            y2 = min(y + tile_size, h)
            
            # If the tile is smaller than the specified size, adjust starting position
            if x2 - x1 < tile_size:
                x1 = max(0, x2 - tile_size)
            if y2 - y1 < tile_size:
                y1 = max(0, y2 - tile_size)
            
            # Extract the tile
            tile = img[y1:y2, x1:x2]
            
            # Skip if tile is not the expected size
            if tile.shape[0] != tile_size or tile.shape[1] != tile_size:
                # Pad the tile to make it the right size
                padded_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
                padded_tile[0:tile.shape[0], 0:tile.shape[1]] = tile
                tile = padded_tile
            
            # Generate output filename
            base_name = image_path.stem
            tile_name = f"{base_name}_tile_x{x1}_y{y1}.png"
            tile_path = output_dir / tile_name
            
            # Save the tile
            cv2.imwrite(str(tile_path), tile)
            tile_paths.append(tile_path)
            
    return tile_paths

def process_all_images(input_dir, output_split_dir, output_enhanced_dir, tile_size=1024):
    """
    Process all images in the input directory:
    1. Split them into tiles
    2. Enhance each tile
    
    Args:
        input_dir (str or Path): Directory containing the input images
        output_split_dir (str or Path): Directory to save the split tiles
        output_enhanced_dir (str or Path): Directory to save the enhanced tiles
        tile_size (int): Size of the square tiles (width and height)
    """
    # Convert to Path objects
    input_dir = Path(input_dir)
    output_split_dir = Path(output_split_dir)
    output_enhanced_dir = Path(output_enhanced_dir)
    
    # Create output directories
    output_split_dir.mkdir(parents=True, exist_ok=True)
    output_enhanced_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG files in the input directory
    png_files = list(input_dir.glob("*.png"))
    total_files = len(png_files)
    
    print(f"Found {total_files} PNG files to process")
    
    # Process each image
    for i, img_path in enumerate(png_files, 1):
        print(f"Processing image {i}/{total_files}: {img_path.name}")
        
        # Create subdirectory for this image's tiles
        img_split_dir = output_split_dir / img_path.stem
        img_enhanced_dir = output_enhanced_dir / img_path.stem
        
        # Split the image
        tile_paths = split_image(img_path, img_split_dir, tile_size)
        print(f"  Split into {len(tile_paths)} tiles")
        
        # Enhance each tile
        for tile_path in tile_paths:
            # Create output path for enhanced tile
            rel_path = tile_path.relative_to(output_split_dir)
            enhanced_path = output_enhanced_dir / rel_path
            
            # Create parent directory if it doesn't exist
            enhanced_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Enhance the tile
            enhance_image(tile_path, enhanced_path)
        
        print(f"  Enhanced {len(tile_paths)} tiles")
    
    print("\nProcessing complete!")
    print(f"Split tiles saved to: {output_split_dir}")
    print(f"Enhanced tiles saved to: {output_enhanced_dir}")

if __name__ == "__main__":
    # Input directory containing the extracted src.png files
    input_dir = "/Users/xiezhijie/GML/split_512/extracted_src_png"
    
    # Output directories
    output_split_dir = "/Users/xiezhijie/GML/split_512/split_tiles"
    output_enhanced_dir = "/Users/xiezhijie/GML/split_512/enhanced_tiles"
    
    # Tile size
    tile_size = 1024
    
    # Process all images
    process_all_images(input_dir, output_split_dir, output_enhanced_dir, tile_size)
