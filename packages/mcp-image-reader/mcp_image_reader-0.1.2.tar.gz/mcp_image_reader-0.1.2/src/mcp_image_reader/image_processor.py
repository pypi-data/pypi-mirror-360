"""Module xử lý ảnh và OCR."""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import base64
import io
import os
from typing import Dict, List, Optional, Tuple, Any
import json
import pandas as pd


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
