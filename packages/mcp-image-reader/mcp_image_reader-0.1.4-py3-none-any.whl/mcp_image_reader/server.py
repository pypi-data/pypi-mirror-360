"""MCP Image Reader Server - Server chính."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .image_processor import ImageProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize image processor
image_processor = ImageProcessor()

# Create MCP server
server = Server("image-reader")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """Liệt kê các công cụ có sẵn."""
    return [
        Tool(
            name="read_image_text",
            description="Đọc và trích xuất text từ ảnh sử dụng OCR",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh",
                    },
                    "language": {
                        "type": "string",
                        "description": "Ngôn ngữ OCR (ví dụ: 'eng', 'vie', 'vie+eng')",
                        "default": "eng",
                    },
                    "preprocess": {
                        "type": "boolean",
                        "description": "Có tiền xử lý ảnh để cải thiện OCR không",
                        "default": True,
                    },
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="analyze_image_table",
            description="Phân tích và trích xuất dữ liệu từ bảng trong ảnh",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh chứa bảng",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Định dạng output: 'json', 'csv', 'text'",
                        "enum": ["json", "csv", "text"],
                        "default": "json",
                    },
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="detect_objects",
            description="Phát hiện và phân loại đối tượng trong ảnh",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh",
                    },
                    "min_area": {
                        "type": "number",
                        "description": "Diện tích tối thiểu của đối tượng để phát hiện",
                        "default": 100,
                    },
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="preprocess_image",
            description="Tiền xử lý ảnh để cải thiện chất lượng cho OCR",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh gốc",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Đường dẫn để lưu ảnh đã xử lý",
                    },
                    "enhance_contrast": {
                        "type": "boolean",
                        "description": "Có tăng cường độ tương phản không",
                        "default": True,
                    },
                    "denoise": {
                        "type": "boolean",
                        "description": "Có khử nhiễu không",
                        "default": True,
                    },
                    "sharpen": {
                        "type": "boolean",
                        "description": "Có làm sắc nét không",
                        "default": True,
                    },
                },
                "required": ["image_path", "output_path"],
            },
        ),
        Tool(
            name="get_image_info",
            description="Lấy thông tin cơ bản về file ảnh",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh",
                    }
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="convert_to_svg",
            description="Convert ảnh PNG/JPG sang định dạng SVG với khả năng đọc file trực tiếp",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh gốc (PNG/JPG) - có thể để trống nếu dùng image_data",
                    },
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data (thay thế cho image_path)",
                    },
                    "use_fs_read": {
                        "type": "boolean",
                        "description": "Sử dụng fs_read để đọc file thay vì đường dẫn trực tiếp",
                        "default": False,
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Đường dẫn lưu file SVG",
                    },
                    "method": {
                        "type": "string",
                        "description": "Phương pháp convert (embed, trace, hybrid)",
                        "default": "embed",
                        "enum": ["embed", "trace", "hybrid"]
                    },
                    "vectorize": {
                        "type": "boolean",
                        "description": "Có thực hiện vectorization không",
                        "default": False,
                    },
                    "max_colors": {
                        "type": "integer",
                        "description": "Số màu tối đa cho vectorization",
                        "default": 16,
                        "minimum": 2,
                        "maximum": 256
                    }
                },
                "required": ["output_path"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý các lời gọi công cụ."""
    try:
        if name == "read_image_text":
            return await handle_read_image_text(arguments)
        elif name == "analyze_image_table":
            return await handle_analyze_image_table(arguments)
        elif name == "detect_objects":
            return await handle_detect_objects(arguments)
        elif name == "preprocess_image":
            return await handle_preprocess_image(arguments)
        elif name == "get_image_info":
            return await handle_get_image_info(arguments)
        elif name == "convert_to_svg":
            return await handle_convert_to_svg(arguments)
        else:
            raise ValueError(f"Công cụ không được hỗ trợ: {name}")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý công cụ {name}: {str(e)}")
        return [TextContent(type="text", text=f"Lỗi: {str(e)}")]


