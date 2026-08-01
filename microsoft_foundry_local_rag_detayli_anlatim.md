# Microsoft Foundry Local ile Dinamik RAG Uygulaması

## 1. Projenin Genel Tanımı

Bu proje, kullanıcıların yüklediği belgeler üzerinden soru sorabildiği ve cevaplarını yalnızca bu belgelerden alan, tamamen yerel çalışan bir yapay zekâ destekli belge soru-cevap uygulamasıdır.

Sistem genel amaçlı bir sohbet botu olarak tasarlanmamıştır. Kullanıcı sisteme PDF, DOCX, TXT veya Markdown dosyaları yükler. Uygulama bu dosyaların içeriğini işler, metni küçük parçalara ayırır, bu parçaları sayısal vektörlere dönüştürür ve yerel veritabanında saklar. Kullanıcı bir soru sorduğunda sistem, soruyla en alakalı belge parçalarını bulur ve bu parçaları yerel çalışan dil modeline bağlam olarak verir.

Dil modeli, cevabını yalnızca bulunan belge parçalarına dayanarak üretir. Cevap yüklenen belgelerde yoksa sistemin bunu açıkça belirtmesi hedeflenir.

Bu nedenle proje üç temel özelliğe sahiptir:

1. Belgelerden bilgi çıkarır.
2. İlgili belge parçalarını anlamsal olarak bulur.
3. Yerel yapay zekâ modeliyle kaynaklı cevap üretir.

---

## 2. Projenin Temel Amacı

Projenin amacı, internet bağlantısına ve bulut tabanlı yapay zekâ servislerine ihtiyaç duymadan çalışan bir belge asistanı geliştirmektir.

Bu uygulama aşağıdaki ihtiyaçlara cevap verir:

- Kurum içi belgelerden hızlı bilgi bulma
- Ders notları üzerinden soru sorma
- Kullanım kılavuzlarından bilgi çıkarma
- Teknik dokümanları sorgulama
- Sık sorulan sorular dosyalarından cevap üretme
- Hassas belgeleri cihaz dışına göndermeden kullanma
- İnternet olmayan ortamlarda yapay zekâ desteği sağlama

Sistemin en önemli farkı, cevap üretirken doğrudan yüklenen belgeleri kaynak olarak kullanmasıdır.

---

## 3. Copilot Kullanılıyor mu?

Hayır. Bu projenin çalışan yapısında GitHub Copilot, Microsoft Copilot veya benzeri bir Copilot servisi kullanılmamaktadır.

Copilot ile Microsoft Foundry Local aynı şey değildir.

### Copilot nedir?

Copilot, kullanıcıya kod yazma, metin üretme veya ofis uygulamalarında yardımcı olma amacıyla kullanılan bir yapay zekâ asistanıdır.

Örneğin:

- GitHub Copilot kod yazmaya yardımcı olur.
- Microsoft 365 Copilot Word, Excel ve PowerPoint içinde çalışabilir.
- Microsoft Copilot genel amaçlı yapay zekâ asistanı olarak kullanılabilir.

Ancak bunların hiçbiri bu projenin zorunlu bir bileşeni değildir.

### Bu projede kullanılan asıl yapay zekâ nedir?

Bu projede yapay zekâ modeli, Microsoft Foundry Local üzerinden yerel olarak çalıştırılır.

Dolayısıyla sunumda şu ifade kullanılabilir:

> Bu projede Copilot kullanılmamaktadır. Yapay zekâ modeli Microsoft Foundry Local üzerinde yerel olarak çalışmaktadır.

### Copilot geliştirme sırasında kullanılabilir mi?

İstenirse sadece geliştirme sürecinde bir kod yardımcısı olarak kullanılabilir. Örneğin geliştirici Visual Studio Code içinde GitHub Copilot kullanarak kod tamamlama desteği alabilir.

Fakat bu kullanım:

- Projenin mimarisinin bir parçası değildir.
- Uygulamanın çalışması için gerekli değildir.
- Son kullanıcıya sunulan bir özellik değildir.
- Yapay zekâ cevap üretme sürecinde görev almaz.
- RAG akışına dahil değildir.

Yani Copilot kullanılsa bile yalnızca geliştirici aracı olur. Projenin gerçek yapay zekâ altyapısı yine Microsoft Foundry Local olur.

