# PDF'den Soru-Cevap Üretimi Sistemi

Bu sistem, beslenme ve sağlık konularındaki PDF dosyalarından Google Gemini AI kullanarak otomatik soru-cevap çiftleri oluşturur.

## 🚀 Özellikler

- **Otomatik PDF İşleme**: Klasördeki tüm PDF'leri otomatik olarak işler
- **AI Destekli Soru-Cevap Üretimi**: Google Gemini API ile kaliteli soru-cevap çiftleri
- **Çoklu Format Desteği**: JSON, CSV, JSONL formatlarında çıktı
- **Veri Analizi**: Oluşturulan verilerin detaylı analizi
- **Kalite Filtreleme**: Düşük kaliteli verileri otomatik filtreleme
- **Konu Bazlı Gruplama**: Kaynaklara göre veri gruplama

## 📋 Gereksinimler

- Python 3.7+
- Google Gemini API anahtarı
- İnternet bağlantısı

## ⚙️ Kurulum

### 1. Hızlı Başlangıç
```bash
python main.py
```
Ana menüden "Sistem kurulumu yap" seçeneğini seçin.

### 2. Manuel Kurulum
```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Kurulum scriptini çalıştır
python setup_qa_generator.py
```

### 3. API Anahtarı Ayarlama
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Yeni API anahtarı oluşturun
3. `pdf_to_qa_gemini.py` dosyasındaki `YOUR_GEMINI_API_KEY_HERE` kısmını anahtarınızla değiştirin

## 📁 Dosya Yapısı

```
d:\PythonNLP\
├── main.py                    # Ana kontrol sistemi
├── pdf_to_qa_gemini.py       # PDF işleme ve AI entegrasyonu
├── run_qa_generation.py      # Hızlı başlatma scripti
├── analyze_qa_data.py        # Veri analizi ve dönüştürme
├── setup_qa_generator.py     # Kurulum scripti
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
