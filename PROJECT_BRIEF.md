# Proje Ozeti

## Nedir

Kullanicinin yukledigi belgeler uzerinden soru sorabildigi, cevaplarini yalnizca bu
belgelerden ureten, tamamen yerel calisan bir belge soru-cevap uygulamasi.

Genel amacli bir sohbet botu degildir. Kullanici PDF, DOCX, TXT veya Markdown yukler;
uygulama metni parcalara ayirir, vektorlere cevirir ve yerel veritabaninda saklar. Soru
sorulunca en alakali parcalar bulunur ve yerel dil modeline baglam olarak verilir. Model
cevabini yalnizca bu parcalara dayandirir; bilgi belgelerde yoksa bunu acikca soyler.

Uc temel islev:

1. Belgelerden bilgi cikarir.
2. Ilgili belge parcalarini anlamsal olarak bulur.
3. Yerel yapay zeka modeliyle kaynakli cevap uretir.

## Amac

Internet baglantisina ve bulut yapay zeka servislerine ihtiyac duymadan calisan bir belge
asistani. Karsiladigi ihtiyaclar: kurum ici belgelerden hizli bilgi bulma, ders notlari ve
kullanim kilavuzlarini sorgulama, hassas belgeleri cihaz disina cikarmadan kullanma,
internetsiz ortamda yapay zeka destegi.

## Teknoloji

| Katman | Secim |
|---|---|
| Dil | Python 3.11-3.13 |
| Model calisma zamani | Microsoft Foundry Local (cihaz uzerinde) |
| Gomme modeli | qwen3-embedding-0.6b (1024 boyut) |
| Cevap modeli | qwen3.5-2b (degistirilebilir, `.env`) |
| Veritabani | SQLite (vektorler dahil, `chunks.embedding` BLOB) |
| Arayuz | Streamlit (MVP) |
| Belge okuma | PyMuPDF, python-docx |
| Hesaplama | NumPy |

Sonraki asamalar: FastAPI katmani, ardindan React arayuzu.

## Degismez kurallar

- Chunk, embedding ve cevap uretimi yalnizca Foundry Local uzerinden yapilir.
- Vektorler SQLite'ta tutulur; ayri bir vektor veritabani kurulmaz.
- Model cevabi yalnizca kendisine verilen baglama dayanir; baglamda olmayan bilgi uydurulmaz.
- Prompt metinleri tek dosyada (`backend/prompts/system_prompts.py`) tutulur.
- Sabitler (chunk boyutu, top_k, model alias'lari) tek yerde (`backend/core/config.py`) tanimlanir.
- `backend/core/` saf is mantigidir; framework ve arayuz kodu iceremez.

## Kullanilmayacak teknolojiler

GitHub/Microsoft Copilot, OpenAI API, bulut tabanli LLM servisleri, Pinecone, ChromaDB,
LangChain, fine-tuning, internetten cevap uretme, genel amacli chatbot davranisi.

Ayrim onemlidir: Copilot gelistiricinin editorunde kullanilmis olabilir, ancak projenin
calisma zamani mimarisinin parcasi degildir. Uygulamanin yapay zeka motoru Foundry Local
uzerinde calisan yerel modeldir.

## Durum

Calisir durumda: belge yukleme, parcalama, gomme, SQLite'a yazma, anlamsal getirme,
kaynakli cevap uretme ve Streamlit arayuzu (koleksiyon, belge listesi, soru sorma,
kaynak gosterme, sohbet gecmisi).

Olcum: `tests/evaluate_rag.py`, 15 soruluk test seti uzerinde dogru parca orani **1.0**,
otomatik puanlanan 12 sorunun **12'si basarili**, ortalama cevap suresi **11.4 s** (CPU).

Henuz yok: FastAPI katmani, React arayuzu, yeniden siralama (reranker), hibrit arama.

Ayrintilar: [docs/architecture.md](docs/architecture.md), [docs/setup.md](docs/setup.md).
