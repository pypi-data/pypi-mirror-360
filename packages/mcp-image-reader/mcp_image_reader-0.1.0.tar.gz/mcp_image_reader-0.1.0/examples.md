# Ví dụ sử dụng MCP Image Reader Server

## 1. Đọc text từ ảnh

```json
{
  "tool": "read_image_text",
  "arguments": {
    "image_path": "/path/to/document.png",
    "language": "vie+eng",
    "preprocess": true
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "image_path": "/path/to/document.png",
  "language": "vie+eng",
  "text": "Nội dung text được trích xuất từ ảnh...",
  "statistics": {
    "total_words": 45,
    "average_confidence": 87.5,
    "word_count_by_confidence": {
      "high (>80)": 38,
      "medium (50-80)": 5,
      "low (<50)": 2
    }
  }
}
```

## 2. Phân tích bảng trong ảnh

```json
{
  "tool": "analyze_image_table",
  "arguments": {
    "image_path": "/path/to/table.png",
    "output_format": "json"
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "image_path": "/path/to/table.png",
  "table_count": 1,
  "tables": [
    {
      "id": 0,
      "bbox": {"x": 50, "y": 100, "width": 300, "height": 200},
      "text": "Tên\tTuổi\tĐịa chỉ\nNguyễn Văn A\t25\tHà Nội\nTrần Thị B\t30\tHCM",
      "data": [
        ["Tên", "Tuổi", "Địa chỉ"],
        ["Nguyễn Văn A", "25", "Hà Nội"],
        ["Trần Thị B", "30", "HCM"]
      ],
      "confidence": 85.2
    }
  ]
}
```

## 3. Mô tả nội dung ảnh

```json
{
  "tool": "describe_image",
  "arguments": {
    "image_path": "/path/to/image.jpg",
    "include_text": true,
    "include_tables": true
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "image_path": "/path/to/image.jpg",
  "description": {
    "dimensions": {"width": 800, "height": 600},
    "color_analysis": {
      "brightness": 145.5,
      "is_dark": false,
      "is_bright": false
    },
    "complexity": {
      "edge_density": 0.08,
      "is_complex": false
    },
    "text_content": {
      "has_text": true,
      "word_count": 25,
      "text_confidence": 82.1,
      "preview": "Đây là nội dung text trong ảnh..."
    },
    "tables": {
      "table_count": 0,
      "has_tables": false
    },
    "content_type": "image_with_text"
  },
  "summary": "Ảnh có kích thước 800x600 pixels, có chứa một ít text, phát hiện 25 từ."
}
```

## 4. Phát hiện đối tượng

```json
{
  "tool": "detect_objects",
  "arguments": {
    "image_path": "/path/to/diagram.png",
    "min_area": 500
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "image_path": "/path/to/diagram.png",
  "total_objects_detected": 8,
  "objects_after_filtering": 5,
  "min_area_threshold": 500,
  "objects": [
    {
      "id": 0,
      "bbox": {"x": 100, "y": 50, "width": 80, "height": 60},
      "area": 4800.0,
      "aspect_ratio": 1.33,
      "shape_type": "rectangle"
    }
  ],
  "shape_distribution": {
    "rectangle": 3,
    "circle": 1,
    "polygon": 1
  }
}
```

## 5. Tiền xử lý ảnh

```json
{
  "tool": "preprocess_image",
  "arguments": {
    "image_path": "/path/to/noisy_image.jpg",
    "output_path": "/path/to/cleaned_image.jpg",
    "enhance_contrast": true,
    "denoise": true,
    "sharpen": true
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "input_path": "/path/to/noisy_image.jpg",
  "output_path": "/path/to/cleaned_image.jpg",
  "processing_applied": {
    "enhance_contrast": true,
    "denoise": true,
    "sharpen": true
  },
  "message": "Ảnh đã được xử lý và lưu tại: /path/to/cleaned_image.jpg"
}
```

## 6. Lấy thông tin ảnh

```json
{
  "tool": "get_image_info",
  "arguments": {
    "image_path": "/path/to/image.png"
  }
}
```

**Kết quả:**
```json
{
  "success": true,
  "image_path": "/path/to/image.png",
  "file_info": {
    "size_bytes": 1048576,
    "size_mb": 1.0,
    "format": "PNG",
    "mode": "RGB"
  },
  "dimensions": {
    "width": 1920,
    "height": 1080,
    "aspect_ratio": 1.78
  },
  "supported_for_ocr": true
}
```

## Các trường hợp sử dụng thực tế

### 1. Xử lý tài liệu scan
```bash
# Đọc text từ tài liệu scan tiếng Việt
{
  "tool": "read_image_text",
  "arguments": {
    "image_path": "/Users/user/Documents/contract_scan.jpg",
    "language": "vie",
    "preprocess": true
  }
}
```

### 2. Phân tích báo cáo có bảng
```bash
# Trích xuất dữ liệu từ báo cáo Excel được chụp ảnh
{
  "tool": "analyze_image_table",
  "arguments": {
    "image_path": "/Users/user/Pictures/report_screenshot.png",
    "output_format": "csv"
  }
}
```

### 3. Mô tả sơ đồ kỹ thuật
```bash
# Phân tích và mô tả sơ đồ kiến trúc hệ thống
{
  "tool": "describe_image",
  "arguments": {
    "image_path": "/Users/user/Diagrams/system_architecture.png",
    "include_text": true,
    "include_tables": false
  }
}
```

### 4. Xử lý ảnh chất lượng kém
```bash
# Cải thiện chất lượng ảnh trước khi OCR
{
  "tool": "preprocess_image",
  "arguments": {
    "image_path": "/Users/user/Photos/blurry_document.jpg",
    "output_path": "/Users/user/Photos/enhanced_document.jpg",
    "enhance_contrast": true,
    "denoise": true,
    "sharpen": true
  }
}
```

## Tips sử dụng hiệu quả

1. **Ngôn ngữ OCR**: Sử dụng `"vie+eng"` cho văn bản tiếng Việt có lẫn tiếng Anh
2. **Tiền xử lý**: Luôn bật `preprocess: true` cho ảnh chất lượng kém
3. **Định dạng bảng**: Sử dụng `"json"` để dễ xử lý dữ liệu, `"csv"` để xuất file
4. **Kích thước đối tượng**: Điều chỉnh `min_area` để lọc nhiễu trong phát hiện đối tượng
5. **Batch processing**: Có thể gọi nhiều tools liên tiếp để phân tích toàn diện
