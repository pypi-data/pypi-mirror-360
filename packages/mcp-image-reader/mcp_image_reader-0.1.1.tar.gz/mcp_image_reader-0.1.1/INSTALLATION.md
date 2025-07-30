# Hướng dẫn cài đặt MCP Image Reader Server

## Yêu cầu hệ thống

### 1. Python 3.8+
```bash
python3 --version
```

### 2. Tesseract OCR

#### macOS:
```bash
brew install tesseract
# Cài thêm ngôn ngữ tiếng Việt
brew install tesseract-lang
```

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

#### Windows:
1. Tải Tesseract từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Cài đặt và thêm vào PATH
3. Tải language packs cho tiếng Việt

## Cài đặt tự động

```bash
# Clone hoặc tải về source code
cd mcp-image-reader

# Chạy script cài đặt
./install.sh
```

## Cài đặt thủ công

### 1. Tạo virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
venv\Scripts\activate     # Windows
```

### 2. Cài đặt dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Cài đặt package
```bash
pip install -e .
```

## Kiểm tra cài đặt

```bash
# Test các chức năng cơ bản
python test_server.py

# Test chạy server
python -m mcp_image_reader.server
```

## Cấu hình MCP Client

### Claude Desktop (macOS)
Thêm vào file `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "image-reader": {
      "command": "python",
      "args": ["-m", "mcp_image_reader.server"],
      "cwd": "/path/to/mcp-image-reader",
      "env": {
        "PATH": "/path/to/mcp-image-reader/venv/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### Claude Desktop (Windows)
Thêm vào file `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "image-reader": {
      "command": "python",
      "args": ["-m", "mcp_image_reader.server"],
      "cwd": "C:\\path\\to\\mcp-image-reader",
      "env": {
        "PATH": "C:\\path\\to\\mcp-image-reader\\venv\\Scripts;C:\\Windows\\System32"
      }
    }
  }
}
```

### Cline (VS Code)
Thêm vào settings.json của Cline:

```json
{
  "cline.mcpServers": {
    "image-reader": {
      "command": "python",
      "args": ["-m", "mcp_image_reader.server"],
      "cwd": "/path/to/mcp-image-reader",
      "env": {
        "VIRTUAL_ENV": "/path/to/mcp-image-reader/venv"
      }
    }
  }
}
```

## Xử lý sự cố

### Lỗi "tesseract not found"
```bash
# Kiểm tra Tesseract đã cài đặt
tesseract --version

# Kiểm tra ngôn ngữ có sẵn
tesseract --list-langs

# Nếu thiếu tiếng Việt, cài thêm:
# macOS
brew install tesseract-lang

# Ubuntu
sudo apt-get install tesseract-ocr-vie
```

### Lỗi "No module named cv2"
```bash
# Cài đặt lại OpenCV
pip uninstall opencv-python
pip install opencv-python
```

### Lỗi "Permission denied"
```bash
# Đảm bảo script có quyền thực thi
chmod +x install.sh
chmod +x test_server.py
```

### Lỗi "MCP server not responding"
1. Kiểm tra đường dẫn trong config
2. Đảm bảo virtual environment được kích hoạt
3. Test server độc lập:
   ```bash
   cd /path/to/mcp-image-reader
   source venv/bin/activate
   python -m mcp_image_reader.server
   ```

## Kiểm tra hoạt động

### 1. Test cơ bản
```bash
python test_server.py
```

### 2. Test với ảnh thực
Tạo file test_real_image.py:

```python
import asyncio
from mcp_image_reader.image_processor import ImageProcessor

async def test_real_image():
    processor = ImageProcessor()
    
    # Thay đường dẫn bằng ảnh thực của bạn
    image_path = "/path/to/your/image.jpg"
    
    try:
        image = processor.load_image(image_path)
        result = processor.extract_text(image, language="vie+eng")
        print(f"Text extracted: {result['text']}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_real_image())
```

### 3. Test với MCP client
Sử dụng các công cụ trong Claude Desktop hoặc Cline để test:

```
Hãy đọc text từ ảnh này: /path/to/image.png
```

## Cập nhật

```bash
cd mcp-image-reader
git pull  # nếu sử dụng git
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## Gỡ cài đặt

```bash
# Xóa virtual environment
rm -rf venv

# Xóa thư mục project
cd ..
rm -rf mcp-image-reader
```
