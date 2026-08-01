# Geliştirme akışı — local-rag-application-foundry-local

Bu dosya projeyi adım adım, her adımda çalışan ve test edilmiş bir parça
ekleyerek geliştirmek için kullanılacak prompt sırasını tutar. Her adım tek
bir konuya odaklanır, `.claude/CLAUDE.md` kurallarına göre kod üretir ve
kendi commit'iyle biter. Bir adımı bitirmeden sonrakine geçilmez.

Her adımda: prompt'u ver → çıktıyı çalıştır/test et → commit at → sıradaki
adıma geç.

## 0. Proje iskeleti

Prompt:

> Proje kök dizinine `.claude/CLAUDE.md`'deki dizin yapısını oluştur:
> `backend/core`, `backend/database`, `backend/prompts`, `backend/api`,
> `streamlit_ui`, `data/documents`, `data/samples`, `tests`, `docs`. Her
> pakete boş `__init__.py` ekle. `requirements.txt`, `.gitignore` (venv,
> `__pycache__`, `rag.db`, `data/documents/*`) ve kısa bir `README.md`
> oluştur. Henüz iş mantığı yazma.

Commit: `init: create project structure`

## 1. Belge yükleme

Prompt:

> `backend/core/document_loader.py` dosyasını yaz. `load_document(file_path: str) -> dict`
> fonksiyonu PDF (PyMuPDF veya pypdf), DOCX (python-docx), TXT ve Markdown
> dosyalarını okuyup `{filename, file_type, text, metadata: {char_count, word_count}}`
> döndürsün. Desteklenmeyen uzantıda anlamlı bir hata fırlatsın.
> `tests/test_document_loader.py` ile her dosya türü için en az bir test
> yaz, `data/samples/` altına küçük örnek dosyalar ekle.

Commit: `feat: add document loader`

## 2. Chunking

Prompt:

> `backend/core/chunker.py` dosyasını yaz. `chunk_text(text: str, chunk_size: int, overlap: int) -> list[dict]`
> fonksiyonu metni `chunk_index`, `chunk_text`, `start_char`, `end_char`
> alanlarıyla parçalara ayırsın. `chunk_size` ve `overlap` sabitlerini
> `backend/core/config.py` içinde tanımla. Kısa metin, tam sınırda biten
> metin ve overlap'in chunk_size'dan büyük olduğu durum için test yaz.

Commit: `feat: implement chunking`

## 3. SQLite şeması

Prompt:

> `backend/database/db.py` dosyasını yaz: `collections`, `documents`,
> `chunks`, `chat_history`, `feedback` tabloları için şema ve
> `get_connection()` / `init_db()` fonksiyonları. Embedding vektörü
> `chunks` tablosunda BLOB olarak tutulsun. Testte geçici bir sqlite
> dosyasıyla tabloların oluştuğunu ve temel insert/select'in çalıştığını
> doğrula.

Commit: `feat: add sqlite schema`

## 4. Embedding (Foundry Local)

Prompt:

> `backend/core/embedder.py` dosyasını yaz. `.claude/CLAUDE.md`'deki Foundry
> Local akışını kullanarak embedding modelini yükle, `embed_texts(texts: list[str]) -> np.ndarray`
> fonksiyonunu yaz. Model referansını `backend/core/config.py`'a ekle.
> Foundry Local kurulu değilse testin anlamlı şekilde atlanmasını sağla
> (`pytest.mark.skipif` gibi).

Commit: `feat: add embedding via foundry local`

## 5. Retriever

Prompt:

> `backend/core/retriever.py` dosyasını yaz. NumPy ile cosine similarity
> hesapla, `find_relevant_chunks(question_embedding, collection_id, top_k=5) -> list[dict]`
> fonksiyonu SQLite'tan chunk'ları okuyup en alakalı `top_k` tanesini
> `similarity_score` ile birlikte döndürsün. Sahte/mock embedding
> vektörleriyle sıralamanın doğru çalıştığını test et (Foundry Local
> gerektirmez, saf NumPy testi).

Commit: `feat: implement retriever`

## 6. Yerel model ile cevap üretme

Prompt:

> `backend/prompts/system_prompts.py` içinde spec'teki sistem talimatını
> tanımla (yalnızca verilen bağlamı kullan, bağlamda yoksa uydurma).
> `backend/core/generator.py` dosyasında Foundry Local chat client'ıyla
> `generate_answer(question: str, context_chunks: list[dict]) -> str`
> fonksiyonunu yaz. Prompt'u context+soru birleştirerek kur.

Commit: `feat: add local generation`

## 7. RAG orkestratörü

Prompt:

> `backend/core/rag_service.py` dosyasında `index_document(file_path, collection_id) -> dict`
> ve `ask_question(question, collection_id, top_k=5) -> dict` fonksiyonlarını
> yaz. Bunlar 1-6 arasında yazılan modülleri sırayla çağırır. `ask_question`
> cevap + kullanılan kaynakları (belge adı, chunk index, similarity) döndürsün.
> Uçtan uca akışı gerçek/örnek bir belgeyle test et.

Commit: `feat: add rag orchestrator`

## 8. Streamlit MVP

Prompt:

> `streamlit_ui/streamlit_app.py` dosyasını yaz: koleksiyon oluşturma, belge
> yükleme, belge listesi, soru sorma, kaynak gösterme, sohbet geçmişi
> bölümleri. `rag_service`'i doğrudan çağırsın, ayrı bir API katmanı yok.

Commit: `feat: add streamlit ui`

## 9. Değerlendirme

Prompt:

> `tests/test_questions.json` içine belgede cevabı olan, olmayan, belirsiz
> ve boş soru örnekleri ekle. `tests/evaluate_rag.py` bu soruları
> `ask_question` üzerinden çalıştırıp `tests/evaluation_results.json`
> üretsin (doğru chunk bulundu mu, cevap süresi, kaynak gösterildi mi).

Commit: `test: add evaluation script and sample questions`

## 10. Dokümantasyon

Prompt:

> `docs/architecture.md` içinde sistem akışını (spec §6, §18) özetle,
> `docs/setup.md` içinde kurulum adımlarını (venv, requirements, Foundry
> Local model indirme, `streamlit run`) yaz. `PROJECT_BRIEF.md`'i kök spec
> dosyasından kısaltarak oluştur.

Commit: `docs: add architecture and setup docs`

## Sonraki aşama (MVP sonrası, ayrı zaman dilimi)

Bu adımlar Streamlit MVP çalışır hale geldikten ve değerlendirildikten
sonra, ayrı bir çalışma oturumunda başlatılır — aynı gün art arda değil.

### 11. FastAPI katmanı

Prompt:

> `backend/api/main.py` içinde spec §7.5'teki endpoint'leri (`/documents/upload`,
> `/documents`, `/chat/ask`, `/chat/history`, `/feedback`, `/stats`)
> `rag_service` üzerinden implemente et. Streamlit'i bu API'ye bağlamayı
> ayrı bir adımda değerlendir.

Commit: `feat: add fastapi layer`

### 12. React arayüzü

Prompt:

> `react_frontend/` altında FastAPI'ye bağlanan minimal bir arayüz kur:
> belge yükleme, sohbet ekranı, kaynak gösterimi.

Commit: `feat: add react frontend`
