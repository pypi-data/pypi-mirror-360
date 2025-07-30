"""
Stamp it - 为图片添加满屏水印
支持文字水印和图片水印
"""

import os
import io
from typing import Optional, Union, Tuple
from pathlib import Path
from fastmcp import FastMCP
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import math

# 创建 FastMCP 实例
mcp = FastMCP("Stamp it - 为图片添加满屏水印")

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

# 缓存字体实例以提高性能
_font_cache = {}

class WatermarkConfig:
    """水印配置类"""
    DEFAULT_FONT_SIZE = 36
    DEFAULT_ANGLE = 30
    SPACING_X_FACTOR = 1.1
    SPACING_Y_FACTOR = 0.9
    BRIGHTNESS_THRESHOLDS = {
        'very_bright': 180,
        'medium': 120,
        'dark': 60
    }

def is_valid_image_format(filename: str) -> bool:
    """检查文件是否为支持的图片格式"""
    return Path(filename).suffix.lower() in SUPPORTED_FORMATS

def get_filename_from_path(file_path: str) -> str:
    """从文件路径获取文件名"""
    return os.path.basename(file_path)

def read_local_image(file_path: str) -> Optional[bytes]:
    """读取本地图片文件"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except (IOError, OSError) as e:
        print(f"读取本地图片失败: {e}")
        return None

def is_local_file(path: str) -> bool:
    """检查路径是否为本地文件"""
    return os.path.isfile(path)

def calculate_average_brightness(image: Image.Image) -> float:
    """计算图片的平均亮度"""
    # 转换为灰度图计算亮度
    if image.mode != 'L':
        gray_image = image.convert('L')
    else:
        gray_image = image
    
    # 缩小图片以提高计算速度
    small_image = gray_image.resize((50, 50))
    pixels = list(small_image.getdata())
    return sum(pixels) / len(pixels)

def get_adaptive_watermark_color(average_brightness: float) -> Tuple[int, int, int, int]:
    """根据图片亮度自动选择水印颜色"""
    if average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['very_bright']:
        # 很亮的图片：使用深色水印
        return (20, 20, 20, 160)
    elif average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['medium']:
        # 中等亮度：使用中深色水印
        return (32, 32, 32, 150)
    elif average_brightness > WatermarkConfig.BRIGHTNESS_THRESHOLDS['dark']:
        # 较暗的图片：使用浅色水印
        return (200, 200, 200, 140)
    else:
        # 很暗的图片：使用白色水印
        return (240, 240, 240, 130)

def get_font(font_size: int = WatermarkConfig.DEFAULT_FONT_SIZE) -> ImageFont.FreeTypeFont:
    """获取字体，支持缓存"""
    if font_size in _font_cache:
        return _font_cache[font_size]
    
    # 字体路径优先级列表
    font_paths = [
        # macOS 中文字体
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux 字体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        # Windows 字体
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "arial.ttf",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except (IOError, OSError):
            continue
    
    # 如果所有字体都加载失败，使用默认字体
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
    
    _font_cache[font_size] = font
    return font

def create_text_watermark_layer(
    size: Tuple[int, int], 
    text: str, 
    color: Tuple[int, int, int, int],
    angle: float = WatermarkConfig.DEFAULT_ANGLE,
    font_size: int = WatermarkConfig.DEFAULT_FONT_SIZE
) -> Image.Image:
    """创建文字水印图层"""
    width, height = size
    watermark_layer = Image.new('RGBA', size, (255, 255, 255, 0))
    
    font = get_font(font_size)
    
    # 获取文本尺寸
    draw = ImageDraw.Draw(watermark_layer)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 计算水印间距
    diagonal_size = math.sqrt(text_width**2 + text_height**2)
    spacing_x = int(diagonal_size * WatermarkConfig.SPACING_X_FACTOR)
    spacing_y = int(diagonal_size * WatermarkConfig.SPACING_Y_FACTOR)
    
    # 计算网格尺寸
    cols = math.ceil(width / spacing_x) + 3
    rows = math.ceil(height / spacing_y) + 3
    
    # 起始偏移确保完整覆盖
    start_offset_y = -spacing_y // 2
    start_offset_x = -spacing_x // 2
    
    # 添加倾斜文字水印
    for row in range(rows):
        for col in range(cols):
            x = start_offset_x + col * spacing_x - (row % 2) * (spacing_x // 2)
            y = start_offset_y + row * spacing_y
            
            # 创建临时画布用于高质量旋转
            temp_size = max(text_width + 40, text_height + 40)
            temp_img = Image.new('RGBA', (temp_size, temp_size), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 居中绘制文本
            text_x = (temp_size - text_width) // 2
            text_y = (temp_size - text_height) // 2
            temp_draw.text((text_x, text_y), text, font=font, fill=color)
            
            # 高质量旋转
            rotated_text = temp_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # 贴到水印层上
            if x < width and y < height:
                watermark_layer.paste(rotated_text, (x, y), rotated_text)
    
    return watermark_layer

def create_image_watermark_layer(
    size: Tuple[int, int],
    watermark_image_path: str,
    opacity: float = 0.5,
    scale: float = 0.15,
    angle: float = WatermarkConfig.DEFAULT_ANGLE
) -> Optional[Image.Image]:
    """创建图片水印图层"""
    try:
        # 读取水印图片
        watermark_img = Image.open(watermark_image_path)
        
        # 转换为RGBA模式
        if watermark_img.mode != 'RGBA':
            watermark_img = watermark_img.convert('RGBA')
        
        # 计算缩放后的尺寸
        width, height = size
        max_size = min(width, height) * scale
        
        # 保持宽高比缩放
        w_ratio = max_size / watermark_img.width
        h_ratio = max_size / watermark_img.height
        scale_ratio = min(w_ratio, h_ratio)
        
        new_width = int(watermark_img.width * scale_ratio)
        new_height = int(watermark_img.height * scale_ratio)
        
        # 缩放水印图片
        watermark_img = watermark_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 调整透明度
        enhancer = ImageEnhance.Brightness(watermark_img)
        watermark_img = enhancer.enhance(1.0)
        
        # 创建水印层
        watermark_layer = Image.new('RGBA', size, (255, 255, 255, 0))
        
        # 计算平铺间距
        spacing_x = int(new_width * 1.5)
        spacing_y = int(new_height * 1.5)
        
        # 计算网格
        cols = math.ceil(width / spacing_x) + 2
        rows = math.ceil(height / spacing_y) + 2
        
        # 起始偏移
        start_offset_x = -spacing_x // 2
        start_offset_y = -spacing_y // 2
        
        # 平铺水印图片
        for row in range(rows):
            for col in range(cols):
                x = start_offset_x + col * spacing_x - (row % 2) * (spacing_x // 2)
                y = start_offset_y + row * spacing_y
                
                # 旋转水印图片
                if angle != 0:
                    rotated_watermark = watermark_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
                else:
                    rotated_watermark = watermark_img
                
                # 调整透明度
                alpha = rotated_watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                rotated_watermark.putalpha(alpha)
                
                # 贴到水印层上
                if x < width and y < height:
                    watermark_layer.paste(rotated_watermark, (x, y), rotated_watermark)
        
        return watermark_layer
        
    except Exception as e:
        print(f"创建图片水印失败: {e}")
        return None

def apply_watermark_to_image(
    image: Image.Image, 
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
    angle: float = WatermarkConfig.DEFAULT_ANGLE
) -> Image.Image:
    """为图片添加水印（文字或图片）"""
    # 记录原始模式以保持图片属性
    original_mode = image.mode
    
    # 转换为RGBA进行处理
    if original_mode != 'RGBA':
        image_rgba = image.convert('RGBA')
    else:
        image_rgba = image.copy()
    
    watermark_layer = None
    
    if watermark_text:
        # 文字水印
        avg_brightness = calculate_average_brightness(image)
        watermark_color = get_adaptive_watermark_color(avg_brightness)
        watermark_layer = create_text_watermark_layer(
            image.size, watermark_text, watermark_color, angle
        )
    elif watermark_image_path:
        # 图片水印
        watermark_layer = create_image_watermark_layer(
            image.size, watermark_image_path, opacity=0.6, angle=angle
        )
    
    if watermark_layer:
        # 合并水印
        watermarked = Image.alpha_composite(image_rgba, watermark_layer)
        
        # 恢复原始模式
        if original_mode == 'RGB':
            watermarked = watermarked.convert('RGB')
        elif original_mode == 'L':
            watermarked = watermarked.convert('L')
        elif original_mode == 'P':
            watermarked = watermarked.convert('P')
        
        return watermarked
    
    return image

def save_watermarked_image(image: Image.Image, original_filename: str, output_dir: str = ".") -> str:
    """保存带水印的图片"""
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 生成新文件名
    name, ext = os.path.splitext(original_filename)
    new_filename = f"{name}_watermark{ext}"
    output_path = os.path.join(output_dir, new_filename)
    
    # 根据文件扩展名处理图片格式
    if ext.lower() in ['.jpg', '.jpeg']:
        # JPEG不支持透明度，需要转换为RGB
        if image.mode == 'RGBA':
            # 创建白色背景
            bg = Image.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[-1])
            image = bg
        image.save(output_path, 'JPEG', quality=95, optimize=True)
    else:
        # 其他格式直接保存
        image.save(output_path, quality=95, optimize=True)
    
    return output_path

@mcp.tool()
def add_text_watermark(image_path: str, watermark_text: str, angle: float = 30) -> str:
    """
    为图片添加文字水印
    
    Args:
        image_path: 本地图片文件路径
        watermark_text: 水印文字内容
        angle: 水印倾斜角度（默认30度）
        
    Returns:
        处理后的图片保存路径信息
    """
    return _process_watermark(image_path, watermark_text=watermark_text, angle=angle)

@mcp.tool()
def add_image_watermark(image_path: str, watermark_image_path: str, angle: float = 30) -> str:
    """
    为图片添加图片水印
    
    Args:
        image_path: 本地图片文件路径
        watermark_image_path: 水印图片文件路径
        angle: 水印倾斜角度（默认30度）
        
    Returns:
        处理后的图片保存路径信息
    """
    # 检查水印图片是否存在
    if not is_local_file(watermark_image_path):
        return f"错误：水印图片文件不存在：{watermark_image_path}"
    
    if not is_valid_image_format(watermark_image_path):
        return f"错误：水印图片格式不支持。支持的格式：{', '.join(SUPPORTED_FORMATS)}"
    
    return _process_watermark(image_path, watermark_image_path=watermark_image_path, angle=angle)

def _process_watermark(
    image_path: str, 
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
    angle: float = 30
) -> str:
    """处理水印的通用函数"""
    # 检查文件是否存在
    if not is_local_file(image_path):
        return f"错误：文件不存在或无法访问：{image_path}"
    
    # 获取文件名
    original_filename = get_filename_from_path(image_path)
    
    # 检查是否为支持的图片格式
    if not is_valid_image_format(original_filename):
        return f"错误：不支持的图片格式。支持的格式：{', '.join(SUPPORTED_FORMATS)}"
    
    # 读取本地图片
    image_data = read_local_image(image_path)
    if not image_data:
        return "错误：无法读取本地图片文件"
    
    try:
        # 打开图片
        image = Image.open(io.BytesIO(image_data))
        
        # 添加水印
        watermarked_image = apply_watermark_to_image(
            image, 
            watermark_text=watermark_text,
            watermark_image_path=watermark_image_path,
            angle=angle
        )
        
        # 确定输出目录（保存在原文件的同一目录）
        output_dir = os.path.dirname(os.path.abspath(image_path))
        if not output_dir:
            output_dir = "."
        
        # 保存带水印的图片
        output_path = save_watermarked_image(watermarked_image, original_filename, output_dir)
        
        watermark_type = "文字" if watermark_text else "图片"
        return f"成功！{watermark_type}水印已添加，图片保存至：{output_path}"
        
    except Exception as e:
        return f"错误：处理图片时发生异常：{str(e)}"

def main():
    """主函数，用于运行MCP服务器"""
    mcp.run()

if __name__ == "__main__":
    main()