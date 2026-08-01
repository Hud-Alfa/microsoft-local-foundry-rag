from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "rag.db"

FOUNDRY_APP_NAME = "local-rag"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

# Embedding vektorleri BLOB olarak float32 dizisi seklinde saklanir; okurken
# ayni dtype ile cozulur, boyut blob uzunlugundan hesaplanir.
EMBEDDING_DTYPE = "float32"

# Parcalama karakter bazlidir (token degil): 1000/200, yaklasik 250 token'lik
# parca ve paragraf sinirlarinda baglam kaybini onleyecek kadar ortusme demek.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 5
