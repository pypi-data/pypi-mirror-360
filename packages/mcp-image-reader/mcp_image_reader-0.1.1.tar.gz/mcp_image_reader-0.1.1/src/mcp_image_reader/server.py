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
            name="describe_image",
            description="Mô tả nội dung tổng quát của ảnh",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Đường dẫn đến file ảnh",
                    },
                    "include_text": {
                        "type": "boolean",
                        "description": "Có bao gồm phân tích text không",
                        "default": True,
                    },
                    "include_tables": {
                        "type": "boolean",
                        "description": "Có bao gồm phân tích bảng không",
                        "default": True,
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
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý các lời gọi công cụ."""
    try:
        if name == "read_image_text":
            return await handle_read_image_text(arguments)
        elif name == "analyze_image_table":
            return await handle_analyze_image_table(arguments)
        elif name == "describe_image":
            return await handle_describe_image(arguments)
        elif name == "detect_objects":
            return await handle_detect_objects(arguments)
        elif name == "preprocess_image":
            return await handle_preprocess_image(arguments)
        elif name == "get_image_info":
            return await handle_get_image_info(arguments)
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


async def handle_describe_image(arguments: Dict[str, Any]) -> List[TextContent]:
    """Xử lý mô tả ảnh."""
    image_path = arguments["image_path"]
    include_text = arguments.get("include_text", True)
    include_tables = arguments.get("include_tables", True)

    # Load image
    image = image_processor.load_image(image_path)

    # Get image description
    description = image_processor.describe_image_content(image)

    # Add additional analysis if requested
    if include_text and not description["text_content"]["has_text"]:
        # Try to extract text anyway
        text_result = image_processor.extract_text(image)
        description["text_content"].update(
            {
                "extracted_text": (
                    text_result["text"][:500] + "..."
                    if len(text_result["text"]) > 500
                    else text_result["text"]
                )
            }
        )

    if include_tables:
        tables = image_processor.detect_tables(image)
        description["tables"]["table_details"] = tables

    response = {
        "success": True,
        "image_path": image_path,
        "description": description,
        "summary": generate_image_summary(description),
    }

    return [
        TextContent(
            type="text", text=json.dumps(response, ensure_ascii=False, indent=2)
        )
    ]


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


def generate_image_summary(description: Dict[str, Any]) -> str:
    """Tạo tóm tắt mô tả ảnh."""
    summary_parts = []

    # Basic info
    dims = description["dimensions"]
    summary_parts.append(f"Ảnh có kích thước {dims['width']}x{dims['height']} pixels")

    # Brightness
    if description["color_analysis"]["is_dark"]:
        summary_parts.append("ảnh khá tối")
    elif description["color_analysis"]["is_bright"]:
        summary_parts.append("ảnh khá sáng")

    # Content type
    content_type = description["content_type"]
    if content_type == "document_with_tables":
        summary_parts.append("chứa tài liệu với bảng")
    elif content_type == "text_document":
        summary_parts.append("chứa nhiều text")
    elif content_type == "image_with_text":
        summary_parts.append("có chứa một ít text")
    elif content_type == "diagram_or_chart":
        summary_parts.append("có thể là sơ đồ hoặc biểu đồ")

    # Text info
    if description["text_content"]["has_text"]:
        word_count = description["text_content"]["word_count"]
        summary_parts.append(f"phát hiện {word_count} từ")

    # Table info
    if description["tables"]["has_tables"]:
        table_count = description["tables"]["table_count"]
        summary_parts.append(f"có {table_count} bảng")

    return ", ".join(summary_parts) + "."


def get_shape_distribution(objects: List[Dict[str, Any]]) -> Dict[str, int]:
    """Lấy phân bố hình dạng của các đối tượng."""
    distribution = {}
    for obj in objects:
        shape = obj["shape_type"]
        distribution[shape] = distribution.get(shape, 0) + 1
    return distribution


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