---

## 4. Microsoft Foundry Local Nedir?

Microsoft Foundry Local, yapay zekâ modellerinin doğrudan kullanıcının bilgisayarında çalıştırılmasını sağlayan yerel yapay zekâ çalışma ortamıdır.

Bu sistem sayesinde model çalıştırmak için sürekli internet bağlantısına veya bulut tabanlı bir API'ye ihtiyaç duyulmaz.

Foundry Local'in projedeki görevleri şunlardır:

- Yerel dil modelini çalıştırmak
- Kullanıcı sorularını modele iletmek
- Belge parçalarını bağlam olarak modele vermek
- Cevabı cihaz üzerinde üretmek
- Embedding modeli kullanılarak metinleri vektörleştirmek
- Bulut bağımlılığını azaltmak

### Foundry Local neden tercih edilmektedir?

Başlıca nedenler:

- İnternet bağlantısı olmadan çalışabilmesi
- Verilerin cihaz dışına çıkmaması
- Yerel model çalıştırabilmesi
- Bulut API maliyeti oluşturmaması
- Hassas veya kurum içi belgeler için daha uygun olması
- Eğitim ve demo ortamlarında bağımsız çalışabilmesi

---

## 5. RAG Nedir?

RAG, Retrieval-Augmented Generation ifadesinin kısaltmasıdır.

Türkçe olarak yaklaşık biçimde:

> Bilgi Getirme Destekli Cevap Üretme

şeklinde açıklanabilir.

RAG sistemi üç ana aşamada çalışır:

### 5.1 Retrieval – Bilgiyi Getirme

Kullanıcı bir soru sorduğunda sistem, yüklenen belgeler içerisinden soruyla en alakalı metin parçalarını bulur.

### 5.2 Augmentation – Bağlam Ekleme

Bulunan metin parçaları kullanıcının sorusuyla birlikte yapay zekâ modeline gönderilir.

### 5.3 Generation – Cevap Üretme

Yerel dil modeli, kendisine verilen belge parçalarını kullanarak cevap üretir.

Bu yaklaşım sayesinde model yalnızca genel bilgisini kullanmak yerine, doğrudan kullanıcı tarafından yüklenen belgelere dayanır.

---

## 6. Sistem Nasıl Çalışır?

Sistemin çalışma sırası aşağıdaki gibidir:

1. Kullanıcı belge yükler.
2. Belgenin metni çıkarılır.
3. Metin küçük parçalara bölünür.
4. Her parça embedding modelinden geçirilir.
5. Embedding sonuçları SQLite veritabanına kaydedilir.
6. Kullanıcı soru sorar.
7. Sorunun da embedding değeri oluşturulur.
8. Soruyla belge parçaları arasında benzerlik hesaplanır.
9. En alakalı belge parçaları seçilir.
10. Seçilen parçalar yerel dil modeline gönderilir.
11. Model yalnızca bu bağlama göre cevap üretir.
12. Kullanıcıya cevap ve kaynak bilgileri gösterilir.

Bu sürecin tamamı tek bir bilgisayarda ve internet bağlantısı olmadan çalışacak şekilde planlanmıştır.

---

## 7. Kullanılacak Teknolojiler

## 7.1 Python

Python, projenin ana geliştirme dilidir.

Python ile aşağıdaki işlemler gerçekleştirilecektir:

- Dosya okuma
- Belgeden metin çıkarma
- Metni parçalara ayırma
- Embedding üretme
- Benzerlik hesaplama
- Veritabanı işlemleri
- RAG akışını yönetme
- Arayüz ve API geliştirme

Python tercih edilme nedenleri:

- Yapay zekâ ve veri işleme alanında yaygın olması
- Foundry Local ile kullanılabilmesi
- SQLite desteğinin hazır bulunması
- Belge işleme kütüphanelerinin güçlü olması
- Streamlit ve FastAPI ile kolay entegrasyon sağlaması

---

## 7.2 Microsoft Foundry Local

Foundry Local, yapay zekâ modelinin cihaz üzerinde çalıştırılmasını sağlar.

Projede iki temel amaçla kullanılacaktır:

1. Embedding modeli çalıştırmak
2. Yerel dil modeliyle cevap üretmek

