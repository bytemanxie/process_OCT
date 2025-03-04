import os
import re
from PIL import Image
import glob

def concat_images_with_same_prefix(input_dir):
    # Get all images
    image_files = glob.glob(os.path.join(input_dir, '*.png'))
    
    # Group images by timestamp prefix
    prefix_groups = {}
    for img_path in image_files:
        basename = os.path.basename(img_path)
        # Extract the timestamp prefix (e.g., '05-1_1_12-03-15-26-16')
        match = re.match(r'([\d-]+_\d+_[\d-]+-[\d-]+-[\d-]+)_res_processed', basename)
        if match:
            prefix = match.group(1)
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(img_path)
    
    # Sort images within each group by resolution
    for prefix in prefix_groups:
        prefix_groups[prefix].sort(key=lambda x: int(re.search(r'x(\d+)', x).group(1)) if re.search(r'x(\d+)', x) else 0)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(input_dir), 'concatenated_enhanced')
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each group
    for prefix, image_paths in prefix_groups.items():
        if not image_paths:
            continue
            
        # Open all images
        images = [Image.open(path) for path in image_paths]
        
        # Get dimensions
        max_height = max(img.height for img in images)
        total_width = sum(img.width for img in images)
        
        # Create new image
        combined = Image.new('RGB', (total_width, max_height))
        
        # Paste images
        x_offset = 0
        for img in images:
            # Calculate vertical position to center the image
            y_offset = (max_height - img.height) // 2
            combined.paste(img, (x_offset, y_offset))
            x_offset += img.width
            img.close()
        
        # Save combined image
        output_path = os.path.join(output_dir, f'{prefix}_combined.png')
        combined.save(output_path)
        combined.close()
        
        print(f'Concatenated {len(image_paths)} images with prefix {prefix}')

if __name__ == '__main__':
    input_dir = os.path.join(os.path.dirname(__file__), 'enhanced_images')
    concat_images_with_same_prefix(input_dir)
