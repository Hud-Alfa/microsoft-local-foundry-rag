import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "rag.db"
DOCUMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "documents"

FOUNDRY_APP_NAME = "local-rag"

# Model ailesi degistirilebilir bir bilesen; kodda sabit degil, .env'den okunur.
# Buraya yalnizca Foundry Local katalogundaki alias'lar yazilir (bulut modeli degil).
EMBEDDING_MODEL_ALIAS = os.getenv("FOUNDRY_EMBEDDING_MODEL", "qwen3-embedding-0.6b")
CHAT_MODEL_ALIAS = os.getenv("FOUNDRY_CHAT_MODEL", "qwen3.5-2b")

# Embedding vektorleri BLOB olarak float32 dizisi seklinde saklanir; okurken
# ayni dtype ile cozulur, boyut blob uzunlugundan hesaplanir.
EMBEDDING_DTYPE = "float32"

# Parcalama karakter bazlidir (token degil). 400/80 olculerek secildi: kucuk parca
# hem dogru parcayi one cikariyor (ayrim gucu 0.025 -> 0.091) hem prompt'u kisaltiyor.
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

TOP_K = 3

# Uretim suresi baglam uzunluguyla dogru orantili (300 krk: 5.7s, 1500 krk: 13.3s) ve
# 5000 karakterde ONNX "bad allocation" ile cokuyor. Ust sinir bu yuzden kodda zorlanir.
MAX_CONTEXT_CHARS = 2000

# Cevap uretimi: dusuk sicaklik + sabit seed => ayni soru ayni cevabi verir,
# degerlendirme (evaluate_rag) ancak boyle karsilastirilabilir olur.
ANSWER_TEMPERATURE = 0.2
ANSWER_MAX_TOKENS = 400
ANSWER_RANDOM_SEED = 42
