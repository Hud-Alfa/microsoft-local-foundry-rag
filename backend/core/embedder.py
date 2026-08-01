import sys

import numpy as np

from backend.core.config import (
    EMBEDDING_DTYPE,
    EMBEDDING_MODEL_ALIAS,
    FOUNDRY_APP_NAME,
)

_embedding_client = None


def _report_download_progress(percent: float) -> None:
    # ilk indirme yuzlerce MB surer, geri bildirim olmazsa uygulama donmus gorunur
    print(f"\r{EMBEDDING_MODEL_ALIAS} indiriliyor: {percent:.2f}%", end="", file=sys.stderr)
    if percent >= 100:
        print(file=sys.stderr)


def get_embedding_client():
    global _embedding_client
    if _embedding_client is not None:
        return _embedding_client

    # SDK kurulu olmadan da modul import edilebilsin diye import fonksiyon icinde
    from foundry_local_sdk import Configuration, FoundryLocalManager

    FoundryLocalManager.initialize(Configuration(app_name=FOUNDRY_APP_NAME))
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(EMBEDDING_MODEL_ALIAS)
    model.download(_report_download_progress)
    model.load()

    _embedding_client = model.get_embedding_client()
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
