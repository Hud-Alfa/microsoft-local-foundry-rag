# local-rag-application-foundry-local

Microsoft Foundry Local, RAG, SQLite ve Python kullanılarak geliştirilen;
yüklenen belgelerden (PDF/DOCX/TXT/MD) kaynaklı cevap üreten, tamamen yerel
ve çevrimdışı çalışan doküman soru-cevap uygulaması. İlk aşama MVP: Streamlit
arayüzü + SQLite. Sonraki aşama: FastAPI katmanı, ardından React arayüzü.

## Teknoloji

- Python 3.11+ — ana geliştirme dili
- Microsoft Foundry Local (`foundry-local-sdk`, Windows'ta
  `foundry-local-sdk-winml`) + `openai` — hem chat hem embedding modeli
  bunun üzerinden çalışır
- SQLite — tek yerel veritabanı (collections, documents, chunks,
  chat_history, feedback)
- Streamlit — ilk çalışan arayüz (MVP)
- FastAPI — backend/frontend ayrışınca eklenecek API katmanı
- React — ileride, FastAPI hazır olduktan sonra
- PyMuPDF/pypdf, python-docx — belge metni çıkarma
- NumPy — embedding/cosine similarity hesapları
- Pandas — test/değerlendirme sonuçları

Copilot (GitHub/Microsoft/M365) bu projenin çalışma zamanı mimarisinin
parçası değil — sadece geliştirici IDE'sinde kullanılmış olabilir, RAG
akışına hiç girmez. Projenin gerçek yapay zeka motoru Foundry Local'de
çalışan yerel modeldir.

## Değişmez kurallar

1. `backend/core/` saf Python iş mantığı: document_loader, chunker,
   embedder, retriever, generator, rag_service. Framework/UI kodu buraya
   girmez, hepsi test edilebilir fonksiyonlardır.
2. Chunk/embedding/cevap üretimi SADECE Foundry Local üzerinden yapılır.
   OpenAI API, ChromaDB, Pinecone, LangChain, herhangi bir bulut LLM
   kullanılmaz.
3. Vektörler SQLite'ta saklanır (`chunks` tablosunda), ayrı bir vektör
   veritabanı kurulmaz.
4. Sistem promptu tek yerde tutulur: `backend/prompts/system_prompts.py`.
   Başka dosyada prompt metni tekrarlanmaz.
5. Model cevabı yalnızca kendisine verilen bağlama dayanır; bağlamda
   olmayan bilgi uydurulmaz, bu açıkça belirtilir.
6. Chunk boyutu (`chunk_size`, `overlap`) gibi sabitler tek bir yerde
   tanımlanır, kod içine gömülmez.

## Kod stili

- Yorum sadece kodun kendisinden çıkmayan bir "neden" varsa yazılır:
  workaround, bir chunk/overlap değerinin gerekçesi, bir kısıt. Fonksiyonun
  ne yaptığını anlatan yorum yazılmaz, isim zaten söylüyor.
- Dosya/fonksiyon başına çok satırlı docstring bloğu yok; gerekiyorsa tek
  satır.
- Kod önce basit ve çalışır haliyle yazılır, ihtiyaç çıktıkça genişler.
  Kullanılmayan parametre, "ileride lazım olur" soyutlaması yok.
- Hata yönetimi yalnızca gerçekten oluşabilecek durumlar için: dosya
  bulunamadı, model yüklenemedi, desteklenmeyen dosya türü. Her fonksiyonu
  try/except'e sarmak yok.
- Değişken/fonksiyon isimlendirmesi `snake_case`, kısaltma yok, birim
  belirsizse ada yazılır (`chunk_size`, `top_k`, `char_count`).
- Emoji yok. "AI", "generated", "as an AI" gibi ifadeler veya disclaimer
  yorumları yazılmaz.

## Dizin yapısı

```text
local-rag-application-foundry-local/
├── backend/
│   ├── core/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── rag_service.py
│   ├── database/
│   │   ├── db.py
│   │   └── rag.db
│   ├── prompts/
│   │   └── system_prompts.py
│   └── api/
│       └── main.py
├── streamlit_ui/
│   └── streamlit_app.py
├── react_frontend/
│   └── README.md
├── data/
│   ├── documents/
│   └── samples/
├── tests/
│   ├── test_questions.json
│   └── evaluate_rag.py
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   ├── final_report.md
│   └── presentation_outline.md
├── PROJECT_BRIEF.md
├── README.md
└── requirements.txt
```

## Foundry Local kullanımı

Kurulum: `pip install foundry-local-sdk openai` (Windows'ta
`foundry-local-sdk-winml` de eklenir).

Akış:

```python
from foundry_local_sdk import Configuration, FoundryLocalManager

config = Configuration(app_name="local-rag")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

model = manager.catalog.get_model(alias)
model.download(progress_callback)
model.load()

client = model.get_chat_client()
response = client.complete_chat(messages)
```

Chat modeli ve embedding modeli ayrı alias'larla yüklenir, `embedder.py` ve
`generator.py` kendi client'ını kendisi tutar. Model referansları
sabit/config dosyasında tutulur, kod içine gömülmez.

## Komutlar

- `pip install -r requirements.txt`
- `streamlit run streamlit_ui/streamlit_app.py`
- `pytest tests/`

## Çalışma şekli

- main'e doğrudan push yok. Dal: `feat/…`, `fix/…` → PR/MR.
- Commit mesajı: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `init:`
  prefix'i, kısa ve tek konulu (örn. `feat: add document loader`,
  `feat: implement chunking`).
- `backend/core/` içindeki her fonksiyona test yazılır.
