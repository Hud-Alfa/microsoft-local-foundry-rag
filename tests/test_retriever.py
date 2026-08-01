import numpy as np
import pytest

from backend.core.config import EMBEDDING_DTYPE
from backend.core.retriever import cosine_similarity, find_relevant_chunks
from backend.database.db import get_connection, init_db


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_rag.db"
    init_db(path)
    return path


def _vector(*values):
    return np.array(values, dtype=EMBEDDING_DTYPE)


def _add_collection(db_path, name):
    connection = get_connection(db_path)
    try:
        cursor = connection.execute("INSERT INTO collections (name) VALUES (?)", (name,))
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def _add_document(db_path, collection_id, filename="ornek.txt"):
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            "INSERT INTO documents (collection_id, filename, file_type, char_count, word_count)"
            " VALUES (?, ?, 'txt', 0, 0)",
            (collection_id, filename),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def _add_chunk(db_path, document_id, chunk_index, text, vector):
    connection = get_connection(db_path)
    try:
        embedding = None if vector is None else vector.tobytes()
        connection.execute(
            "INSERT INTO chunks (document_id, chunk_index, chunk_text, start_char, end_char, embedding)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (document_id, chunk_index, text, 0, len(text), embedding),
        )
        connection.commit()
    finally:
        connection.close()


@pytest.fixture
def collection_with_chunks(db_path):
    collection_id = _add_collection(db_path, "varsayilan")
    document_id = _add_document(db_path, collection_id)
    # soru vektoru (1, 0, 0) olacak: tam eslesme, kismi eslesme, dik, ters
    _add_chunk(db_path, document_id, 0, "tam eslesen parca", _vector(1, 0, 0))
    _add_chunk(db_path, document_id, 1, "kismen eslesen parca", _vector(1, 1, 0))
    _add_chunk(db_path, document_id, 2, "alakasiz parca", _vector(0, 0, 1))
    _add_chunk(db_path, document_id, 3, "ters parca", _vector(-1, 0, 0))
    return collection_id


def test_cosine_similarity_known_values():
    chunk_vectors = np.vstack([_vector(1, 0, 0), _vector(1, 1, 0), _vector(-1, 0, 0)])

    scores = cosine_similarity(_vector(1, 0, 0), chunk_vectors)

    assert scores[0] == pytest.approx(1.0)
    assert scores[1] == pytest.approx(1 / np.sqrt(2))
    assert scores[2] == pytest.approx(-1.0)


def test_cosine_similarity_zero_vector_scores_zero():
    scores = cosine_similarity(_vector(1, 0, 0), np.vstack([_vector(0, 0, 0)]))

    assert scores[0] == 0.0


def test_results_are_sorted_by_similarity(db_path, collection_with_chunks):
    results = find_relevant_chunks(
        _vector(1, 0, 0), collection_with_chunks, db_path=db_path
    )

    assert [result["chunk_text"] for result in results] == [
        "tam eslesen parca",
        "kismen eslesen parca",
        "alakasiz parca",
        "ters parca",
    ]
    scores = [result["similarity_score"] for result in results]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == pytest.approx(1.0)
    assert scores[-1] == pytest.approx(-1.0)


def test_top_k_limits_results(db_path, collection_with_chunks):
    results = find_relevant_chunks(
        _vector(1, 0, 0), collection_with_chunks, top_k=2, db_path=db_path
    )

    assert len(results) == 2
    assert results[0]["chunk_text"] == "tam eslesen parca"


def test_top_k_larger_than_chunk_count(db_path, collection_with_chunks):
    results = find_relevant_chunks(
        _vector(1, 0, 0), collection_with_chunks, top_k=50, db_path=db_path
    )

    assert len(results) == 4


def test_result_carries_source_fields(db_path, collection_with_chunks):
    result = find_relevant_chunks(
        _vector(1, 0, 0), collection_with_chunks, top_k=1, db_path=db_path
    )[0]

    assert result["filename"] == "ornek.txt"
    assert result["chunk_index"] == 0
    assert result["start_char"] == 0
    assert result["end_char"] == len("tam eslesen parca")
    assert isinstance(result["similarity_score"], float)


def test_two_dimensional_question_embedding_is_accepted(db_path, collection_with_chunks):
    question = _vector(1, 0, 0).reshape(1, 3)

    results = find_relevant_chunks(question, collection_with_chunks, db_path=db_path)

    assert results[0]["chunk_text"] == "tam eslesen parca"


def test_other_collections_are_not_searched(db_path, collection_with_chunks):
    other_id = _add_collection(db_path, "diger")
    other_document_id = _add_document(db_path, other_id, filename="diger.txt")
    _add_chunk(db_path, other_document_id, 0, "diger koleksiyon parcasi", _vector(1, 0, 0))

    results = find_relevant_chunks(
        _vector(1, 0, 0), collection_with_chunks, db_path=db_path
    )

    assert all(result["filename"] == "ornek.txt" for result in results)
    assert len(results) == 4


def test_chunks_without_embedding_are_skipped(db_path):
    collection_id = _add_collection(db_path, "varsayilan")
    document_id = _add_document(db_path, collection_id)
    _add_chunk(db_path, document_id, 0, "gomulmus parca", _vector(1, 0, 0))
    _add_chunk(db_path, document_id, 1, "gomulmemis parca", None)

    results = find_relevant_chunks(_vector(1, 0, 0), collection_id, db_path=db_path)

    assert [result["chunk_text"] for result in results] == ["gomulmus parca"]


def test_empty_collection_returns_empty_list(db_path):
    collection_id = _add_collection(db_path, "bos")

    assert find_relevant_chunks(_vector(1, 0, 0), collection_id, db_path=db_path) == []


def test_unknown_collection_returns_empty_list(db_path):
    assert find_relevant_chunks(_vector(1, 0, 0), 999, db_path=db_path) == []


def test_dimension_mismatch_raises(db_path, collection_with_chunks):
    with pytest.raises(ValueError, match="boyutlari uyusmuyor"):
        find_relevant_chunks(_vector(1, 0), collection_with_chunks, db_path=db_path)


def test_non_positive_top_k_raises(db_path, collection_with_chunks):
    with pytest.raises(ValueError, match="top_k"):
        find_relevant_chunks(
            _vector(1, 0, 0), collection_with_chunks, top_k=0, db_path=db_path
        )
