import pytest

from backend.core.chunker import chunk_text
from backend.core.config import CHUNK_OVERLAP, CHUNK_SIZE


def test_short_text_single_chunk():
    text = "kisa metin"

    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert len(chunks) == 1
    assert chunks[0] == {
        "chunk_index": 0,
        "chunk_text": text,
        "start_char": 0,
        "end_char": len(text),
    }


def test_empty_text_returns_no_chunks():
    assert chunk_text("", chunk_size=100, overlap=20) == []


def test_text_ending_exactly_on_boundary_has_no_empty_tail():
    text = "a" * 20

    chunks = chunk_text(text, chunk_size=10, overlap=0)

    assert len(chunks) == 2
    assert [(c["start_char"], c["end_char"]) for c in chunks] == [(0, 10), (10, 20)]
    assert all(c["chunk_text"] for c in chunks)


def test_boundary_with_overlap_has_no_empty_tail():
    text = "b" * 17

    chunks = chunk_text(text, chunk_size=10, overlap=3)

    assert [(c["start_char"], c["end_char"]) for c in chunks] == [(0, 10), (7, 17)]


def test_chunks_overlap_and_cover_whole_text():
    text = "".join(str(i % 10) for i in range(55))

    chunks = chunk_text(text, chunk_size=20, overlap=5)

    assert [c["chunk_index"] for c in chunks] == list(range(len(chunks)))
    for index, chunk in enumerate(chunks):
        assert chunk["chunk_text"] == text[chunk["start_char"] : chunk["end_char"]]
        if index > 0:
            previous = chunks[index - 1]
            assert previous["end_char"] - chunk["start_char"] == 5
    assert chunks[0]["start_char"] == 0
    assert chunks[-1]["end_char"] == len(text)


def test_overlap_greater_than_chunk_size_raises():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("a" * 50, chunk_size=10, overlap=15)


def test_overlap_equal_to_chunk_size_raises():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("a" * 50, chunk_size=10, overlap=10)


def test_negative_overlap_raises():
    with pytest.raises(ValueError, match="overlap"):
        chunk_text("a" * 50, chunk_size=10, overlap=-1)


def test_non_positive_chunk_size_raises():
    with pytest.raises(ValueError, match="chunk_size"):
        chunk_text("a" * 50, chunk_size=0, overlap=0)


def test_defaults_come_from_config():
    text = "c" * (CHUNK_SIZE + 1)

    chunks = chunk_text(text)

    assert chunks[0]["end_char"] == CHUNK_SIZE
    assert chunks[1]["start_char"] == CHUNK_SIZE - CHUNK_OVERLAP
