# PythonNLP - PDF'den Soru-Cevap Üretimi Sistemi

Bu modül, beslenme ve sağlık konularındaki PDF dosyalarından Google Gemini AI kullanarak otomatik soru-cevap çiftleri oluşturan kapsamlı bir sistemdir.

## 🚀 Modül Özellikleri

- **Otomatik PDF İşleme**: Klasördeki tüm PDF'leri otomatik olarak işler
- **AI Destekli Soru-Cevap Üretimi**: Google Gemini API ile kaliteli soru-cevap çiftleri
- **Çoklu Format Desteği**: JSON, CSV, JSONL formatlarında çıktı
- **Veri Analizi**: Oluşturulan verilerin detaylı analizi
- **Kalite Filtreleme**: Düşük kaliteli verileri otomatik filtreleme
- **Konu Bazlı Gruplama**: Kaynaklara göre veri gruplama
- **Kullanıcı Dostu Arayüz**: Menü tabanlı kontrol sistemi

## 📋 Gereksinimler

- **Python 3.7+** (Önerilen: 3.8+)
- **Google Gemini API Anahtarı**
- **İnternet Bağlantısı**
- **PDF Dosyaları** (işlenecek içerik)

### Python Paketleri:
```
PyMuPDF==1.23.9
google-generativeai>=0.3.2
requests==2.31.0
pandas==2.1.4
numpy==1.24.3
```

## ⚙️ Kurulum

### Yöntem 1: Hızlı Kurulum (Önerilen)
```powershell
# Ana sistemi başlatın
python main.py

# Menüden "1 - Sistem kurulumu yap" seçeneğini seçin
```

### Yöntem 2: Manuel Kurulum
```powershell
# 1. Gerekli paketleri yükle
pip install -r requirements.txt

# 2. Kurulum scriptini çalıştır
python setup_qa_generator.py

# 3. API anahtarını ayarla
python setup_api_key.py
```

### 3. API Anahtarı Yapılandırması
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Yeni API anahtarı oluşturun
3. `pdf_to_qa_gemini.py` dosyasında `YOUR_GEMINI_API_KEY_HERE` kısmını anahtarınızla değiştirin

## 📁 Dosya Yapısı ve İşlevleri

### Ana Kontrol Sistemi

#### 1. `main.py` - Ana Menü ve Sistem Yöneticisi
**Ne yapar:**
- Sistem durumunu kontrol eder
- Kullanıcı dostu menü sağlar
- Tüm işlemleri koordine eder
- Kurulum ve konfigürasyon yönetimi

**Nasıl çalıştırılır:**
```powershell
python main.py
```

**Menü Seçenekleri:**
1. Sistem kurulumu yap
2. PDF'leri işle ve soru-cevap üret
3. Mevcut verileri analiz et
4. Sistem durumunu kontrol et
5. Çıkış

### PDF İşleme Motoru

#### 2. `pdf_to_qa_gemini.py` - PDF İşleme ve AI Entegrasyonu
**Ne yapar:**
- PDF dosyalarını metin ve görsel olarak işler
- Gemini AI ile soru-cevap çiftleri üretir
- Çoklu format çıktı sağlar
- Hata yönetimi ve logging

**Nasıl çalıştırılır:**
```powershell
# Doğrudan çalıştırma (gelişmiş kullanıcılar için)
python pdf_to_qa_gemini.py
```

**Çalıştırmadan önce yapılması gerekenler:**
1. API anahtarını dosyada güncelleyin
2. `pdfs/` klasörüne PDF dosyalarını yerleştirin
3. İşlem limitlerini kontrol edin

### Yardımcı Araçlar

#### 3. `run_qa_generation.py` - Hızlı Başlatma Scripti
**Ne yapar:**
- Tek komutla PDF işleme başlatır
- Ön kontrolleri yapar
- Hızlı kurulum sağlar

**Nasıl çalıştırılır:**
```powershell
python run_qa_generation.py
```

