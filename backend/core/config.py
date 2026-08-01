import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "rag.db"

FOUNDRY_APP_NAME = "local-rag"

# Model ailesi degistirilebilir bir bilesen; kodda sabit degil, .env'den okunur.
# Buraya yalnizca Foundry Local katalogundaki alias'lar yazilir (bulut modeli degil).
EMBEDDING_MODEL_ALIAS = os.getenv("FOUNDRY_EMBEDDING_MODEL", "qwen3-embedding-0.6b")
CHAT_MODEL_ALIAS = os.getenv("FOUNDRY_CHAT_MODEL", "qwen3.5-2b")

# Embedding vektorleri BLOB olarak float32 dizisi seklinde saklanir; okurken
# ayni dtype ile cozulur, boyut blob uzunlugundan hesaplanir.
EMBEDDING_DTYPE = "float32"

# Parcalama karakter bazlidir (token degil): 1000/200, yaklasik 250 token'lik
# parca ve paragraf sinirlarinda baglam kaybini onleyecek kadar ortusme demek.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 5

# Cevap uretimi: dusuk sicaklik + sabit seed => ayni soru ayni cevabi verir,
# degerlendirme (evaluate_rag) ancak boyle karsilastirilabilir olur.
ANSWER_TEMPERATURE = 0.2
ANSWER_MAX_TOKENS = 400
ANSWER_RANDOM_SEED = 42
