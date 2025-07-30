# 🎯 Stamp it - Apply a full-screen watermark to an image

A professional image watermarking service built with FastMCP, supporting both text and image watermarks with intelligent color adaptation.

[中文文档](README_CN.md) | English

## ✨ Key Features

- 🖼️ **Dual Watermark Modes**: Support for both text and image watermarks
- 📂 **Local File Processing**: Professional local image file handling
- 🎨 **Smart Adaptive Colors**: Automatic color selection based on image brightness
- 📐 **Tilted Watermark Effects**: Customizable angle tilting (default 30° upward right)
- 🌍 **Multi-language Support**: Chinese, English, Japanese, Korean and more
- 🎯 **High-density Coverage**: Complete coverage of every corner with no gaps
- 💎 **High Definition**: BICUBIC resampling for smooth edges
- 📁 **Smart Saving**: Auto-save in the same directory as original image
- ⚡ **Performance Optimized**: Font caching, intelligent scaling, memory management
- 🛠️ **Rich Format Support**: Supports 7 common image formats

## 🚀 Installation

### Using uv (Recommended)

```bash
# Install dependencies
uv pip install fastmcp pillow

# Or install using project configuration
uv pip install -e .
```

### Using pip

```bash
pip install fastmcp pillow
```

## 📖 Usage

### MCP Client Configuration

#### Cherry Studio (Recommended)

1. **Open Cherry Studio Settings**
   - Go to Settings → MCP Servers
   - Click "Add Server"

2. **Configure MCP Server**
   ```json
   {
     "name": "Stampit",
     "command": "python",
     "args": ["main.py"],
     "cwd": "/path/to/stampit"
   }
   ```

3. **Save and Connect**
   - Click "Save" to add the server
   - The server will automatically connect
   - You can now use the watermark tools in Cherry Studio

#### Cursor IDE

1. **Open Cursor Settings**
   - Go to Settings → Extensions → MCP
   - Or press `Cmd+,` (Mac) / `Ctrl+,` (Windows/Linux)

2. **Add MCP Configuration**
   ```json
   {
     "mcpServers": {
       "stampit": {
         "command": "python",
         "args": ["main.py"],
         "cwd": "/path/to/stampit"
       }
     }
   }
   ```

3. **Restart Cursor**
   - Restart Cursor to load the MCP server
   - The watermark tools will be available in the MCP panel

### Start the MCP Server (Standalone)

```bash
python main.py
```

After the server starts, you will see output similar to:
```
╭─ FastMCP 2.0 ────────────────────────────────────────╮
│   🖥️  Server name:     Stampit Watermark Server      │
│   📦 Transport:       STDIO                         │
╰────────────────────────────────────────────────────╯
```

### Available MCP Tools

#### `add_text_watermark` - Text Watermark

Add intelligent text watermarks to images with multi-language support and adaptive colors.

**Parameters:**
- `image_path` (str): Local image file path
- `watermark_text` (str): Watermark text content
- `angle` (float, optional): Watermark tilt angle, default 30°

**Usage Examples:**
```python
# Basic text watermark
add_text_watermark("/Users/photos/vacation.jpg", "My Copyright")

# Custom angle
add_text_watermark("./document.png", "Confidential", angle=45)

# Multi-language watermark
add_text_watermark("photo.jpg", "Copyright © 2024 All Rights Reserved")
```

#### `add_image_watermark` - Image Watermark

Add image watermarks to photos, supporting logos, signatures, and other images as watermarks.

**Parameters:**
- `image_path` (str): Local image file path
- `watermark_image_path` (str): Watermark image file path
- `angle` (float, optional): Watermark tilt angle, default 30°

**Usage Examples:**
```python
# Add logo watermark
add_image_watermark("/Users/photos/product.jpg", "/Users/logos/company_logo.png")

# Custom angle logo watermark
add_image_watermark("photo.jpg", "signature.png", angle=0)

# Brand watermark
add_image_watermark("marketing_image.jpg", "brand_watermark.png", angle=15)
```

## 🎨 Watermark Features

### 📝 Text Watermark Features

- **Smart Color Adaptation**
  - Bright images: Automatically use dark watermarks (RGB 20,20,20)
  - Dark images: Automatically use light/white watermarks (RGB 240,240,240)
  - Medium brightness: Intelligently select optimal contrast colors

- **Multi-language Font Support**
  - Auto-detect and load system's best Chinese fonts
  - Support for PingFang SC, Microsoft YaHei, SimHei, etc.
  - Perfect display of Chinese, Japanese, Korean, and English

- **High-quality Rendering**
  - Font caching for improved performance
  - BICUBIC resampling for smooth edges
  - Centered rendering with excellent rotation effects

### 🖼️ Image Watermark Features

- **Smart Scaling**: Auto-scale to appropriate size (default 15%)
- **Opacity Control**: Automatic opacity adjustment without affecting original image
- **Aspect Ratio Preservation**: Maintain watermark image aspect ratio
- **High-quality Scaling**: Use LANCZOS algorithm for clarity

### 🎯 Layout Algorithm

- **Complete Coverage**: Start from outside image boundaries for 100% coverage
- **Staggered Arrangement**: Odd-even row offset for more natural visual effect
- **Dense Distribution**: Optimized spacing algorithm, 40% higher density than traditional methods
- **Edge Handling**: Complete watermark coverage in all four corners

## 📁 File Output

