import os
import cv2
import numpy as np
from pathlib import Path
import re

def reassemble_tiles(tiles_dir, output_dir, tile_size=1024):
    """
    Reassemble tiles back into complete images
    
    Args:
        tiles_dir (str or Path): Directory containing the tile images
        output_dir (str or Path): Directory to save the reassembled images
        tile_size (int): Size of the square tiles (width and height)
    """
    # Convert to Path objects
    tiles_dir = Path(tiles_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all subdirectories (each corresponds to an original image)
    image_dirs = [d for d in tiles_dir.iterdir() if d.is_dir()]
    
    print(f"Found {len(image_dirs)} image directories to reassemble")
    
    # Process each image directory
    for i, img_dir in enumerate(image_dirs, 1):
        print(f"Reassembling image {i}/{len(image_dirs)}: {img_dir.name}")
        
        # Get all tile images in this directory
        tile_paths = list(img_dir.glob("*.png"))
        
        if not tile_paths:
            print(f"  No tiles found in {img_dir}")
            continue
        
        # Extract coordinates from filenames
        tile_info = []
        for tile_path in tile_paths:
            # Extract x and y coordinates from filename
            match = re.search(r'tile_x(\d+)_y(\d+)', tile_path.name)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                tile_info.append((x, y, tile_path))
        
        if not tile_info:
            print(f"  Could not parse tile coordinates in {img_dir}")
            continue
        
        # Determine the dimensions of the reassembled image
        max_x = max(x for x, _, _ in tile_info) + tile_size
        max_y = max(y for _, y, _ in tile_info) + tile_size
        
        # Create an empty image to hold the reassembled result
        # Read one tile to determine the number of channels
        sample_tile = cv2.imread(str(tile_info[0][2]))
        channels = sample_tile.shape[2] if len(sample_tile.shape) > 2 else 1
        
        if channels == 1:
            reassembled = np.zeros((max_y, max_x), dtype=np.uint8)
        else:
            reassembled = np.zeros((max_y, max_x, channels), dtype=np.uint8)
        
        # Place each tile in the correct position
        for x, y, tile_path in tile_info:
            tile = cv2.imread(str(tile_path))
            
            # Ensure the tile fits within the reassembled image
            h, w = tile.shape[:2]
            reassembled[y:y+h, x:x+w] = tile
        
        # Save the reassembled image
        output_path = output_dir / f"{img_dir.name}_reassembled.png"
        cv2.imwrite(str(output_path), reassembled)
        print(f"  Saved reassembled image: {output_path}")
    
    print("\nReassembly complete!")
    print(f"Reassembled images saved to: {output_dir}")

if __name__ == "__main__":
    # Input directory containing the enhanced tiles
    tiles_dir = "/Users/xiezhijie/GML/split_512/enhanced_tiles"
    
    # Output directory for reassembled images
    output_dir = "/Users/xiezhijie/GML/split_512/reassembled_images"
    
    # Tile size
    tile_size = 1024
    
    # Reassemble the tiles
    reassemble_tiles(tiles_dir, output_dir, tile_size)
