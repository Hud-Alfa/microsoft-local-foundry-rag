# Mimari

## Sistem akisi

Spec §6'daki 12 adim, kodda su sekilde karsilik buluyor:

```
BELGE YUKLEME (index_document)
  1-2. Kullanici belge yukler, metni cikarilir      document_loader.py   PDF/DOCX/TXT/MD
  3.   Metin parcalara bolunur                       chunker.py           paragraf sinirli, 400 krk
  4.   Her parca vektore cevrilir                    embedder.py          qwen3-embedding-0.6b, 1024 boyut
  5.   Vektorler veritabanina yazilir                rag_service.py       chunks.embedding (float32 BLOB)

SORU SORMA (ask_question)
  6-7. Soru alinir ve vektore cevrilir               embedder.embed_query talimat onekli
  8-9. Benzerlik hesaplanir, en iyi K parca secilir   retriever.py         cosine similarity (NumPy)
  10.  Parcalar baglam olarak modele verilir          generator.py         qwen3.5-2b
  11.  Model yalnizca bu baglama gore cevaplar        system_prompts.py    baglam disina cikmaz
  12.  Cevap ve kaynaklar gosterilir                  streamlit_app.py     dosya adi, parca no, benzerlik
```

Tum zincir tek makinede calisir. Internet yalnizca modellerin **ilk indirilmesinde** gerekir;
sonrasinda sistem cevrimdisi calisir. Hicbir asamada bulut servisi cagrilmaz.

## Modul sorumluluklari

| Modul | Sorumluluk | Disa bagimlilik |
|---|---|---|
| `core/document_loader.py` | Dosyadan metin cikarma, desteklenmeyen turde anlamli hata | PyMuPDF, python-docx |
| `core/chunker.py` | Paragraf sinirlarina saygili parcalama, orijinal metne offset | yok (saf Python) |
| `core/embedder.py` | Parca ve sorgu gomme; sorgu talimat onekli gomulur | Foundry Local |
| `core/retriever.py` | Cosine similarity, koleksiyon icinde en iyi K parca | NumPy, SQLite |
| `core/generator.py` | Prompt kurma, baglam siniri, cevap uretme | Foundry Local |
| `core/rag_service.py` | Yukaridakileri sirayla cagiran servis katmani + koleksiyon/belge/gecmis sorgulari | SQLite |
| `core/foundry.py` | Foundry Local manager'i ve model yukleme (tek noktadan) | Foundry Local |
| `core/config.py` | Tum sabitler; model alias'lari `.env`'den okunur | python-dotenv |
| `prompts/system_prompts.py` | Butun prompt metinleri (sistem promptu, sablonlar, sabit cevaplar) | yok |
| `database/db.py` | Sema ve baglanti | sqlite3 |
| `streamlit_ui/streamlit_app.py` | Arayuz; SQL icermez, yalnizca `rag_service` cagirir | Streamlit |

Bagimlilik yonu tek yonludur: `streamlit_ui -> rag_service -> (core modulleri) -> database`.
Arayuz veritabanina dogrudan dokunmaz, `core` de arayuzu bilmez.

## Veri modeli

```
collections (id, name UNIQUE, description, created_at)
  └── documents (id, collection_id, filename, file_type, char_count, word_count, created_at)
        └── chunks (id, document_id, chunk_index, chunk_text, start_char, end_char, embedding BLOB)
chat_history (id, collection_id, question, answer, created_at)
  └── feedback (id, chat_id, rating, comment, created_at)
```

- Vektorler ayri bir vektor veritabaninda degil, `chunks.embedding` icinde `float32` BLOB olarak durur.
- `start_char`/`end_char` orijinal metne isaret eder; parca kirpilmaz, kaynak gosterimi buna dayanir.
- Yabanci anahtarlar `ON DELETE CASCADE`; koleksiyon silinince belgeleri ve parcalari da silinir.
  SQLite'ta bu kontrol baglanti basina acilir, `get_connection()` bunu tek noktadan yapar.

## Olcumle alinan kararlar

Bu kararlar tahminle degil, olculerek verildi; degistirmeden once `tests/evaluate_rag.py` calistirilmalidir.

| Karar | Gerekce |
|---|---|
| Parcalama paragraf sinirinda (400/80) | Baslik kendi bolumuyle ayni parcada kalir. Dogru parca 1. sirada: 6/7 -> 7/7, ayrim gucu 0.087 -> 0.147 |
| Sorgu talimat onekli gomulur | Qwen3-Embedding asimetrik calisir; onek ayrim gucunu ~iki katina cikarir |
| `TOP_K = 3`, `MAX_CONTEXT_CHARS = 2000` | Uretim suresi baglam uzunluguyla dogru orantili (300 krk: 5.7 s, 1500 krk: 13.3 s), 5000 krk'de ONNX `bad allocation` ile cokuyor |
| Sabit seed + dusuk sicaklik | Ayni soru ayni cevabi verir; degerlendirme ancak boyle karsilastirilabilir |
| Baglam bossa model cagrilmaz | Uydurma riski prompt'a degil, yapiya birakilir |
| Bos soru modele gitmez | Iki modeli bosuna calistirmanin anlami yok |
| Zaman damgalari `localtime` | Uygulama tek makinede calisir; UTC gostermek kullaniciyi yaniltiyordu |

## Su an kapsam disinda

- `backend/api/main.py` (FastAPI) ve `react_frontend/` spec'te planli, henuz yazilmadi.
  Arayuz bugun `rag_service`'i dogrudan cagirir; API katmani eklendiginde ayni servis
  fonksiyonlari HTTP arkasina alinacak, `core` degismeyecek.
- Yeniden siralama (reranker), hibrit arama (BM25 + vektor) ve sorgu yeniden yazma yok.
- GPU hizlandirma: makinede CUDA saglayicisi kayitli ama Foundry Local katalogunda
  GPU model varyanti yayinlanmiyor, tum modeller `generic-cpu`. Varyant cikarsa
  `.env`'deki alias disinda degisiklik gerekmez.
