import sqlite3

import numpy as np
import pytest

from backend.database.db import get_connection, init_db

TABLES = {"collections", "documents", "chunks", "chat_history", "feedback"}


@pytest.fixture
def connection(tmp_path):
    db_path = tmp_path / "test_rag.db"
    init_db(db_path)
    connection = get_connection(db_path)
    yield connection
    connection.close()


def _insert_collection(connection, name="varsayilan"):
    cursor = connection.execute(
        "INSERT INTO collections (name, description) VALUES (?, ?)",
        (name, "test koleksiyonu"),
    )
    return cursor.lastrowid


def _insert_document(connection, collection_id):
    cursor = connection.execute(
        "INSERT INTO documents (collection_id, filename, file_type, char_count, word_count)"
        " VALUES (?, ?, ?, ?, ?)",
        (collection_id, "ornek.txt", "txt", 155, 20),
    )
    return cursor.lastrowid


def test_init_db_creates_all_tables(connection):
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

    assert TABLES <= {row["name"] for row in rows}


def test_init_db_is_idempotent(tmp_path):
    db_path = tmp_path / "test_rag.db"
    init_db(db_path)

    connection = get_connection(db_path)
    _insert_collection(connection)
    connection.commit()
    connection.close()

    init_db(db_path)

    connection = get_connection(db_path)
    count = connection.execute("SELECT COUNT(*) AS n FROM collections").fetchone()["n"]
    connection.close()
    assert count == 1


def test_insert_and_select_chunk_with_embedding(connection):
    collection_id = _insert_collection(connection)
    document_id = _insert_document(connection, collection_id)
    embedding = np.array([0.1, -0.25, 3.5], dtype=np.float32)

    connection.execute(
        "INSERT INTO chunks (document_id, chunk_index, chunk_text, start_char, end_char, embedding)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (document_id, 0, "ilk parca", 0, 9, embedding.tobytes()),
    )
    connection.commit()

    row = connection.execute(
        "SELECT c.chunk_text, c.start_char, c.end_char, c.embedding, d.filename"
        " FROM chunks c JOIN documents d ON d.id = c.document_id"
        " WHERE c.document_id = ?",
        (document_id,),
    ).fetchone()

    assert row["chunk_text"] == "ilk parca"
    assert (row["start_char"], row["end_char"]) == (0, 9)
    assert row["filename"] == "ornek.txt"
    assert isinstance(row["embedding"], bytes)
    assert np.array_equal(np.frombuffer(row["embedding"], dtype=np.float32), embedding)


def test_insert_and_select_chat_history_with_feedback(connection):
    collection_id = _insert_collection(connection)
    cursor = connection.execute(
        "INSERT INTO chat_history (collection_id, question, answer) VALUES (?, ?, ?)",
        (collection_id, "Uygulama cevrimdisi mi calisir?", "Evet, tamamen yerel."),
    )
    chat_id = cursor.lastrowid
    connection.execute(
        "INSERT INTO feedback (chat_id, rating, comment) VALUES (?, ?, ?)",
        (chat_id, 1, "dogru cevap"),
    )
    connection.commit()

    row = connection.execute(
        "SELECT h.question, h.answer, f.rating, f.comment"
        " FROM chat_history h JOIN feedback f ON f.chat_id = h.id"
        " WHERE h.id = ?",
        (chat_id,),
    ).fetchone()

    assert row["question"] == "Uygulama cevrimdisi mi calisir?"
    assert row["rating"] == 1
    assert row["comment"] == "dogru cevap"


def test_duplicate_collection_name_rejected(connection):
    _insert_collection(connection)

    with pytest.raises(sqlite3.IntegrityError):
        _insert_collection(connection)


def test_chunk_requires_existing_document(connection):
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO chunks (document_id, chunk_index, chunk_text, start_char, end_char)"
            " VALUES (?, ?, ?, ?, ?)",
            (999, 0, "sahipsiz parca", 0, 14),
        )


def test_deleting_collection_cascades_to_documents_and_chunks(connection):
    collection_id = _insert_collection(connection)
    document_id = _insert_document(connection, collection_id)
    connection.execute(
        "INSERT INTO chunks (document_id, chunk_index, chunk_text, start_char, end_char)"
        " VALUES (?, ?, ?, ?, ?)",
        (document_id, 0, "ilk parca", 0, 9),
    )
    connection.commit()

    connection.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    connection.commit()

    assert connection.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"] == 0
    assert connection.execute("SELECT COUNT(*) AS n FROM chunks").fetchone()["n"] == 0