Bu yapı sayesinde OpenAI API veya başka bir bulut yapay zekâ servisine ihtiyaç duyulmaz.

---

## 7.3 SQLite

SQLite, sistemdeki yerel veritabanıdır.

Veritabanında şu bilgiler tutulabilir:

- Koleksiyonlar
- Yüklenen belgeler
- Belge parçaları
- Embedding vektörleri
- Soru-cevap geçmişi
- Kullanıcı geri bildirimleri
- Kaynak bilgileri

Planlanan temel tablolar:

- `collections`
- `documents`
- `chunks`
- `chat_history`
- `feedback`

SQLite tercih edilme nedenleri:

- Ayrı bir veritabanı sunucusu gerektirmemesi
- Tek dosya olarak çalışması
- Hafif olması
- Python ile kolay kullanılabilmesi
- Yerel ve çevrimdışı sistemler için uygun olması

---

## 7.4 Streamlit

Streamlit, projenin ilk çalışan kullanıcı arayüzünü oluşturmak için kullanılacaktır.

Streamlit arayüzünde şu bölümler bulunabilir:

- Ana panel
- Koleksiyon oluşturma
- Belge yükleme
- Belge listesi
- Soru sorma ekranı
- Kaynak görüntüleme
- Sohbet geçmişi
- Değerlendirme ekranı
- Ayarlar

Streamlit'in amacı hızlı şekilde çalışan bir MVP ortaya çıkarmaktır.

MVP, Minimum Viable Product ifadesinin kısaltmasıdır. Türkçe olarak temel işlevleri çalışan ilk ürün sürümü anlamına gelir.

---

## 7.5 FastAPI

FastAPI, projenin ilerleyen aşamasında API katmanı oluşturmak için kullanılacaktır.

Planlanan örnek endpointler:

- `POST /documents/upload`
- `GET /documents`
- `POST /chat/ask`
- `GET /chat/history`
- `POST /feedback`
- `GET /stats`

FastAPI sayesinde backend ile React arayüzü birbirinden ayrılabilir.

---

## 7.6 React

React, gelecekte geliştirilecek daha modern web arayüzü için planlanmaktadır.

İlk aşamada Streamlit kullanılacaktır. Daha sonra proje büyütülürse React tabanlı bir kullanıcı arayüzü hazırlanabilir.

React'in görevleri:

- Modern kullanıcı arayüzü oluşturmak
- Belge yükleme ekranını geliştirmek
- Sohbet ekranı hazırlamak
- Kaynakları görsel olarak sunmak
- FastAPI ile haberleşmek

React projenin ilk MVP aşamasında zorunlu değildir.

---

## 7.7 PyMuPDF veya pypdf

PDF dosyalarından metin çıkarmak için kullanılabilir.

Görevleri:

- PDF dosyasını açmak
- Sayfa metinlerini okumak
- Belge içeriğini tek metin halinde hazırlamak
- Sayfa ve belge metadatasını almak

---

## 7.8 python-docx

DOCX dosyalarından metin çıkarmak için kullanılır.

Görevleri:

- Word dosyasını açmak
- Paragrafları okumak
- Metni uygulamanın işleyebileceği formata dönüştürmek

---

## 7.9 NumPy

NumPy, sayısal işlemler için kullanılacaktır.

Özellikle:

- Embedding vektörlerini işlemek
- Vektör hesaplamaları yapmak
- Cosine similarity hesaplamak
- Sayısal verileri düzenlemek

için kullanılabilir.

---

## 7.10 Pandas

Pandas, test ve değerlendirme sonuçlarını düzenlemek için kullanılabilir.

Örnek kullanım alanları:

- Test sonuçlarını tabloya dönüştürmek
- Başarı oranlarını hesaplamak
- Cevap sürelerini incelemek
- Değerlendirme sonuçlarını raporlamak

---

## 7.11 Git

Git, projenin versiyon kontrol sistemi olacaktır.

Git ile:

- Kod değişiklikleri takip edilir.
- Hatalı sürümlere geri dönülebilir.
- Geliştirme adımları commitlerle kayıt altına alınır.
- Ekip çalışması daha düzenli yürütülür.

Örnek commit mesajları:

