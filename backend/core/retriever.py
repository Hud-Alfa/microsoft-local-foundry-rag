from pathlib import Path

import numpy as np

from backend.core.config import DB_PATH, EMBEDDING_DTYPE, TOP_K
from backend.database.db import get_connection

SELECT_CHUNKS = """
SELECT c.id, c.document_id, c.chunk_index, c.chunk_text, c.start_char, c.end_char,
       c.embedding, d.filename
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE d.collection_id = ? AND c.embedding IS NOT NULL
ORDER BY c.id
"""


def cosine_similarity(question_vector: np.ndarray, chunk_vectors: np.ndarray) -> np.ndarray:
    denominator = np.linalg.norm(chunk_vectors, axis=1) * np.linalg.norm(question_vector)
    dot_products = chunk_vectors @ question_vector
    # sifir vektorlu parca 0/0 uretir, benzerligi 0 sayilir
    return np.divide(
        dot_products,
        denominator,
        out=np.zeros_like(dot_products),
        where=denominator > 0,
    )


def find_relevant_chunks(
    question_embedding: np.ndarray,
    collection_id: int,
    top_k: int = TOP_K,
    db_path: str | Path = DB_PATH,
) -> list[dict]:
    if top_k <= 0:
        raise ValueError(f"top_k pozitif olmali: {top_k}")

    # embed_texts (1, boyut) dondurur, tek soru vektoru olarak duzlestirilir
    question_vector = np.asarray(question_embedding, dtype=EMBEDDING_DTYPE).ravel()

    connection = get_connection(db_path)
    try:
        rows = connection.execute(SELECT_CHUNKS, (collection_id,)).fetchall()
    finally:
        connection.close()

    if not rows:
        return []

    chunk_vectors = np.vstack(
        [np.frombuffer(row["embedding"], dtype=EMBEDDING_DTYPE) for row in rows]
    )
    if chunk_vectors.shape[1] != question_vector.shape[0]:
        raise ValueError(
            f"Vektor boyutlari uyusmuyor: soru {question_vector.shape[0]}, "
            f"parca {chunk_vectors.shape[1]} - parcalar baska bir modelle gomulmus olabilir"
        )

    scores = cosine_similarity(question_vector, chunk_vectors)
    best_indexes = np.argsort(-scores, kind="stable")[:top_k]

    return [
        {
            "chunk_id": rows[index]["id"],
            "document_id": rows[index]["document_id"],
            "filename": rows[index]["filename"],
            "chunk_index": rows[index]["chunk_index"],
            "chunk_text": rows[index]["chunk_text"],
            "start_char": rows[index]["start_char"],
            "end_char": rows[index]["end_char"],
            "similarity_score": float(scores[index]),
        }
        for index in best_indexes
    ]
