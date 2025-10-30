# utils/pdf_extract.py
import fitz  # PyMuPDF


def extract_text_from_pdf(path_or_bytes):
    """Return extracted text. path_or_bytes: filepath or bytes."""
    if isinstance(path_or_bytes, bytes):
        doc = fitz.open(stream=path_or_bytes, filetype='pdf')
    else:
        doc = fitz.open(path_or_bytes)
    text = []
    for page in doc:
        text.append(page.get_text())
    return '\n'.join(text)
