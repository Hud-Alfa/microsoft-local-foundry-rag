from pathlib import Path

import pytest

from backend.core.document_loader import UnsupportedFileTypeError, load_document

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


@pytest.mark.parametrize(
    "filename, file_type, expected_text",
    [
        ("ornek.txt", "txt", "Yerel RAG uygulamasi"),
        ("ornek.md", "md", "# Ornek Markdown Belgesi"),
        ("ornek.docx", "docx", "Ornek Word Belgesi"),
        ("ornek.pdf", "pdf", "Ornek PDF Belgesi"),
    ],
)
def test_load_document_supported_types(filename, file_type, expected_text):
    result = load_document(str(SAMPLES_DIR / filename))

    assert result["filename"] == filename
    assert result["file_type"] == file_type
    assert expected_text in result["text"]
    assert result["metadata"]["char_count"] == len(result["text"])
    assert result["metadata"]["word_count"] == len(result["text"].split())


def test_load_document_extension_is_case_insensitive(tmp_path):
    path = tmp_path / "BUYUK.TXT"
    path.write_text("iki kelime", encoding="utf-8")

    result = load_document(str(path))

    assert result["file_type"] == "txt"
    assert result["metadata"]["word_count"] == 2


def test_load_document_unsupported_extension(tmp_path):
    path = tmp_path / "tablo.xlsx"
    path.write_bytes(b"")

    with pytest.raises(UnsupportedFileTypeError, match="xlsx"):
        load_document(str(path))


def test_load_document_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_document(str(tmp_path / "yok.txt"))