#### 4. `analyze_qa_data.py` - Veri Analizi ve Dönüştürme
**Ne yapar:**
- Oluşturulan verileri analiz eder
- İstatistik raporları üretir
- Format dönüştürmeleri yapar
- Kalite kontrolü

**Nasıl çalıştırılır:**
```powershell
python analyze_qa_data.py
```

#### 5. `setup_qa_generator.py` - Kurulum Scripti
**Ne yapar:**
- Sistem gereksinimlerini kontrol eder
- Klasör yapısını oluşturur
- Test işlemleri yapar

#### 6. `setup_api_key.py` - API Anahtar Yapılandırıcı
**Ne yapar:**
- API anahtarını güvenli şekilde kaydeder
- Anahtar geçerliliğini test eder

### Konfigürasyon Dosyaları

#### 7. `config.json` - Sistem Ayarları
**İçeriği:**
- API konfigürasyonu
- İşlem parametreleri
- Çıktı formatları
- Kalite filtreleri

## 🚀 Kullanım Senaryoları

### Scenario 1: İlk Kez Kullanım
```powershell
# 1. Ana sistemi başlatın
python main.py

# 2. Menüden "1" seçin (Sistem kurulumu)
# 3. API anahtarınızı girin
# 4. PDF'lerinizi pdfs/ klasörüne yerleştirin
# 5. Menüden "2" seçin (PDF işleme)
```

### Scenario 2: PDF'leri Toplu İşleme
```powershell
# Hızlı işleme için
python run_qa_generation.py
```

### Scenario 3: Veri Analizi
```powershell
# Oluşturulan verileri analiz etmek için
python analyze_qa_data.py
```

## 📊 Çıktı Formatları

Sistem aşağıdaki formatlarda çıktı üretir:

### 1. JSON Format
```json
[
  {
    "soru": "Protein ihtiyacı nasıl hesaplanır?",
    "cevap": "Günlük protein ihtiyacı vücut ağırlığının kg başına 0.8-1.2 gram...",
    "kaynak": "beslenme_rehberi.pdf",
    "sayfa": 15
  }
]
```

### 2. CSV Format
```csv
soru,cevap,kaynak,sayfa
"Protein ihtiyacı nasıl hesaplanır?","Günlük protein ihtiyacı...","beslenme_rehberi.pdf",15
```

### 3. JSONL Format (ML için optimize)
```
{"soru": "...", "cevap": "...", "kaynak": "...", "sayfa": ...}
{"soru": "...", "cevap": "...", "kaynak": "...", "sayfa": ...}
```

## ⚠️ Önemli Notlar

### PDF Gereksinimleri:
- PDF'ler metin çıkarılabilir formatta olmalı
- Görsel içerikli PDF'ler desteklenir
- Maksimum dosya boyutu: 100MB
- Desteklenen diller: Türkçe, İngilizce

### API Limitleri:
- Gemini API: Dakikada 60 istek
- Büyük PDF'ler için işlem süresi uzun olabilir
- İnternet bağlantısı kesintisinde işlem durur

### Veri Kalitesi:
- Oluşturulan sorular otomatik filtrelenir
- Manuel kalite kontrolü önerilir
- Tekrarlı içerikler temizlenir

## 🔧 Sorun Giderme

### Yaygın Hatalar:

1. **PDF Okuma Hatası:**
```powershell
# PDF'in metin çıkarılabilir olduğunu kontrol edin
python -c "import fitz; print(fitz.open('pdfs/dosya.pdf')[0].get_text())"
```

2. **API Anahtar Hatası:**
```powershell
# API anahtarını test edin
python setup_api_key.py
```

3. **Bağımlılık Hatası:**
```powershell
# Paketleri yeniden yükleyin
pip install -r requirements.txt --force-reinstall
```

### Debug Modu:
```powershell
# Detaylı hata mesajları için
python main.py --debug
```

