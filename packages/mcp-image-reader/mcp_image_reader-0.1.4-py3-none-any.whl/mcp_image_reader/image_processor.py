"""Module xử lý ảnh và OCR với fs_read integration."""

import base64
import io
import logging
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import xml.etree.ElementTree as ET


class ImageProcessor:
    """Lớp xử lý ảnh và OCR."""

    def __init__(self):
        """Khởi tạo ImageProcessor."""
        self.supported_formats = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".gif",
            ".webp",
        }

    def fs_read_image(self, file_path: str) -> bytes:
        """
        Đọc file ảnh sử dụng fs_read concept.
        
        Args:
            file_path: Đường dẫn đến file ảnh
            
        Returns:
            Raw bytes của file ảnh
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File không tồn tại: {file_path}")
            
            # Check if it's an image file
            if not self.is_supported_format(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                raise ValueError(f"Định dạng file không được hỗ trợ: {ext}")
            
            # Read file as binary (simulating fs_read)
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            
            # Validate it's actually an image by trying to open it
            try:
                test_image = Image.open(io.BytesIO(image_bytes))
                test_image.verify()  # Verify it's a valid image
            except Exception as e:
                raise ValueError(f"File không phải là ảnh hợp lệ: {str(e)}")
            
            return image_bytes
            
        except Exception as e:
            raise RuntimeError(f"Lỗi khi đọc file ảnh: {str(e)}")

    def load_image_from_bytes(self, image_bytes: bytes) -> Image.Image:
        """
        Load ảnh từ raw bytes.
        
        Args:
            image_bytes: Raw bytes của ảnh
            
        Returns:
            PIL Image object
        """
        try:
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            raise RuntimeError(f"Lỗi khi load ảnh từ bytes: {str(e)}")

    def load_image_from_base64(self, base64_data: str) -> Image.Image:
        """
        Load ảnh từ base64 string.
        
        Args:
            base64_data: Base64 encoded image data
            
        Returns:
            PIL Image object
        """
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',', 1)[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_data)
            
            # Load from bytes
            return self.load_image_from_bytes(image_bytes)
            
        except Exception as e:
            raise RuntimeError(f"Lỗi khi load ảnh từ base64: {str(e)}")

    def is_supported_format(self, file_path: str) -> bool:
        """Kiểm tra định dạng ảnh có được hỗ trợ không."""
        ext = os.path.splitext(file_path.lower())[1]
        return ext in self.supported_formats

    def load_image(self, image_path: str) -> Image.Image:
        """Tải ảnh từ file path."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Không tìm thấy file ảnh: {image_path}")

        if not self.is_supported_format(image_path):
            raise ValueError(f"Định dạng ảnh không được hỗ trợ: {image_path}")

        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise ValueError(f"Không thể tải ảnh: {str(e)}")

    def preprocess_image(
        self,
        image: Image.Image,
        enhance_contrast: bool = True,
        denoise: bool = True,
        sharpen: bool = True,
    ) -> Image.Image:
        """Tiền xử lý ảnh để cải thiện chất lượng OCR."""
        processed_image = image.copy()

        # Enhance contrast
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.5)

        # Denoise
        if denoise:
            processed_image = processed_image.filter(ImageFilter.MedianFilter(size=3))

        # Sharpen
        if sharpen:
            processed_image = processed_image.filter(ImageFilter.SHARPEN)

        return processed_image

    def extract_text(self, image: Image.Image, language: str = "eng") -> Dict[str, Any]:
        """Trích xuất text từ ảnh sử dụng Tesseract OCR."""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # OCR configuration
            config = "--oem 3 --psm 6"

            # Extract text
            text = pytesseract.image_to_string(cv_image, lang=language, config=config)

            # Get detailed data with bounding boxes
            data = pytesseract.image_to_data(
                cv_image,
                lang=language,
                config=config,
                output_type=pytesseract.Output.DICT,
            )

            # Extract confidence scores and bounding boxes
            words_info = []
            for i in range(len(data["text"])):
                if int(data["conf"][i]) > 0:  # Only include words with confidence > 0
                    words_info.append(
                        {
                            "text": data["text"][i],
                            "confidence": int(data["conf"][i]),
                            "bbox": {
                                "x": data["left"][i],
                                "y": data["top"][i],
                                "width": data["width"][i],
                                "height": data["height"][i],
                            },
                        }
                    )

            return {
                "text": text.strip(),
                "words": words_info,
                "language": language,
                "total_words": len([w for w in words_info if w["text"].strip()]),
                "average_confidence": (
                    np.mean([w["confidence"] for w in words_info]) if words_info else 0
                ),
            }
        except Exception as e:
            raise RuntimeError(f"Lỗi khi trích xuất text: {str(e)}")

    def detect_tables(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Phát hiện và trích xuất bảng từ ảnh."""
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            # Detect vertical lines
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)

            # Combine lines
            table_mask = cv2.addWeighted(
                horizontal_lines, 0.5, vertical_lines, 0.5, 0.0
            )

            # Find contours
            contours, _ = cv2.findContours(
                table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            tables = []
            for i, contour in enumerate(contours):
                # Filter small contours
                area = cv2.contourArea(contour)
                if area < 1000:  # Minimum area threshold
                    continue

                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Extract table region
                table_region = image.crop((x, y, x + w, y + h))

                # Extract text from table region
                table_text = self.extract_text(table_region)

                # Try to parse as table
                table_data = self._parse_table_text(table_text["text"])

                tables.append(
                    {
                        "id": i,
                        "bbox": {"x": x, "y": y, "width": w, "height": h},
                        "text": table_text["text"],
                        "data": table_data,
                        "confidence": table_text["average_confidence"],
                    }
                )

            return tables
        except Exception as e:
            raise RuntimeError(f"Lỗi khi phát hiện bảng: {str(e)}")

    def _parse_table_text(self, text: str) -> List[List[str]]:
        """Parse text thành dạng bảng."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Simple table parsing - split by whitespace
        table_data = []
        for line in lines:
            # Split by multiple spaces or tabs
            cells = [cell.strip() for cell in line.split() if cell.strip()]
            if cells:
                table_data.append(cells)

        return table_data

    def detect_objects(self, image: Image.Image) -> Dict[str, Any]:
        """Phát hiện đối tượng cơ bản trong ảnh."""
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Simple object detection using contours
            # Apply threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            objects = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 100:  # Filter small objects
                    continue

                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Calculate object properties
                aspect_ratio = w / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0

                # Simple shape classification
                shape_type = self._classify_shape(contour, aspect_ratio, extent)

                objects.append(
                    {
                        "id": i,
                        "bbox": {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h),
                        },
                        "area": float(area),
                        "aspect_ratio": float(aspect_ratio),
                        "shape_type": shape_type,
                    }
                )

            return {"object_count": len(objects), "objects": objects}
        except Exception as e:
            raise RuntimeError(f"Lỗi khi phát hiện đối tượng: {str(e)}")

    def _classify_shape(self, contour, aspect_ratio: float, extent: float) -> str:
        """Phân loại hình dạng cơ bản."""
        # Approximate contour
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        vertices = len(approx)

        if vertices == 3:
            return "triangle"
        elif vertices == 4:
            if 0.8 <= aspect_ratio <= 1.2:
                return "square"
            else:
                return "rectangle"
        elif vertices > 8:
            return "circle"
        else:
            return "polygon"

    def convert_to_svg(
        self, 
        image: Image.Image, 
        output_path: str,
        method: str = "embed",
        vectorize: bool = False,
        max_colors: int = 16
    ) -> Dict[str, Any]:
        """
        Convert PNG/JPG image to SVG format.
        
        Args:
            image: PIL Image object
            output_path: Path to save SVG file
            method: Conversion method ('embed', 'trace', 'hybrid')
            vectorize: Whether to attempt vectorization
            max_colors: Maximum colors for vectorization
            
        Returns:
            Dictionary with conversion results
        """
        try:
            width, height = image.size
            
            if method == "embed":
                # Simple embedding method - fastest
                return self._embed_image_to_svg(image, output_path, width, height)
            
            elif method == "trace" and vectorize:
                # Edge tracing method - more vector-like
                return self._trace_image_to_svg(image, output_path, width, height, max_colors)
            
            elif method == "hybrid":
                # Hybrid approach - combine embedding with some vectorization
                return self._hybrid_image_to_svg(image, output_path, width, height, max_colors)
            
            else:
                # Default to embed method
                return self._embed_image_to_svg(image, output_path, width, height)
                
        except Exception as e:
            raise RuntimeError(f"Lỗi khi convert sang SVG: {str(e)}")

    def _embed_image_to_svg(self, image: Image.Image, output_path: str, width: int, height: int) -> Dict[str, Any]:
        """Embed image as base64 in SVG."""
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Create SVG with embedded image
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" 
     viewBox="0 0 {width} {height}">
  <title>Converted Image</title>
  <image x="0" y="0" width="{width}" height="{height}" 
         xlink:href="data:image/png;base64,{img_data}"/>
