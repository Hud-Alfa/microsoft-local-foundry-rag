import importlib.util
from pathlib import Path

import numpy as np
import pytest

from backend.core import rag_service
from backend.core.config import CHAT_MODEL_ALIAS, EMBEDDING_DTYPE, EMBEDDING_MODEL_ALIAS
from backend.database.db import get_connection, init_db
from backend.prompts.system_prompts import EMPTY_QUESTION_ANSWER
from tests.helpers import skip_if_out_of_memory

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"
KEYWORDS = ("cevrimdisi", "parcalama", "kedi")

is_foundry_installed = importlib.util.find_spec("foundry_local_sdk") is not None


def fake_embed_texts(texts):
    # anahtar kelime sayimi: gercek modele ihtiyac duymadan anlamli siralama verir
    return np.array(
        [[text.lower().count(keyword) for keyword in KEYWORDS] for text in texts],
        dtype=EMBEDDING_DTYPE,
    )


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_rag.db"
    init_db(path)
    return path


@pytest.fixture
def collection_id(db_path):
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            "INSERT INTO collections (name) VALUES ('varsayilan')"
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


@pytest.fixture
def offline_models(monkeypatch):
    monkeypatch.setattr(rag_service, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(rag_service, "embed_query", lambda question: fake_embed_texts([question])[0])
    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        lambda question, chunks: f"cevap: {question} | parca sayisi: {len(chunks)}",
    )


@pytest.fixture
def long_document(tmp_path):
    path = tmp_path / "tesisat.txt"
    path.write_text(
        "Uygulama tamamen cevrimdisi calisir. " * 40
        + "\n"
        + "Belge parcalama isi chunker tarafindan yapilir. " * 40,
        encoding="utf-8",
    )
    return path


def _count(db_path, table, **where):
    condition = " AND ".join(f"{column} = ?" for column in where)
    connection = get_connection(db_path)
    try:
        return connection.execute(
            f"SELECT COUNT(*) AS n FROM {table} WHERE {condition}", tuple(where.values())
        ).fetchone()["n"]
    finally:
        connection.close()


def test_index_document_writes_document_and_chunks(
    db_path, collection_id, offline_models
):
    result = rag_service.index_document(
        str(SAMPLES_DIR / "ornek.md"), collection_id, db_path=db_path
    )

    assert result["filename"] == "ornek.md"
    assert result["file_type"] == "md"
    assert result["chunk_count"] >= 1
    assert result["char_count"] > 0
    assert _count(db_path, "documents", id=result["document_id"]) == 1
    assert (
        _count(db_path, "chunks", document_id=result["document_id"])
        == result["chunk_count"]
    )


def test_index_document_stores_embeddings(db_path, collection_id, offline_models):
    result = rag_service.index_document(
        str(SAMPLES_DIR / "ornek.txt"), collection_id, db_path=db_path
    )

    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT chunk_text, embedding FROM chunks WHERE document_id = ?",
            (result["document_id"],),
        ).fetchall()
    finally:
        connection.close()

    for row in rows:
        stored = np.frombuffer(row["embedding"], dtype=EMBEDDING_DTYPE)
        assert np.array_equal(stored, fake_embed_texts([row["chunk_text"]])[0])


def test_index_document_rejects_unknown_collection(db_path, offline_models):
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        rag_service.index_document(
            str(SAMPLES_DIR / "ornek.txt"), 999, db_path=db_path
        )

    assert _count(db_path, "documents", collection_id=999) == 0


def test_index_document_unsupported_file_type(db_path, collection_id, tmp_path, offline_models):
    from backend.core.document_loader import UnsupportedFileTypeError

    unsupported = tmp_path / "tablo.xlsx"
    unsupported.write_bytes(b"")

    with pytest.raises(UnsupportedFileTypeError):
        rag_service.index_document(str(unsupported), collection_id, db_path=db_path)


def test_ask_question_returns_answer_and_sources(
    db_path, collection_id, offline_models, long_document
):
    rag_service.index_document(str(long_document), collection_id, db_path=db_path)

    result = rag_service.ask_question(
        "Uygulama cevrimdisi calisir mi?", collection_id, top_k=2, db_path=db_path
    )

    assert result["answer"].startswith("cevap:")
    assert len(result["sources"]) == 2
    first = result["sources"][0]
    assert set(first) == {"filename", "chunk_index", "similarity_score"}
    assert first["filename"] == "tesisat.txt"
    scores = [source["similarity_score"] for source in result["sources"]]
    assert scores == sorted(scores, reverse=True)


def test_ask_question_picks_the_matching_chunk(
    db_path, collection_id, offline_models, long_document
):
    rag_service.index_document(str(long_document), collection_id, db_path=db_path)

    cevrimdisi = rag_service.ask_question(
        "cevrimdisi", collection_id, top_k=1, db_path=db_path
    )
    parcalama = rag_service.ask_question(
        "parcalama", collection_id, top_k=1, db_path=db_path
    )

    assert cevrimdisi["sources"][0]["chunk_index"] != parcalama["sources"][0]["chunk_index"]


@pytest.mark.parametrize("question", ["", "   "])
def test_empty_question_does_not_call_models(db_path, collection_id, monkeypatch, question):
    def fail(*args, **kwargs):
        raise AssertionError("bos soruda model cagrilmamali")

    monkeypatch.setattr(rag_service, "embed_query", fail)
    monkeypatch.setattr(rag_service, "generate_answer", fail)

    result = rag_service.ask_question(question, collection_id, db_path=db_path)

    assert result == {"answer": EMPTY_QUESTION_ANSWER, "sources": []}


def test_ask_question_on_empty_collection(db_path, collection_id, offline_models):
    result = rag_service.ask_question("herhangi bir soru", collection_id, db_path=db_path)

    assert result["sources"] == []
    assert result["answer"]


@pytest.mark.skipif(
    not is_foundry_installed,
    reason="Foundry Local SDK kurulu degil (pip install foundry-local-sdk-winml)",
)
def test_end_to_end_with_foundry_local(db_path, collection_id):
    from backend.core.foundry import get_manager

    cached = {getattr(model, "alias", None) for model in get_manager().catalog.get_cached_models()}
    missing = {EMBEDDING_MODEL_ALIAS, CHAT_MODEL_ALIAS} - cached
    if missing:
        pytest.skip(f"indirilmemis model(ler): {', '.join(sorted(missing))}")

    try:
        indexed = rag_service.index_document(
            str(SAMPLES_DIR / "ornek.md"), collection_id, db_path=db_path
        )
        assert indexed["chunk_count"] >= 1

        result = rag_service.ask_question(
            "Bu belge ne icin kullanilir?", collection_id, top_k=2, db_path=db_path
        )
    except Exception as error:
        skip_if_out_of_memory(error)

    assert result["answer"].strip()
    assert result["sources"]
    assert result["sources"][0]["filename"] == "ornek.md"
    assert -1.0 <= result["sources"][0]["similarity_score"] <= 1.0