## 📈 Performans İyileştirme

- **Küçük PDF'lerle başlayın** (test için)
- **API çağrı sıklığını optimize edin**
- **Çıktı dosyalarını düzenli temizleyin**
- **System kaynakları limitlerini göz önünde bulundurun**
├── requirements.txt          # Python gereksinimleri
├── pdfs/                     # PDF dosyalarını buraya koyun
│   ├── dosya1.pdf
│   ├── dosya2.pdf
│   └── ...
└── çıktı dosyaları/
    ├── pdf_qa_pairs.json     # Ana soru-cevap verisi
    ├── qa_pairs_export.csv   # CSV formatında
    ├── training_data.jsonl   # AI eğitimi için
    ├── qa_by_topics.json     # Konulara göre gruplu
    └── quality_qa_pairs.json # Filtrelenmiş kaliteli veri
```

## 🎯 Kullanım

### Ana Sistem
```bash
python main.py
```

### Doğrudan Çalıştırma
```bash
# PDF'leri işle
python run_qa_generation.py

# Verileri analiz et
python analyze_qa_data.py
```

## 📊 Çıktı Formatları

### JSON Format
```json
[
  {
    "soru": "Beslenme nedir?",
    "cevap": "Beslenme, vücudun büyüme, gelişme ve sağlıklı yaşam için gerekli besin öğelerini alması sürecidir.",
    "kaynak": "beslenme-temelleri.pdf"
  }
]
```

### CSV Format
Excel ve diğer araçlarda kullanım için.

### JSONL Format (AI Eğitimi)
```jsonl
{"instruction": "Soru", "input": "", "output": "Cevap", "source": "kaynak.pdf"}
```

## ⚡ Performans

- **İşleme Hızı**: PDF başına ~2-5 dakika
- **Soru-Cevap Üretimi**: Sayfa başına 5-8 çift
- **API Limitleri**: Dakikada 60 istek (otomatik bekleme)

## 🔧 Konfigürasyon

### Metin Parçalama
```python
chunk_size = 3000  # Karakter sayısı
```

### Soru-Cevap Miktarı
```python
# prompt içinde ayarlanabilir
"5-8 adet soru-cevap çifti oluştur"
```

### Kalite Filtreleme
```python
min_answer_length = 10  # Minimum cevap kelime sayısı
```

## 🛠️ Sorun Giderme

### API Hatası
- API anahtarının doğru olduğundan emin olun
- İnternet bağlantısını kontrol edin
- API limitlerini kontrol edin

### PDF Okuma Hatası
- PDF dosyasının bozuk olmadığından emin olun
- Dosya izinlerini kontrol edin
- OCR gereksinimi olabilir (taranmış PDF'ler için)

### Bellek Sorunu
- Büyük PDF'leri küçük parçalara bölün
- `chunk_size` değerini azaltın

## 📈 Veri Kalitesi

Sistem aşağıdaki kalite kontrolleri yapar:
- Minimum soru uzunluğu (5 kelime)
- Minimum cevap uzunluğu (10 kelime)
- Soru işareti kontrolü
- Cevap/soru oranı kontrolü

## 🔄 Güncelleme

```bash
# Paketleri güncelle
pip install -r requirements.txt --upgrade

# Sistem dosyalarını yeniden indir
git pull origin main
```

## 📞 Destek

Sorunlar için:
1. `main.py` menüsünden "Örnek verileri göster" ile test edin
2. Log dosyalarını kontrol edin
3. API anahtarını yeniden oluşturun

## 📝 Notlar

- İşlem uzun sürebilir (100+ PDF için saatler)
- İnternet bağlantısı kesintisiz olmalı
- API maliyetlerini göz önünde bulundurun
- Ara kayıtlar otomatik olarak yapılır

## 🎉 Örnekler

70+ beslenme ve sağlık PDF'si ile test edilmiş, binlerce kaliteli soru-cevap çifti üretmiştir.
