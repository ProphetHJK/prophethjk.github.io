import os
from PIL import Image

def compress_image(image_path, max_size_kb=500, quality_step=5):
    max_size = max_size_kb * 1024  # 转换为字节
    img = Image.open(image_path)
    
    # 如果文件已经小于 500KB，则跳过
    if os.path.getsize(image_path) <= max_size:
        print(f"跳过: {image_path} (已小于 {max_size_kb}KB)")
        return None
    
    # 确保是 RGB 模式（避免 PNG RGBA 影响压缩）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    quality = 95  # 初始质量
    temp_path = image_path + ".temp.jpg"  # 临时文件路径
    
    while quality > 10:
        img.save(temp_path, "WEBP", quality=quality)
        if os.path.getsize(temp_path) <= max_size:
            break  # 达到目标大小
        quality -= quality_step
    
    # 替换原文件
    print(f"压缩完成: {image_path} (质量 {quality})")
    return temp_path

def replace_image(src_img,dst_img):
    os.replace(src_img, dst_img)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_path = os.path.join(root, file)
                temp_path = compress_image(image_path)
                if temp_path != None:
                    replace_image(temp_path, image_path)

if __name__ == "__main__":
    dir_path = os.getcwd()  # 直接使用当前目录
    process_directory(dir_path)
    print("所有图片处理完成。")
