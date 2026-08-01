import sqlite3
from pathlib import Path

import numpy as np
import pytest

from backend.core import rag_service
from backend.core.config import EMBEDDING_DTYPE
from backend.database.db import init_db

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_rag.db"
    init_db(path)
    return path


@pytest.fixture
def offline_embedder(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_texts",
        lambda texts: np.ones((len(texts), 3), dtype=EMBEDDING_DTYPE),
    )
    monkeypatch.setattr(
        rag_service, "embed_query", lambda question: np.ones(3, dtype=EMBEDDING_DTYPE)
    )


def test_create_and_list_collections(db_path):
    first = rag_service.create_collection("mevzuat", "yonetmelikler", db_path=db_path)
    second = rag_service.create_collection("notlar", db_path=db_path)

    collections = rag_service.list_collections(db_path=db_path)

    assert [collection["id"] for collection in collections] == [first, second]
    assert collections[0]["description"] == "yonetmelikler"
    assert collections[1]["description"] is None
    assert collections[0]["created_at"]


def test_duplicate_collection_name_rejected(db_path):
    rag_service.create_collection("mevzuat", db_path=db_path)

    with pytest.raises(sqlite3.IntegrityError):
        rag_service.create_collection("mevzuat", db_path=db_path)


def test_list_documents_reports_chunk_count(db_path, offline_embedder):
    collection_id = rag_service.create_collection("mevzuat", db_path=db_path)
    indexed = rag_service.index_document(
        str(SAMPLES_DIR / "ornek.md"), collection_id, db_path=db_path
    )

    documents = rag_service.list_documents(collection_id, db_path=db_path)

    assert len(documents) == 1
    assert documents[0]["filename"] == "ornek.md"
    assert documents[0]["chunk_count"] == indexed["chunk_count"]
    assert documents[0]["char_count"] == indexed["char_count"]


def test_list_documents_is_scoped_to_collection(db_path, offline_embedder):
    first = rag_service.create_collection("ilk", db_path=db_path)
    second = rag_service.create_collection("ikinci", db_path=db_path)
    rag_service.index_document(str(SAMPLES_DIR / "ornek.md"), first, db_path=db_path)

    assert len(rag_service.list_documents(first, db_path=db_path)) == 1
    assert rag_service.list_documents(second, db_path=db_path) == []


def test_save_and_list_chat_history(db_path):
    collection_id = rag_service.create_collection("mevzuat", db_path=db_path)

    rag_service.save_chat("ilk soru", "ilk cevap", collection_id, db_path=db_path)
    last_id = rag_service.save_chat(
        "ikinci soru", "ikinci cevap", collection_id, db_path=db_path
    )

    history = rag_service.list_chat_history(collection_id, db_path=db_path)

    # en yeni kayit basta olmali
    assert history[0]["id"] == last_id
    assert history[0]["question"] == "ikinci soru"
    assert history[1]["answer"] == "ilk cevap"


def test_chat_history_limit_and_scope(db_path):
    first = rag_service.create_collection("ilk", db_path=db_path)
    second = rag_service.create_collection("ikinci", db_path=db_path)
    for index in range(5):
        rag_service.save_chat(f"soru {index}", "cevap", first, db_path=db_path)

    assert len(rag_service.list_chat_history(first, limit=3, db_path=db_path)) == 3
    assert rag_service.list_chat_history(second, db_path=db_path) == []


def test_ask_question_does_not_write_history(db_path, offline_embedder, monkeypatch):
    monkeypatch.setattr(rag_service, "generate_answer", lambda question, chunks: "cevap")
    collection_id = rag_service.create_collection("mevzuat", db_path=db_path)

    rag_service.ask_question("soru", collection_id, db_path=db_path)

    # gecmis kaydi cagiranin isi: evaluate_rag yuzlerce soru sorunca tablo kirlenmesin
    assert rag_service.list_chat_history(collection_id, db_path=db_path) == []
