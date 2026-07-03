from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from docx import Document


def read_pdf_bytes(file_bytes: bytes) -> str:
    pdf_stream = BytesIO(file_bytes)
    reader = PdfReader(pdf_stream)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_txt_bytes(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def read_docx_bytes(file_bytes: bytes) -> str:
    doc_stream = BytesIO(file_bytes)
    document = Document(doc_stream)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_text_bytes(filename: str, file_bytes: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return read_pdf_bytes(file_bytes)
    elif extension == ".txt":
        return read_txt_bytes(file_bytes)
    elif extension == ".docx":
        return read_docx_bytes(file_bytes)

    raise Exception("Unsupported file type.")