```text
init: create project structure
feat: add document loader
feat: implement chunking
feat: add sqlite schema
docs: add project brief
```

---

## 8. Arkadaki Yapay Zekâ Bileşenleri

Projede tek bir modelden ziyade iki ayrı yapay zekâ görevi bulunur.

## 8.1 Embedding Modeli

Embedding modeli, metinleri sayısal vektörlere dönüştürür.

Örneğin aşağıdaki iki cümle anlam bakımından birbirine yakındır:

- Doğal gaz sayacı nasıl çalışır?
- Gaz tüketimini ölçen cihaz nedir?

Kelimeleri birebir aynı olmasa da anlamları benzer olduğu için embedding vektörleri de birbirine yakın olur.

Bu sayede sistem kelime eşleşmesi yerine anlam benzerliğine göre arama yapabilir.

Embedding modeli şu metinleri vektöre çevirir:

- Belge parçaları
- Kullanıcı soruları

Daha sonra bu vektörler karşılaştırılır.

---

## 8.2 Yerel Dil Modeli

Yerel dil modeli, bulunan belge parçalarını kullanarak cevabı oluşturur.

Modelin görevi:

- Soruyu anlamak
- Verilen bağlamı incelemek
- Bağlamdan doğru cevabı çıkarmak
- Anlaşılır bir cevap üretmek
- Gerekirse kaynak belirtmek
- Bilgi yoksa cevap uydurmamak

Model Microsoft Foundry Local üzerinde çalışacaktır.

---

## 9. Semantic Retrieval Nedir?

Semantic Retrieval, anlamsal bilgi getirme işlemidir.

Kullanıcının sorusuyla aynı kelimeleri içermeyen ancak aynı anlamı taşıyan belge parçaları bulunabilir.

Örneğin kullanıcı:

> Sistemde kullanıcı geçmişi tutuluyor mu?

diye sorduğunda belgede:

> Soru-cevap geçmişi chat_history tablosunda saklanacaktır.

ifadesi yer alabilir.

Kelimeler tamamen aynı değildir fakat anlam benzerdir. Semantic retrieval bu ilişkiyi embedding vektörleri üzerinden bulur.

---

## 10. Cosine Similarity Nedir?

Cosine similarity, iki vektörün birbirine ne kadar benzediğini ölçmek için kullanılan yöntemdir.

Projede şu karşılaştırma yapılır:

- Kullanıcı sorusunun embedding vektörü
- Her belge parçasının embedding vektörü

Benzerlik değeri yüksek olan belge parçaları seçilir.

Örnek sonuç:

```json
[
  {
    "document_name": "manual.pdf",
    "chunk_index": 2,
    "similarity_score": 0.87
  },
  {
    "document_name": "faq.docx",
    "chunk_index": 5,
    "similarity_score": 0.79
  }
]
```

Bu sonuçlar içinden en yüksek puanlı parçalar modele bağlam olarak verilir.

---

## 11. Chunking Nedir?

Chunking, uzun belgeleri küçük metin parçalarına ayırma işlemidir.

Bir PDF dosyasının tamamını doğrudan modele göndermek verimsiz olabilir. Bu nedenle belge belirli boyutlarda parçalara ayrılır.

Örnek ayarlar:

```python
chunk_size = 800
overlap = 150
```

Burada:

- `chunk_size`: Her parçanın yaklaşık uzunluğu
- `overlap`: Ardışık parçalar arasındaki ortak metin miktarı

Overlap kullanılmasının nedeni, bir bilginin iki parça arasında bölünmesi durumunda anlam kaybını azaltmaktır.

Örnek chunk yapısı:

```json
{
  "chunk_index": 0,
  "chunk_text": "Belgeden alınan metin parçası...",
  "start_char": 0,
  "end_char": 800
}
```

---

## 12. Belge Yükleme Modülü

Belge yükleme modülü şu dosya türlerini destekleyecektir:

- PDF
- DOCX
- TXT
- Markdown

Örnek fonksiyon:

```python
def load_document(file_path: str) -> dict:
    ...
```

Örnek dönüş değeri:

```json
{
  "filename": "example.pdf",
  "file_type": "pdf",
  "text": "Belgeden çıkarılan metin...",
  "metadata": {
    "char_count": 12500,
    "word_count": 2100
  }
}
```

