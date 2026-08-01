import numpy as np

from backend.core.config import EMBEDDING_DTYPE, EMBEDDING_MODEL_ALIAS
from backend.core.foundry import load_model

_embedding_client = None


def get_embedding_client():
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = load_model(EMBEDDING_MODEL_ALIAS).get_embedding_client()
    return _embedding_client


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype=EMBEDDING_DTYPE)

    response = get_embedding_client().generate_embeddings(texts)
    vectors = np.array([item.embedding for item in response.data], dtype=EMBEDDING_DTYPE)

    if len(vectors) != len(texts):
        raise RuntimeError(
            f"Model {len(texts)} metin icin {len(vectors)} vektor dondurdu"
        )
    return vectors