async def handle_read_image_text(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý đọc text từ ảnh."""
    image_path = arguments["image_path"]
    language = arguments.get("language", "eng")
    preprocess = arguments.get("preprocess", True)

    # Load image
    image = image_processor.load_image(image_path)

    # Preprocess if requested
    if preprocess:
        image = image_processor.preprocess_image(image)

    # Extract text
    result = image_processor.extract_text(image, language)

    # Format response
    response = {
        "success": True,
        "image_path": image_path,
        "language": language,
        "text": result["text"],
        "statistics": {
            "total_words": result["total_words"],
            "average_confidence": result["average_confidence"],
            "word_count_by_confidence": {
                "high (>80)": len([w for w in result["words"] if w["confidence"] > 80]),
                "medium (50-80)": len(
                    [w for w in result["words"] if 50 <= w["confidence"] <= 80]
                ),
                "low (<50)": len([w for w in result["words"] if w["confidence"] < 50]),
            },
        },
        "words_detail": result["words"][:20],  # Limit to first 20 words for brevity
    }

    return [
        TextContent(
            type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
        )
    ]


async def handle_analyze_image_table(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý phân tích bảng từ ảnh."""
    image_path = arguments["image_path"]
    output_format = arguments.get("output_format", "json")

    # Load image
    image = image_processor.load_image(image_path)

    # Detect tables
    tables = image_processor.detect_tables(image)

    if output_format == "json":
        response = {
            "success": True,
            "image_path": image_path,
            "table_count": len(tables),
            "tables": tables,
        }
        return [
            TextContent(
                type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
            )
        ]

    elif output_format == "csv":
        csv_content = ""
        for i, table in enumerate(tables):
            csv_content += f"# Bảng {i+1}\n"
            for row in table["data"]:
                csv_content += ",".join(row) + "\n"
            csv_content += "\n"
        return [TextContent(type="text", text=csv_content)]

    else:  # text format
        text_content = f"Phát hiện {len(tables)} bảng trong ảnh:\n\n"
        for i, table in enumerate(tables):
            text_content += f"Bảng {i+1}:\n"
            text_content += table["text"] + "\n\n"
        return [TextContent(type="text", text=text_content)]


async def handle_detect_objects(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý phát hiện đối tượng."""
    image_path = arguments["image_path"]
    min_area = arguments.get("min_area", 100)

    # Load image
    image = image_processor.load_image(image_path)

    # Detect objects
    objects_info = image_processor.detect_objects(image)

    # Filter by minimum area
    filtered_objects = [
        obj for obj in objects_info["objects"] if obj["area"] >= min_area
    ]

    response = {
        "success": True,
        "image_path": image_path,
        "total_objects_detected": objects_info["object_count"],
        "objects_after_filtering": len(filtered_objects),
        "min_area_threshold": min_area,
        "objects": filtered_objects,
        "shape_distribution": get_shape_distribution(filtered_objects),
    }

    return [
        TextContent(
            type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
        )
    ]


async def handle_preprocess_image(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý tiền xử lý ảnh."""
    image_path = arguments["image_path"]
    output_path = arguments["output_path"]
    enhance_contrast = arguments.get("enhance_contrast", True)
    denoise = arguments.get("denoise", True)
    sharpen = arguments.get("sharpen", True)

    # Load image
    image = image_processor.load_image(image_path)

    # Preprocess
    processed_image = image_processor.preprocess_image(
        image, enhance_contrast, denoise, sharpen
    )

    # Save processed image
    processed_image.save(output_path)

    response = {
        "success": True,
        "input_path": image_path,
        "output_path": output_path,
        "processing_applied": {
            "enhance_contrast": enhance_contrast,
            "denoise": denoise,
            "sharpen": sharpen,
        },
        "message": f"Ảnh đã được xử lý và lưu tại: {output_path}",
    }

    return [
        TextContent(
            type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
        )
    ]


async def handle_get_image_info(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý lấy thông tin ảnh."""
    image_path = arguments["image_path"]

    # Load image
    image = image_processor.load_image(image_path)

    # Get basic info
    import os

    file_size = os.path.getsize(image_path)

    response = {
        "success": True,
        "image_path": image_path,
        "file_info": {
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "format": image.format,
            "mode": image.mode,
        },
        "dimensions": {
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 2),
        },
        "supported_for_ocr": image_processor.is_supported_format(image_path),
    }

    return [
        TextContent(
            type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
        )
    ]


def get_shape_distribution(objects: List[Dict[str, Any]]) -> Dict[str, int]:
    """Lấy phân bố hình dạng của các đối tượng."""
    distribution = {}
    for obj in objects:
        shape = obj["shape_type"]
        distribution[shape] = distribution.get(shape, 0) + 1
    return distribution


async def handle_convert_to_svg(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý convert ảnh sang SVG với fs_read integration."""
    image_path = arguments.get("image_path")
    image_data = arguments.get("image_data")
    use_fs_read = arguments.get("use_fs_read", False)
    output_path = arguments["output_path"]
    method = arguments.get("method", "embed")
    vectorize = arguments.get("vectorize", False)
    max_colors = arguments.get("max_colors", 16)

    # Validate input - cần ít nhất một trong các input methods
    if not image_path and not image_data:
        raise ValueError("Cần cung cấp image_path hoặc image_data")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Load image using different methods
    image = None
    input_info = {}
    
    try:
        if image_data:
            # Method 1: Load from base64 data
            image = image_processor.load_image_from_base64(image_data)
            input_info = {
                "source": "base64_data",
                "data_length": len(image_data),
                "method": "direct_base64"
            }
            
        elif use_fs_read and image_path:
            # Method 2: Use fs_read to read file as bytes first
            image_bytes = image_processor.fs_read_image(image_path)
            image = image_processor.load_image_from_bytes(image_bytes)
            input_info = {
                "source": "fs_read",
                "file_path": image_path,
                "file_size": len(image_bytes),
                "method": "fs_read_bytes"
            }
            
        elif image_path:
            # Method 3: Traditional file path loading
            if not os.path.exists(image_path):
                raise ValueError(f"File ảnh không tồn tại: {image_path}")
            
            # Check file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                raise ValueError(f"Định dạng file không được hỗ trợ: {file_ext}")
            
            image = image_processor.load_image(image_path)
            input_size = os.path.getsize(image_path)
            input_info = {
                "source": "file_path",
                "file_path": image_path,
                "file_size": input_size,
                "method": "traditional_path"
            }
        
        # Convert to SVG
        conversion_result = image_processor.convert_to_svg(
            image=image,
            output_path=output_path,
            method=method,
            vectorize=vectorize,
            max_colors=max_colors
        )

        # Get output file info
        output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        input_size = input_info.get("file_size", 0)

        response = {
            "success": True,
            "input_info": input_info,
            "output_file": output_path,
            "conversion_method": method,
            "vectorized": conversion_result.get("vectorized", False),
            "file_sizes": {
                "input_bytes": input_size,
                "output_bytes": output_size,
                "compression_ratio": round(output_size / input_size, 2) if input_size > 0 else 0
            },
            "dimensions": conversion_result.get("dimensions", {}),
            "conversion_details": conversion_result,
            "fs_read_used": use_fs_read
        }

        return [
            TextContent(
                type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
            )
        ]
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "input_info": input_info,
            "fs_read_used": use_fs_read
        }
        
        return [
            TextContent(
                type="text", text=json.dumps(error_response, ensure_ascii=False, indent=2)
            )
        ]


async def main():
    """Chạy MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def cli_main():
    """Entry point for CLI command."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
