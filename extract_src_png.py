import os
import shutil
from pathlib import Path

def extract_src_png(source_dir, output_dir, from_res=True, from_src=True):
    """
    Recursively extract all src.png files from the source directory
    and save them to the output directory with unique names based on their parent folder.
    
    Args:
        source_dir (str): Source directory to search for src.png files
        output_dir (str): Directory to save the extracted src.png files
        from_res (bool): Whether to extract src.png from 'res' directories
        from_src (bool): Whether to extract src.png from 'src' directories
    """
    # Convert to Path objects
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Counter for found files
    found_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(source_path):
        root_path = Path(root)
        
        # Check if this is a 'res' or 'src' directory
        if (from_res and root_path.name == "res") or (from_src and root_path.name == "src"):
            # Check if src.png exists in this directory
            src_png_path = root_path / "src.png"
            if src_png_path.exists():
                # Get parent folder name for unique filename
                parent_folder = root_path.parent.relative_to(source_path).as_posix().replace('/', '_')
                if parent_folder == "":
                    parent_folder = "root"
                
                # Create destination filename with directory type indicator
                dir_type = root_path.name  # 'res' or 'src'
                dest_filename = f"{parent_folder}_{dir_type}_src.png"
                dest_path = output_path / dest_filename
                
                # Copy the file
                shutil.copy2(src_png_path, dest_path)
                found_count += 1
                print(f"Extracted: {src_png_path} -> {dest_path}")
    
    print(f"\nExtraction complete! Found {found_count} src.png files.")
    return found_count

if __name__ == "__main__":
    # Source directory containing the 20250220 folder
    source_dir = "/Users/xiezhijie/GML/split_512/20250220"
    
    # Output directory for extracted src.png files
    output_dir = "/Users/xiezhijie/GML/split_512/extracted_src_png"
    
    # Extract all src.png files
    # Set from_res=True to extract from 'res' directories
    # Set from_src=True to extract from 'src' directories
    extract_src_png(source_dir, output_dir, from_res=True, from_src=True)
