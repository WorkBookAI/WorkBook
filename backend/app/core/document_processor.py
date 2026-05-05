import fitz  # PyMuPDF
import docx
from pptx import Presentation
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    @staticmethod
    def extract_pdf(file_path: str) -> dict:
        """Extract text and images from PDF."""
        doc = fitz.open(file_path)
        content = []
        images = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            content.append({
                "page": page_num + 1,
                "text": text,
            })

            # Extract images
            for img_idx, img in enumerate(page.get_images()):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                image_path = f"{file_path}_page{page_num+1}_img{img_idx}.png"
                pix.save(image_path)
                images.append({
                    "page": page_num + 1,
                    "path": image_path,
                })

        full_text = "\n".join([c["text"] for c in content])
        doc.close()

        return {
            "type": "pdf",
            "pages": len(doc),
            "content": content,
            "full_text": full_text,
            "images": images,
        }

    @staticmethod
    def extract_docx(file_path: str) -> dict:
        """Extract text from DOCX."""
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        full_text = "\n".join(paragraphs)

        return {
            "type": "docx",
            "paragraphs": len(paragraphs),
            "content": paragraphs,
            "full_text": full_text,
        }

    @staticmethod
    def extract_pptx(file_path: str) -> dict:
        """Extract text from PPTX with Unicode support."""
        prs = Presentation(file_path)
        slides_content = []

        for slide_num, slide in enumerate(prs.slides):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    try:
                        text = shape.text.encode('utf-8', errors='replace').decode('utf-8')
                        slide_text.append(text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from shape: {e}")
                        continue

            slides_content.append({
                "slide": slide_num + 1,
                "text": "\n".join(slide_text),
            })

        full_text = "\n\n".join([s["text"] for s in slides_content if s["text"]])

        return {
            "type": "pptx",
            "slides": len(prs.slides),
            "content": slides_content,
            "full_text": full_text,
        }

    @staticmethod
    def extract_code(file_path: str) -> dict:
        """Extract code file content."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        return {
            "type": "code",
            "language": Path(file_path).suffix[1:],
            "lines": len(content.split('\n')),
            "full_text": content,
        }

    @staticmethod
    def extract_text(file_path: str) -> dict:
        """Extract plain text file content."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        return {
            "type": "text",
            "full_text": content,
        }

    @classmethod
    def process_document(cls, file_path: str) -> dict:
        """Auto-detect file type and extract content."""
        path = Path(file_path)
        ext = path.suffix.lower()

        try:
            if ext == ".pdf":
                return cls.extract_pdf(file_path)
            elif ext == ".docx":
                return cls.extract_docx(file_path)
            elif ext == ".pptx":
                return cls.extract_pptx(file_path)
            elif ext in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]:
                return cls.extract_code(file_path)
            elif ext in [".txt", ".md", ".rst"]:
                return cls.extract_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
