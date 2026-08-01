import importlib
from pathlib import Path

import pytest

from backend.core import config

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _reload_config(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # dotenv varsayilan olarak mevcut ortam degiskenlerini ezmez
    return importlib.reload(config)


def test_model_aliases_come_from_env(monkeypatch):
    reloaded = _reload_config(
        monkeypatch,
        FOUNDRY_CHAT_MODEL="phi-4-mini",
        FOUNDRY_EMBEDDING_MODEL="qwen3-embedding-8b",
    )

    assert reloaded.CHAT_MODEL_ALIAS == "phi-4-mini"
    assert reloaded.EMBEDDING_MODEL_ALIAS == "qwen3-embedding-8b"

    importlib.reload(config)


@pytest.mark.skipif(
    ENV_FILE.exists(), reason=".env dosyasi varsayilanlari eziyor, varsayilan testi anlamsiz"
)
def test_defaults_are_foundry_local_aliases(monkeypatch):
    monkeypatch.delenv("FOUNDRY_CHAT_MODEL", raising=False)
    monkeypatch.delenv("FOUNDRY_EMBEDDING_MODEL", raising=False)

    reloaded = importlib.reload(config)

    assert reloaded.CHAT_MODEL_ALIAS == "qwen3.5-2b"
    assert reloaded.EMBEDDING_MODEL_ALIAS == "qwen3-embedding-0.6b"