---

## 13. RAG Service Orchestrator

RAG servis katmanı, tüm işlemleri tek merkezden yönetecektir.

Planlanan temel fonksiyonlar:

```python
def index_document(file_path: str, collection_id: int) -> dict:
    ...
```

Bu fonksiyon:

- Belgeyi yükler
- Metni çıkarır
- Chunklara böler
- Embedding üretir
- Veritabanına kaydeder

İkinci temel fonksiyon:

```python
def ask_question(
    question: str,
    collection_id: int,
    top_k: int = 5
) -> dict:
    ...
```

Bu fonksiyon:

- Sorunun embedding değerini üretir
- En alakalı chunkları bulur
- Prompt hazırlar
- Yerel modele gönderir
- Cevabı ve kaynakları döndürür

---

## 14. Prompt Yapısı

Dil modeline verilen prompt, modelin yalnızca yüklenen belgeleri kullanmasını sağlayacak şekilde hazırlanacaktır.

Örnek sistem talimatı:

```text
Yalnızca verilen belge bağlamını kullanarak cevap ver.
Cevap bağlamda bulunmuyorsa bilgi uydurma.
Bilginin yüklenen belgelerde bulunmadığını açıkça belirt.
Mümkün olduğunda kaynak belge adını belirt.
```

Örnek kullanıcı promptu:

```text
Bağlam:
[Bulunan belge parçaları]

Soru:
[Kullanıcının sorusu]
```

Bu yapı modelin genel bilgisiyle rastgele cevap vermesini sınırlar.

---

## 15. Kaynak Gösterme

Sistem yalnızca cevap vermekle kalmayacak, cevabın hangi belge parçalarına dayandığını da gösterecektir.

Gösterilecek bilgiler:

- Belge adı
- Chunk numarası
- Benzerlik puanı
- Kullanılan metin parçası

Örnek:

```text
Kaynak: project_plan.pdf
Chunk: 12
Benzerlik: 0.84
```

Bu özellik sayesinde kullanıcı cevabı kontrol edebilir.

---

## 16. Chat History ve Feedback

Sistemde kullanıcının önceki soru ve cevapları saklanabilir.

Saklanabilecek bilgiler:

- Kullanıcı sorusu
- Üretilen cevap
- Kullanılan kaynaklar
- Sorunun sorulma zamanı
- Cevap süresi
- Kullanıcı değerlendirmesi
- Doğru veya yanlış geri bildirimi
- Kullanıcı yorumu

Bu veriler sistemin değerlendirilmesi ve geliştirilmesi için kullanılabilir.

---

## 17. Test ve Değerlendirme

Projenin doğruluğunu ölçmek için farklı soru türleri hazırlanacaktır.

Test türleri:

- Cevabı belgede bulunan sorular
- Cevabı belgede bulunmayan sorular
- Yanıltıcı sorular
- Çok genel sorular
- Boş sorular
- Eksik sorular

Değerlendirilecek ölçütler:

- Doğru chunk bulundu mu?
- Cevap belgeye dayanıyor mu?
- Kaynak gösterildi mi?
- Model bilgi uydurdu mu?
- Cevap anlaşılır mı?
- Ortalama cevap süresi nedir?

Örnek test dosyası:

```text
tests/test_questions.json
```

Örnek sonuç dosyası:

```text
tests/evaluation_results.json
```

---

## 18. Projenin Planlanan Mimari Yapısı

```text
local-rag-application-foundry-local/
│
├── backend/
│   ├── core/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── rag_service.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   └── rag.db
│   │
│   ├── prompts/
│   │   └── system_prompts.py
│   │
│   └── api/
│       └── main.py
│
├── streamlit_ui/
│   └── streamlit_app.py
│
├── react_frontend/
│   └── README.md
│
├── data/
│   ├── documents/
│   └── samples/
│
├── tests/
│   ├── test_questions.json
│   └── evaluate_rag.py
│
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   ├── final_report.md
│   └── presentation_outline.md
│
├── PROJECT_BRIEF.md
├── README.md
└── requirements.txt
```

Bu yapı modülerdir. Her bileşen ayrı dosyada tutulduğu için proje daha kolay geliştirilebilir ve test edilebilir.

---