</svg>'''
        
        # Save SVG file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return {
            "method": "embed",
            "file_size": len(svg_content),
            "dimensions": {"width": width, "height": height},
            "vectorized": False
        }

    def _trace_image_to_svg(self, image: Image.Image, output_path: str, width: int, height: int, max_colors: int) -> Dict[str, Any]:
        """Trace image edges to create vector paths."""
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Reduce colors for better tracing
        reduced_image = self._reduce_colors(cv_image, max_colors)
        
        # Find contours for different color regions
        paths = self._extract_color_paths(reduced_image)
        
        # Create SVG with paths
        svg_content = self._create_svg_with_paths(paths, width, height)
        
        # Save SVG file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return {
            "method": "trace",
            "file_size": len(svg_content),
            "dimensions": {"width": width, "height": height},
            "vectorized": True,
            "paths_count": len(paths),
            "colors_used": max_colors
        }

    def _hybrid_image_to_svg(self, image: Image.Image, output_path: str, width: int, height: int, max_colors: int) -> Dict[str, Any]:
        """Hybrid method: embed image + add vector overlays for text/shapes."""
        # Start with embedded image
        result = self._embed_image_to_svg(image, output_path + ".temp", width, height)
        
        # Detect text regions and simple shapes
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Extract text information
        text_info = self.extract_text(image)
        
        # Detect simple shapes
        objects_info = self.detect_objects(image)
        
        # Create enhanced SVG
        svg_content = self._create_hybrid_svg(image, width, height, text_info, objects_info)
        
        # Save final SVG
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # Clean up temp file
        if os.path.exists(output_path + ".temp"):
            os.remove(output_path + ".temp")
        
        return {
            "method": "hybrid",
            "file_size": len(svg_content),
            "dimensions": {"width": width, "height": height},
            "vectorized": True,
            "text_regions": len(text_info.get("words", [])),
            "shapes_detected": len(objects_info.get("objects", []))
        }

    def _reduce_colors(self, image: np.ndarray, max_colors: int) -> np.ndarray:
        """Reduce number of colors in image for better vectorization."""
        # Reshape image to be a list of pixels
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        # Apply K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, max_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8 and reshape
        centers = np.uint8(centers)
        reduced_data = centers[labels.flatten()]
        reduced_image = reduced_data.reshape(image.shape)
        
        return reduced_image

    def _extract_color_paths(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract paths for different color regions."""
        paths = []
        height, width = image.shape[:2]
        
        # Get unique colors
        unique_colors = np.unique(image.reshape(-1, image.shape[2]), axis=0)
        
        for color in unique_colors:
            # Create mask for this color
            mask = cv2.inRange(image, color, color)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) > 10:  # Filter small areas
                    # Convert contour to SVG path
                    path_data = self._contour_to_svg_path(contour)
                    
                    paths.append({
                        "path": path_data,
                        "fill": f"rgb({color[2]},{color[1]},{color[0]})",  # BGR to RGB
                        "area": cv2.contourArea(contour)
                    })
        
        return paths

    def _contour_to_svg_path(self, contour: np.ndarray) -> str:
        """Convert OpenCV contour to SVG path data."""
        if len(contour) < 2:
            return ""
        
        # Start path
        path_data = f"M {contour[0][0][0]} {contour[0][0][1]}"
        
        # Add lines to other points
        for point in contour[1:]:
            path_data += f" L {point[0][0]} {point[0][1]}"
        
        # Close path
        path_data += " Z"
        
        return path_data

    def _create_svg_with_paths(self, paths: List[Dict[str, Any]], width: int, height: int) -> str:
        """Create SVG content with vector paths."""
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="{width}" height="{height}" 
     viewBox="0 0 {width} {height}">
  <title>Vectorized Image</title>
'''
        
        # Sort paths by area (largest first) for better layering
        sorted_paths = sorted(paths, key=lambda x: x["area"], reverse=True)
        
        for path_info in sorted_paths:
            svg_content += f'  <path d="{path_info["path"]}" fill="{path_info["fill"]}" stroke="none"/>\n'
        
        svg_content += '</svg>'
        
        return svg_content

    def _create_hybrid_svg(self, image: Image.Image, width: int, height: int, text_info: Dict, objects_info: Dict) -> str:
        """Create hybrid SVG with embedded image + vector overlays."""
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" 
     viewBox="0 0 {width} {height}">
  <title>Hybrid Image</title>
  
  <!-- Base image -->
  <image x="0" y="0" width="{width}" height="{height}" 
         xlink:href="data:image/png;base64,{img_data}" opacity="0.9"/>
  
  <!-- Vector overlays -->
  <g id="overlays">
'''
        
        # Add text overlays (if text was detected)
        if text_info.get("words"):
            svg_content += '    <!-- Text regions -->\n'
            for word in text_info["words"][:10]:  # Limit to first 10 words
                if "bbox" in word:
                    x, y, w, h = word["bbox"]
                    svg_content += f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="blue" stroke-width="1" opacity="0.3"/>\n'
        
        # Add shape overlays (if shapes were detected)
        if objects_info.get("objects"):
            svg_content += '    <!-- Detected shapes -->\n'
            for obj in objects_info["objects"][:5]:  # Limit to first 5 objects
                if "bbox" in obj:
                    x, y, w, h = obj["bbox"]
                    svg_content += f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="red" stroke-width="2" opacity="0.5"/>\n'
        
        svg_content += '''  </g>
</svg>'''
        
        return svg_content
