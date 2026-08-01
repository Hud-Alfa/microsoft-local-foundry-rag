from pathlib import Path

from backend.core.chunker import chunk_text
from backend.core.config import DB_PATH, TOP_K
from backend.core.document_loader import load_document
from backend.core.embedder import embed_query, embed_texts
from backend.core.generator import fit_context, generate_answer
from backend.core.retriever import find_relevant_chunks
from backend.database.db import get_connection
from backend.prompts.system_prompts import EMPTY_QUESTION_ANSWER

INSERT_DOCUMENT = """
INSERT INTO documents (collection_id, filename, file_type, char_count, word_count)
VALUES (?, ?, ?, ?, ?)
"""

INSERT_CHUNK = """
INSERT INTO chunks (document_id, chunk_index, chunk_text, start_char, end_char, embedding)
VALUES (?, ?, ?, ?, ?, ?)
"""

SELECT_DOCUMENTS = """
SELECT d.id, d.filename, d.file_type, d.char_count, d.word_count, d.created_at,
       COUNT(c.id) AS chunk_count
FROM documents d
LEFT JOIN chunks c ON c.document_id = d.id
WHERE d.collection_id = ?
GROUP BY d.id
ORDER BY d.id DESC
"""

SELECT_CHAT_HISTORY = """
SELECT id, question, answer, created_at
FROM chat_history
WHERE collection_id = ?
ORDER BY id DESC
LIMIT ?
"""


def create_collection(
    name: str, description: str | None = None, db_path: str | Path = DB_PATH
) -> int:
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            "INSERT INTO collections (name, description) VALUES (?, ?)",
            (name, description),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def list_collections(db_path: str | Path = DB_PATH) -> list[dict]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT id, name, description, created_at FROM collections ORDER BY name"
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def list_documents(collection_id: int, db_path: str | Path = DB_PATH) -> list[dict]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(SELECT_DOCUMENTS, (collection_id,)).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def save_chat(
    question: str, answer: str, collection_id: int, db_path: str | Path = DB_PATH
) -> int:
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            "INSERT INTO chat_history (collection_id, question, answer) VALUES (?, ?, ?)",
            (collection_id, question, answer),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def list_chat_history(
    collection_id: int, limit: int = 20, db_path: str | Path = DB_PATH
) -> list[dict]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(SELECT_CHAT_HISTORY, (collection_id, limit)).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def index_document(
    file_path: str, collection_id: int, db_path: str | Path = DB_PATH
) -> dict:
    document = load_document(file_path)
    chunks = chunk_text(document["text"])
    vectors = embed_texts([chunk["chunk_text"] for chunk in chunks])

    connection = get_connection(db_path)
    try:
        # belge ve parcalari tek transaction: yarim indekslenmis belge kalmaz
        cursor = connection.execute(
            INSERT_DOCUMENT,
            (
                collection_id,
                document["filename"],
                document["file_type"],
                document["metadata"]["char_count"],
                document["metadata"]["word_count"],
            ),
        )
        document_id = cursor.lastrowid
        connection.executemany(
            INSERT_CHUNK,
            [
                (
                    document_id,
                    chunk["chunk_index"],
                    chunk["chunk_text"],
                    chunk["start_char"],
                    chunk["end_char"],
                    vector.tobytes(),
                )
                for chunk, vector in zip(chunks, vectors)
            ],
        )
        connection.commit()
    finally:
        connection.close()

    return {
        "document_id": document_id,
        "filename": document["filename"],
        "file_type": document["file_type"],
        "chunk_count": len(chunks),
        "char_count": document["metadata"]["char_count"],
        "word_count": document["metadata"]["word_count"],
    }


def ask_question(
    question: str,
    collection_id: int,
    top_k: int = TOP_K,
    db_path: str | Path = DB_PATH,
) -> dict:
    # bos soru iki modeli de bosuna calistirir, cevabi da anlamsiz olur
    if not question.strip():
        return {"answer": EMPTY_QUESTION_ANSWER, "sources": []}

    relevant_chunks = find_relevant_chunks(
        embed_query(question), collection_id, top_k=top_k, db_path=db_path
    )
    # kaynak listesi promptta gercekten yer alan parcalari gostermeli
    relevant_chunks = fit_context(relevant_chunks)

    return {
        "answer": generate_answer(question, relevant_chunks),
        "sources": [
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "similarity_score": chunk["similarity_score"],
            }
            for chunk in relevant_chunks
        ],
    }