## 19. Kullanılmayacak Teknolojiler

Proje kapsamında açıkça istenmedikçe aşağıdaki teknolojiler kullanılmayacaktır:

- GitHub Copilot
- Microsoft Copilot
- OpenAI API
- Bulut tabanlı LLM servisleri
- Pinecone
- ChromaDB
- LangChain
- Fine-tuning
- İnternetten cevap üretme
- Genel amaçlı chatbot davranışı

Burada özellikle şu ayrım önemlidir:

> Copilot bir geliştirme yardımcısı olabilir; fakat bu projenin yapay zekâ motoru değildir.

Projenin yapay zekâ motoru Microsoft Foundry Local üzerinde çalışan yerel modeldir.

---

## 20. Veri Gizliliği

Yerel çalışma yaklaşımının önemli avantajlarından biri veri gizliliğidir.

Belgeler:

- Kullanıcının bilgisayarında tutulur.
- Bulut sistemine gönderilmez.
- Harici yapay zekâ API'lerine aktarılmaz.
- Yerel veritabanında saklanır.
- Yerel model tarafından işlenir.

Bu özellik kurum içi belgeler, özel dokümanlar ve internet erişimi kısıtlı ortamlar için önemlidir.

---

## 21. Projenin Avantajları

- İnternet olmadan çalışabilir.
- Belgeler cihaz dışına çıkmaz.
- Kaynaklı cevap üretir.
- Uydurma cevap riskini azaltır.
- Farklı belge türlerini destekler.
- Hafif ve modüler yapıdadır.
- Streamlit ile hızlı demo hazırlanabilir.
- FastAPI ve React ile büyütülebilir.
- SQLite sayesinde ek sunucu gerektirmez.
- Eğitim ve akademik proje için uygundur.

---

## 22. Projenin Sınırlamaları

- Büyük belge koleksiyonlarında SQLite tabanlı benzerlik araması yavaşlayabilir.
- Yerel modelin başarısı bilgisayar donanımına bağlıdır.
- Küçük modeller büyük bulut modelleri kadar güçlü olmayabilir.
- Chunk boyutu yanlış seçilirse retrieval kalitesi düşebilir.
- Tarama görüntüsü içeren PDF dosyaları için OCR gerekebilir.
- Çok karmaşık tablolar ve görseller doğrudan metne çevrilemeyebilir.
- Model tamamen bağlama bağlı olduğu için belgede bulunmayan bilgiyi veremez.

---

## 23. Gelecekte Yapılabilecek Geliştirmeler

- React tabanlı gelişmiş arayüz
- FastAPI servis katmanı
- Kullanıcı yönetimi
- Rol tabanlı yetkilendirme
- Daha güçlü embedding modeli
- Daha gelişmiş vektör arama
- OCR desteği
- Tablo ve görsel analizi
- Birden fazla koleksiyon desteği
- Belge silme ve yeniden indeksleme
- Cevap kalitesi ölçüm paneli
- Kaynak cümlelerini vurgulama
- Dosya bazlı erişim izinleri
- Çoklu dil desteği

---

## 24. Kısa Sunum Metni

Bu proje, Microsoft Foundry Local kullanılarak geliştirilen tamamen yerel bir RAG uygulamasıdır. Kullanıcı PDF, DOCX, TXT veya Markdown belgelerini sisteme yükler. Sistem bu belgeleri parçalara ayırır, embedding vektörleri oluşturur ve SQLite veritabanında saklar. Kullanıcı soru sorduğunda en alakalı belge parçaları semantic retrieval yöntemiyle bulunur ve yerel dil modeline bağlam olarak verilir. Model cevabını yalnızca bu belgelere dayanarak üretir. Cevap belgelerde bulunmuyorsa bilgi uydurmaz. Projede Copilot kullanılmamaktadır; yapay zekâ altyapısı Microsoft Foundry Local üzerinde çalışan yerel modelden oluşmaktadır.

---

## 25. Tek Cümlelik Proje Tanımı

> Microsoft Foundry Local, RAG, SQLite ve Python kullanılarak geliştirilen; yüklenen belgelerden kaynaklı cevap üreten, tamamen yerel ve çevrimdışı çalışan yapay zekâ destekli doküman soru-cevap uygulamasıdır.
