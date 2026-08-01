from pathlib import Path

import fitz
from docx import Document


class UnsupportedFileTypeError(ValueError):
    pass


def _read_pdf(path: Path) -> str:
    with fitz.open(path) as pdf:
        return "\n".join(page.get_text() for page in pdf)


def _read_docx(path: Path) -> str:
    return "\n".join(paragraph.text for paragraph in Document(path).paragraphs)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


READERS = {
    ".pdf": _read_pdf,
    ".docx": _read_docx,
    ".txt": _read_text,
    ".md": _read_text,
}


def load_document(file_path: str) -> dict:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dosya bulunamadi: {file_path}")

    extension = path.suffix.lower()
    reader = READERS.get(extension)
    if reader is None:
        supported = ", ".join(sorted(READERS))
        raise UnsupportedFileTypeError(
            f"Desteklenmeyen dosya turu: '{extension or path.name}'. "
            f"Desteklenenler: {supported}"
        )

    text = reader(path).strip()
    return {
        "filename": path.name,
        "file_type": extension.lstrip("."),
        "text": text,
        "metadata": {
            "char_count": len(text),
            "word_count": len(text.split()),
        },
    }
