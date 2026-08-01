# Kurulum

## Gereksinimler

- **Python 3.11, 3.12 veya 3.13.** Foundry Local SDK 3.14'u desteklemiyor; sistemde 3.14 kurulu
  olsa bile projeye ayri bir sanal ortam acilmalidir.
- Windows 10/11 (bu kurulum Windows uzerinde dogrulandi).
- En az 8 GB RAM. Modeller RAM'de calisir; bos bellek 1 GB'in altina duserse
  `bad allocation` hatasi alinir (asagida).
- Ilk kurulum icin internet (yalnizca model indirme). Sonrasi cevrimdisi calisir.

## 1. Sanal ortam

```powershell
cd C:\Users\<kullanici>\...\Local-rag
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

`uv` kuruluysa Python 3.12'yi kendisi indirir:

```powershell
uv venv --python 3.12 .venv
```

## 2. Bagimliliklar

```powershell
pip install -r requirements.txt
```

Windows'ta Foundry Local'in WinML varyanti tercih edilir (Windows ML ile daha genis donanim destegi):

```powershell
pip install foundry-local-sdk-winml
```

Iki paketi ayni anda kurma; `foundry-local-sdk` ve `foundry-local-sdk-winml` ayni
`foundry_local_sdk` modul adini paylasir.

## 3. Model ayari

Model adlari koda gomulu degil, `.env`'den okunur. Ornegi kopyala:

```powershell
copy .env.example .env
```

```
FOUNDRY_CHAT_MODEL=qwen3.5-2b
FOUNDRY_EMBEDDING_MODEL=qwen3-embedding-0.6b
```

Katalogdaki alias'lari gormek icin (SDK ile):

```powershell
python -c "from backend.core.foundry import get_manager; [print(m.alias) for m in get_manager().catalog.list_models()]"
```

## 4. Model indirme

Modeller ilk kullanimda otomatik iner; ilerleme `stderr`'e yazilir. Uygulamayi acmadan
once indirmek istersen:

```powershell
python -c "from backend.core.embedder import get_embedding_client; get_embedding_client()"
python -c "from backend.core.generator import get_chat_client; get_chat_client()"
```

Yaklasik boyutlar: gomme modeli ~0.5 GB, chat modeli ~2 GB. Modeller
`C:\Users\<kullanici>\.local-rag\cache\models` altina iner (klasor adi `FOUNDRY_APP_NAME`'den gelir).
Yer acmak icin kullanilmayan model klasorleri silinebilir.

## 5. Calistirma

```powershell
streamlit run streamlit_ui\streamlit_app.py
```

Tarayicida acilan sayfada sirasiyla: soldan koleksiyon olustur, "Belgeler" sekmesinden
PDF/DOCX/TXT/MD yukleyip "Indeksle" de, "Soru sor" sekmesinden soru sor.

Ilk soruda chat modeli bellege yuklenirken ~20 saniye beklenir, sonraki sorular daha hizlidir.

## 6. Testler ve degerlendirme

```powershell
pytest tests/                  # birim testleri
python tests\evaluate_rag.py   # RAG kalite olcumu -> tests\evaluation_results.json
```

Degerlendirme betigi ornek belgeyi gecici bir veritabanina indeksler, `tests/test_questions.json`
icindeki sorulari calistirir ve dogru parca orani, kaynak gosterme orani, cevap sureleri raporlar.
Model degistirdikten sonra bu betik yeniden calistirilip sonuclar karsilastirilmalidir.

## Sik karsilasilan sorunlar

**`ModuleNotFoundError: No module named 'foundry_local_sdk'`**
Sanal ortam aktif degil ya da paket sistem Python'una kuruldu. `.\.venv\Scripts\Activate.ps1`
calistir, `python -c "import sys; print(sys.version)"` ile 3.12 gorundugunu dogrula.

**`bad allocation` (model yuklenemedi veya cevap uretilemedi)**
Bos RAM yetmiyor. Tarayici ve diger uygulamalari kapat. Kalici cozum icin `.env`'de daha kucuk
bir chat modeli sec (ornegin `qwen3.5-0.8b`). Testler bu durumda kirmizi yanmaz, sebebini
yazip atlanir.

**Cevaplar cok yavas**
Sure, prompt'a giren baglam uzunluguyla dogru orantilidir. `config.py`'daki `TOP_K` ve
`MAX_CONTEXT_CHARS` ust siniri belirler; degistirirsen `python tests\evaluate_rag.py` ile
dogruluk kaybi olup olmadigini olc.

**Cevap "Verilen belgelerde bu bilgi bulunmuyor." diyor ama bilgi belgede var**
Once dogru parcanin getirilip getirilmedigine bak: cevabin altindaki kaynak listesi ve benzerlik
skorlari bunu gosterir. Parca dogruysa sorun modelin okumasindadir (daha buyuk model gerekir);
parca yanlissa soruyu belgenin dilini kullanacak sekilde netlestir.