### Save Rules
- **Save Location**: Auto-save in the same directory as original image
- **Naming Convention**: Original filename + `_watermark` + extension
- **Format Preservation**: Maintain original image format and quality
- **Optimized Saving**: Enable compression optimization to reduce file size

### Output Examples
```
Input:  /Users/photos/vacation.jpg
Output: /Users/photos/vacation_watermark.jpg

Input:  ./designs/logo.png
Output: ./designs/logo_watermark.png

Input:  document.pdf.png
Output: document.pdf_watermark.png
```

## 🛠️ Supported Image Formats

| Format | Extensions | Read | Save | Transparency | Optimized |
|--------|------------|------|------|--------------|-----------|
| JPEG | .jpg, .jpeg | ✅ | ✅ | ❌ | ✅ |
| PNG | .png | ✅ | ✅ | ✅ | ✅ |
| GIF | .gif | ✅ | ✅ | ✅ | ✅ |
| BMP | .bmp | ✅ | ✅ | ❌ | ✅ |
| TIFF | .tiff, .tif | ✅ | ✅ | ✅ | ✅ |
| WebP | .webp | ✅ | ✅ | ✅ | ✅ |

## 🌍 Multi-language Font Support

### Supported Languages
- **Chinese**: Simplified & Traditional Chinese
- **Japanese**: ひらがな、カタカナ、漢字
- **Korean**: 한글 (Hangul)
- **English**: Latin character set
- **Others**: Most Unicode characters

### Font Priority

**macOS System:**
1. PingFang SC (Apple's default Chinese font)
2. STHeiti Light (Chinese typography)
3. Hiragino Sans GB (Winter Blue font)
4. Arial Unicode (Universal Unicode font)

**Windows System:**
1. Microsoft YaHei
2. SimSun
3. SimHei

**Linux System:**
1. DejaVu Sans
2. Liberation Sans
3. Noto Sans CJK
4. WenQuanYi Zen Hei

## 📂 Project Structure

```
stampit/
├── main.py                   # Main program and MCP server
├── pyproject.toml            # Project configuration
├── README.md                 # English project documentation
├── README_CN.md              # Chinese project documentation
├── uv.lock                   # Dependency lock file
└── LICENSE                   # License file
```

## 🧪 Quick Testing

### Test Text Watermark
```bash
# 1. Start server
python main.py

# 2. Call in MCP client
add_text_watermark("path/to/your/image.jpg", "Test Watermark")
```

### Test Image Watermark
```bash
# 1. Prepare a logo image
# 2. Call in MCP client
add_image_watermark("path/to/your/photo.jpg", "path/to/logo.png")
```

## ⚙️ Technical Details

### Core Algorithms
- **Brightness Calculation**: Grayscale conversion + pixel average algorithm
- **Color Adaptation**: Four-tier classification system based on brightness thresholds
- **Position Calculation**: Staggered grid + edge offset algorithm
- **Rendering Optimization**: BICUBIC/LANCZOS resampling technology

### Performance Optimization
- **Font Caching**: Avoid repeated font file loading
- **Smart Scaling**: Brightness calculation using 50x50 small images for speed
- **Memory Management**: Timely release of temporary layers and cache
- **Batch Processing**: Support for efficient batch image processing

### Quality Assurance
- **Edge Smoothing**: Use high-quality resampling algorithms
- **Color Fidelity**: Preserve original image color space and mode
- **Transparency Handling**: Proper RGBA channel processing
- **Format Compatibility**: Smart conversion between different image formats

## 🔧 Advanced Configuration

You can adjust parameters by modifying the `WatermarkConfig` class:

```python
class WatermarkConfig:
    DEFAULT_FONT_SIZE = 36          # Default font size
    DEFAULT_ANGLE = 30              # Default tilt angle
    SPACING_X_FACTOR = 1.1          # Horizontal spacing multiplier
    SPACING_Y_FACTOR = 0.9          # Vertical spacing multiplier
    BRIGHTNESS_THRESHOLDS = {       # Brightness thresholds
        'very_bright': 180,
        'medium': 120,
        'dark': 60
    }
```

### Custom Parameter Suggestions
- **Dense Watermarks**: Lower spacing multipliers (0.8, 0.7)
- **Sparse Watermarks**: Higher spacing multipliers (1.5, 1.3)
- **Large Fonts**: Increase font size (48, 54)
- **Small Fonts**: Decrease font size (24, 30)

## 🎛️ Usage Tips

### Text Watermark Tips
1. **Copyright Info**: Use "© 2024 Company Name" format
2. **Multi-language**: Mixed Chinese-English works better
3. **Angle Selection**: 30° most natural, 45° more prominent, 0° for documents

### Image Watermark Tips
1. **Logo Design**: Use transparent background PNG format
2. **Size Control**: Logo shouldn't be too large, recommend within 15% of original
3. **Color Matching**: Choose logo colors with appropriate contrast to original image

## 💡 Best Practices

### Batch Processing Recommendations
```python
# Recommended batch processing method
images = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
watermark_text = "© 2024 My Company"

for image_path in images:
    result = add_text_watermark(image_path, watermark_text)
    print(result)
```

### Performance Optimization Suggestions
1. **Use same font size in batches** to leverage font caching
2. **Avoid frequent angle changes** to reduce computational overhead
3. **Use small-sized image watermarks** to improve processing speed

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Contributing Guidelines
1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## 📞 Technical Support

For questions or suggestions:
1. Submit GitHub Issues
2. Check project documentation
3. Contact development team

---

**🎉 Thank you for using Stamp it!**