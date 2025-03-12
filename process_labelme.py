import json
import numpy as np
from PIL import Image, ImageDraw
import os
from pathlib import Path
import cv2

def load_labelme_json(json_path):
    """加载LabelMe的JSON文件"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def create_mask(shapes, img_size):
    """根据标注创建mask"""
    mask = Image.new('L', img_size, 0)
    draw = ImageDraw.Draw(mask)
    
    for shape in shapes:
        points = shape['points']
        if shape['shape_type'] == 'polygon':
            # 处理多边形标注
            draw.polygon([tuple(map(int, p)) for p in points], fill=255)
        elif shape['shape_type'] == 'linestrip':
            # 处理线段标注
            for i in range(len(points)-1):
                p1 = tuple(map(int, points[i]))
                p2 = tuple(map(int, points[i+1]))
                draw.line([p1, p2], fill=255, width=3)
    
    return np.array(mask)

def visualize_annotation(image, mask, output_dir):
    """可视化标注效果"""
    # 创建输出目录
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 在原图上显示标注
    overlay = image.copy()
    mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    mask_rgb[mask > 0] = [0, 0, 255]  # 红色标注
    cv2.addWeighted(mask_rgb, 0.5, overlay, 0.5, 0, overlay)
    
    # 保存结果
    image_name = Path(output_dir) / "annotation_on_image.png"
    blank_name = Path(output_dir) / "annotation_on_blank.png"
    
    cv2.imwrite(str(image_name), overlay)
    cv2.imwrite(str(blank_name), mask_rgb)
    
    return overlay, mask_rgb

def split_image_and_mask(image, mask, tile_size=512, overlap=0):
    """将图像和mask切分成小块"""
    h, w = image.shape[:2]
    tiles_img = []
    tiles_mask = []
    positions = []
    
    for y in range(0, h-overlap, tile_size-overlap):
        for x in range(0, w-overlap, tile_size-overlap):
            x1 = x
            y1 = y
            x2 = min(x + tile_size, w)
            y2 = min(y + tile_size, h)
            
            # 如果是图像边缘的小块，调整起始位置确保大小一致
            if x2 - x1 < tile_size:
                x1 = max(0, x2 - tile_size)
            if y2 - y1 < tile_size:
                y1 = max(0, y2 - tile_size)
            
            tile_img = image[y1:y2, x1:x2]
            tile_mask = mask[y1:y2, x1:x2]
            
            # 确保所有切片大小一致
            if tile_img.shape[:2] == (tile_size, tile_size):
                tiles_img.append(tile_img)
                tiles_mask.append(tile_mask)
                positions.append((x1, y1))
    
    return tiles_img, tiles_mask, positions

def process_labelme_annotation(image_path, json_path, output_dir, tile_size=512):
    """处理单个LabelMe标注文件"""
    try:
        # 加载图像和标注
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"无法读取图像: {image_path}")
            return
        
        data = load_labelme_json(json_path)
        
        # 创建mask
        mask = create_mask(data['shapes'], (image.shape[1], image.shape[0]))
        
        # 创建输出目录
        base_name = Path(image_path).stem
        vis_dir = Path(output_dir) / 'visualization' / base_name
        vis_dir.mkdir(parents=True, exist_ok=True)
        
        # 可视化标注效果
        visualize_annotation(image, mask, vis_dir)
        
        # 切分图像和mask
        tiles_img, tiles_mask, positions = split_image_and_mask(image, mask, tile_size)
        
        # 保存切分后的图像和mask
        for idx, (tile_img, tile_mask, pos) in enumerate(zip(tiles_img, tiles_mask, positions)):
            # 只保存包含标注的图像块
            if np.max(tile_mask) > 0:
                img_name = f"{base_name}_tile_{pos[0]}_{pos[1]}.png"
                cv2.imwrite(str(Path(output_dir) / 'images' / img_name), tile_img)
                cv2.imwrite(str(Path(output_dir) / 'masks' / img_name), tile_mask)
        
        print(f"成功处理: {image_path}")
    except Exception as e:
        print(f"处理文件时出错 {image_path}: {str(e)}")

def process_directory(input_dir, output_dir, tile_size=512):
    """处理整个目录下的所有图片和对应的JSON文件"""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # 创建输出目录结构
    (output_dir / 'images').mkdir(parents=True, exist_ok=True)
    (output_dir / 'masks').mkdir(parents=True, exist_ok=True)
    (output_dir / 'visualization').mkdir(parents=True, exist_ok=True)
    
    # 获取所有PNG文件
    png_files = list(input_dir.glob('*.png'))
    processed_count = 0
    
    for png_file in png_files:
        json_file = png_file.with_suffix('.json')
        if json_file.exists():
            process_labelme_annotation(png_file, json_file, output_dir, tile_size)
            processed_count += 1
    
    print(f"\n处理完成! 共处理了 {processed_count} 个文件")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    # 使用示例
    input_dir = "/Users/xiezhijie/GML/split_512/concatenated_enhanced"
    output_dir = "dataset"
    
    process_directory(input_dir, output_dir, tile_size=512)