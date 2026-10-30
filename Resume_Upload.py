import io
import os
import tempfile

import docx
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

try:
    import pypandoc
except Exception:
    pypandoc = None


class MultiFormatDocumentParser:
    def __init__(self, options=None):
        self.options = options or {}
        self.reject_empty = self.options.get("reject_empty", False)
        self.enable_ocr = self.options.get("enable_ocr", True)

    def _ocr_pdf(self, file_bytes: bytes) -> str:
        try:
            images = convert_from_bytes(file_bytes)
            ocr_text = []
            for img in images:
                text = pytesseract.image_to_string(img)
                if text.strip():
                    ocr_text.append(text)
            return "\n".join(ocr_text)
        except Exception:
            return ""

    def __extract_from_doc(self, file_bytes: bytes) -> str:
        """Extract text from legacy binary .doc files via pypandoc."""
        if pypandoc is None:
            raise ValueError("pypandoc is not available for .doc parsing")

        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        try:
            return pypandoc.convert_file(temp_path, "plain", format="doc")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if extracted_text.strip() or not self.enable_ocr:
                return extracted_text
        except Exception:
            if not self.enable_ocr:
                return ""
        return self._ocr_pdf(file_bytes)

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    def _extract_from_txt(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="replace")

    def _extract_from_image(self, file_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(image)
        except Exception:
            return ""

    def parse(self, contents: bytes, filename: str) -> dict:
        ext = os.path.splitext(filename)[1].lower()
        extractors = {
            '.pdf': self._extract_from_pdf,
            '.docx': self._extract_from_docx,
            '.doc': self.__extract_from_doc,
            '.txt': self._extract_from_txt,
            '.png': self._extract_from_image,
            '.jpg': self._extract_from_image,
            '.jpeg': self._extract_from_image,
            '.bmp': self._extract_from_image,
        }

        if ext not in extractors:
            raise ValueError(f"Unsupported file format: {ext}")

        extracted_text = extractors[ext](contents)

        if self.reject_empty and not extracted_text.strip():
            raise ValueError("Document contains no readable text.")

        return {
            "filename": filename,
            "extension": ext,
            "text": extracted_text,
            "metadata": {
                "character_count": len(extracted_text),
                "byte_size": len(contents),
            },
        }
