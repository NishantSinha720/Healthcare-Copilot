from pathlib import Path

import pymupdf
from docx import Document as DocxDocument


def extract_pdf_text(file_path):
    text_parts = []

    with pymupdf.open(file_path) as pdf:
        for page in pdf:
            text = page.get_text("text")

            if text:
                text = text.strip()

                if text:
                    text_parts.append(text)

    return "\n\n".join(text_parts).strip()


def extract_docx_text(file_path):
    document = DocxDocument(file_path)

    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    return "\n".join(text_parts).strip()


def extract_text(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError(
        "Unsupported document format. "
        "Only PDF and DOCX are supported."
    )