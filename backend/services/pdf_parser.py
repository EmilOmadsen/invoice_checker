import pdfplumber
import fitz  # PyMuPDF
import base64
from io import BytesIO


def pdf_to_images_base64(pdf_bytes: bytes) -> list[str]:
    """
    Convert PDF pages to base64-encoded PNG images.

    Args:
        pdf_bytes: Raw bytes of the PDF file

    Returns:
        List of base64-encoded PNG images
    """
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render at 2x resolution for better quality
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(img_base64)

    doc.close()
    return images


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.
    First tries direct text extraction, returns marker for image-based PDFs.

    Args:
        pdf_bytes: Raw bytes of the PDF file

    Returns:
        Extracted text as a string, or special marker for image PDFs
    """
    text_parts = []

    # First, try direct text extraction with pdfplumber
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            # Also extract tables if present
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables, 1):
                if table:
                    table_text = "\n".join(
                        " | ".join(str(cell) if cell else "" for cell in row)
                        for row in table
                    )
                    text_parts.append(f"\n[Table {table_idx}]\n{table_text}")

    full_text = "\n\n".join(text_parts)

    # If no text was extracted, it's likely an image-based PDF
    if not full_text.strip():
        return "[IMAGE_PDF]"

    return full_text
