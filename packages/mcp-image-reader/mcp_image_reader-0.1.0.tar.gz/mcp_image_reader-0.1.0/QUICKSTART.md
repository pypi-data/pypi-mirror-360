# 🚀 Quick Start - MCP Image Reader Server

## Cài đặt nhanh (5 phút)

### 1. Cài đặt Tesseract OCR
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian  
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### 2. Cài đặt MCP Server
```bash
# Clone hoặc tải về source code
cd mcp-image-reader

# Chạy script cài đặt
./install.sh

# Hoặc cài đặt thủ công
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Test hoạt động
```bash
# Test cơ bản
python test_server.py

# Demo đầy đủ
python demo.py
```

## Cấu hình MCP Client

### Claude Desktop
Thêm vào `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cline (VS Code)
Thêm vào Cline settings:

```json
{
  "cline.mcpServers": {
    "image-reader": {
      "command": "python",
      "args": ["-m", "mcp_image_reader.server"],
      "cwd": "/path/to/mcp-image-reader"
    }
  }
}
```

## Sử dụng ngay

### 1. Đọc text từ ảnh
```
Hãy đọc text từ ảnh này: /path/to/document.jpg
```

### 2. Phân tích bảng
```
Trích xuất dữ liệu từ bảng trong ảnh: /path/to/table.png
```

### 3. Mô tả ảnh
```
Mô tả nội dung của ảnh này: /path/to/image.jpg
```

### 4. Phát hiện đối tượng
```
Phân tích các đối tượng trong sơ đồ: /path/to/diagram.png
```

## Các công cụ có sẵn

| Công cụ | Mô tả | Ví dụ sử dụng |
|---------|-------|---------------|
| `read_image_text` | Đọc text từ ảnh | OCR tài liệu scan |
| `analyze_image_table` | Phân tích bảng | Trích xuất dữ liệu Excel |
| `describe_image` | Mô tả ảnh | Phân tích nội dung tổng quát |
| `detect_objects` | Phát hiện đối tượng | Phân tích sơ đồ |
| `preprocess_image` | Xử lý ảnh | Cải thiện chất lượng OCR |
| `get_image_info` | Thông tin ảnh | Kiểm tra thuộc tính file |

## Định dạng ảnh hỗ trợ

✅ PNG, JPG, JPEG, BMP, TIFF, GIF, WebP

## Ngôn ngữ OCR

- `eng` - Tiếng Anh
- `vie` - Tiếng Việt  
- `vie+eng` - Kết hợp (khuyến nghị)

## Tips sử dụng hiệu quả

### 🎯 Để có kết quả OCR tốt nhất:
- Sử dụng ảnh có độ phân giải cao
- Đảm bảo text rõ nét, không bị mờ
- Sử dụng `preprocess: true` cho ảnh chất lượng kém
- Chọn ngôn ngữ phù hợp (`vie+eng` cho văn bản hỗn hợp)

### 📊 Để phân tích bảng hiệu quả:
- Bảng có đường viền rõ ràng cho kết quả tốt nhất
- Sử dụng `output_format: "json"` để xử lý dữ liệu
- Kiểm tra `confidence` score để đánh giá độ tin cậy

### 🖼️ Để mô tả ảnh chi tiết:
- Bật `include_text: true` và `include_tables: true`
- Kết hợp với các công cụ khác để phân tích sâu hơn

## Xử lý sự cố nhanh

### ❌ "tesseract not found"
```bash
# Kiểm tra cài đặt
tesseract --version
tesseract --list-langs

# Cài đặt lại nếu cần
brew reinstall tesseract tesseract-lang  # macOS
```

### ❌ "No module named cv2"
```bash
source venv/bin/activate
pip install opencv-python --force-reinstall
```

### ❌ "MCP server not responding"
```bash
# Test server độc lập
cd /path/to/mcp-image-reader
source venv/bin/activate
python -m mcp_image_reader.server
```

### ❌ Kết quả OCR kém
- Thử `preprocess_image` trước
- Kiểm tra chất lượng ảnh gốc
- Sử dụng ngôn ngữ OCR phù hợp

## Ví dụ thực tế

### 📄 Xử lý hóa đơn
```
Đọc thông tin từ hóa đơn này và trích xuất: tên công ty, số tiền, ngày tháng
[Đính kèm ảnh hóa đơn]
```

### 📊 Phân tích báo cáo
```
Trích xuất dữ liệu từ bảng trong báo cáo này thành format CSV
[Đính kèm ảnh báo cáo]
```

### 📈 Mô tả biểu đồ
```
Mô tả biểu đồ này và giải thích các thông tin chính
[Đính kèm ảnh biểu đồ]
```

## Tài liệu chi tiết

- 📖 [README.md](README.md) - Tổng quan
- 🔧 [INSTALLATION.md](INSTALLATION.md) - Hướng dẫn cài đặt chi tiết
- 💡 [examples.md](examples.md) - Ví dụ sử dụng
- 📋 [SUMMARY.md](SUMMARY.md) - Tóm tắt kỹ thuật

## Hỗ trợ

- 🐛 Báo lỗi: Tạo issue trên GitHub
- 💬 Thảo luận: GitHub Discussions
- 📧 Email: [your-email@example.com]

---

**🎉 Chúc bạn sử dụng MCP Image Reader Server hiệu quả!**
