import importlib.util
from dataclasses import dataclass

import numpy as np
import pytest

from backend.core import embedder
from backend.core.config import EMBEDDING_DTYPE

is_foundry_installed = importlib.util.find_spec("foundry_local_sdk") is not None


@dataclass
class FakeEmbedding:
    embedding: list[float]


@dataclass
class FakeResponse:
    data: list[FakeEmbedding]


class FakeEmbeddingClient:
    def __init__(self, dimensions=4, returned_count=None):
        self.dimensions = dimensions
        self.returned_count = returned_count
        self.calls = []

    def generate_embeddings(self, texts):
        self.calls.append(texts)
        count = len(texts) if self.returned_count is None else self.returned_count
        return FakeResponse(
            data=[FakeEmbedding([float(i)] * self.dimensions) for i in range(count)]
        )


@pytest.fixture
def fake_client(monkeypatch):
    client = FakeEmbeddingClient()
    monkeypatch.setattr(embedder, "get_embedding_client", lambda: client)
    return client


def test_embed_texts_returns_one_row_per_text(fake_client):
    texts = ["ilk metin", "ikinci metin", "ucuncu metin"]

    vectors = embedder.embed_texts(texts)

    assert vectors.shape == (3, fake_client.dimensions)
    assert vectors.dtype == np.dtype(EMBEDDING_DTYPE)
    assert fake_client.calls == [texts]


def test_embed_texts_sends_all_texts_in_one_batch(fake_client):
    embedder.embed_texts(["a", "b"])

    assert len(fake_client.calls) == 1


def test_embed_texts_empty_input_does_not_call_model(monkeypatch):
    def fail():
        raise AssertionError("bos girdide model yuklenmemeli")

    monkeypatch.setattr(embedder, "get_embedding_client", fail)

    vectors = embedder.embed_texts([])

    assert vectors.shape == (0, 0)
    assert vectors.dtype == np.dtype(EMBEDDING_DTYPE)


def test_embed_texts_rejects_mismatched_vector_count(monkeypatch):
    monkeypatch.setattr(
        embedder, "get_embedding_client", lambda: FakeEmbeddingClient(returned_count=1)
    )

    with pytest.raises(RuntimeError, match="vektor"):
        embedder.embed_texts(["a", "b"])


def test_vectors_survive_blob_roundtrip(fake_client):
    vectors = embedder.embed_texts(["a", "b"])

    restored = np.frombuffer(vectors.tobytes(), dtype=EMBEDDING_DTYPE).reshape(
        vectors.shape
    )

    assert np.array_equal(restored, vectors)


@pytest.mark.skipif(
    not is_foundry_installed,
    reason="Foundry Local SDK kurulu degil (pip install foundry-local-sdk-winml)",
)
def test_embed_texts_against_foundry_local():
    try:
        vectors = embedder.embed_texts(["yerel model testi", "ikinci metin"])
    except Exception as error:  # servis kapali/model indirilmemis olabilir
        pytest.skip(f"Foundry Local calistirilamadi: {error}")

    assert vectors.shape[0] == 2
    assert vectors.shape[1] > 0
    assert vectors.dtype == np.dtype(EMBEDDING_DTYPE)
    assert not np.array_equal(vectors[0], vectors[1])
