# T3PROJE - AI Destekli Veri İşleme ve Soru-Cevap Üretim Sistemi

Bu proje, AI teknolojileri kullanarak çeşitli veri işleme görevlerini otomatikleştiren araçlar koleksiyonudur. Beslenme, sağlık ve genel konularda PDF'lerden soru-cevap çiftleri üretmek, veri temizleme, veri çoğaltma ve analiz işlemleri gerçekleştirebilirsiniz.

## 🚀 Proje Özeti

Bu proje 4 ana modülden oluşmaktadır:

1. **kaynakkaldir** - JSON veri temizleme ve AI ile veri çoğaltma araçları
2. **PythonNLP** - PDF'den soru-cevap üretimi (Gemini AI entegrasyonlu)
3. **PythonNLP2** - Veri analizi ve birleştirme araçları
4. **PythonNLPRAG** - Gelişmiş PDF işleme ve soru-cevap üretimi sistemi

## 📋 Genel Gereksinimler

- **Python 3.7+** (Önerilen: Python 3.8 veya üzeri)
- **Google Gemini API Anahtarı** (AI işlemler için)
- **İnternet Bağlantısı** (API çağrıları için)
- **Windows PowerShell** (komut satırı işlemleri için)

## 🛠️ Hızlı Başlangıç

### 1. Projeyi İndirin
```powershell
# Projeyi indirdikten sonra ana klasöre gidin
cd "c:\Users\bilal\Desktop\T3PROJE"
```

### 2. Python Kurulumu Kontrolü
```powershell
python --version
```

### 3. Modül Seçimi
Hangi işlemi yapmak istediğinize göre uygun klasöre gidin:

```powershell
# JSON temizleme ve veri çoğaltma için
cd kaynakkaldir

# PDF'den soru-cevap üretimi için (Basit)
cd PythonNLP

# Veri analizi ve birleştirme için
cd PythonNLP2

# Gelişmiş PDF işleme için
cd PythonNLPRAG
```

### 4. Gerekli Paketleri Yükleyin
Her klasörde `requirements.txt` dosyası bulunmaktadır:
```powershell
pip install -r requirements.txt
```

## 📁 Proje Yapısı

```
T3PROJE/
├── README.md                    # Bu dosya - Ana kılavuz
├── LICENSE                      # Lisans bilgileri
│
├── kaynakkaldir/               # JSON Temizleme ve Veri Çoğaltma
│   ├── README.md               # Detaylı kullanım kılavuzu
│   ├── requirements.txt        # Python gereksinimleri
│   ├── config.json            # API konfigürasyonu
│   ├── kaynak_kaldir.py       # Basit JSON temizleme
│   ├── gelismis_kaynak_kaldir.py # Gelişmiş JSON temizleme
│   ├── vericogaltma.py        # Basit veri çoğaltma
│   ├── gelismis_vericogaltma.py # Gelişmiş veri çoğaltma
│   └── [test dosyaları].json  # Örnek veri dosyaları
│
├── PythonNLP/                 # PDF'den Soru-Cevap Üretimi
│   ├── README.md              # Detaylı kullanım kılavuzu
│   ├── requirements.txt       # Python gereksinimleri
│   ├── main.py               # Ana kontrol sistemi
│   ├── pdf_to_qa_gemini.py   # PDF işleme motoru
│   ├── analyze_qa_data.py    # Veri analizi
│   ├── setup_qa_generator.py # Kurulum scripti
│   └── pdfs/                 # PDF dosyaları klasörü
│
├── PythonNLP2/               # Veri Analizi ve Birleştirme
│   ├── README.md             # Detaylı kullanım kılavuzu
│   ├── test.py              # CSV birleştirme
│   ├── test2.py             # Veri analizi
│   ├── veritemizleme.py     # Veri temizleme
│   └── [veri dosyaları]     # CSV ve JSON dosyaları
│
└── PythonNLPRAG/            # Gelişmiş PDF İşleme Sistemi
    ├── README.md            # Detaylı kullanım kılavuzu
    ├── requirements.txt     # Python gereksinimleri
    ├── config.json         # Sistem konfigürasyonu
    ├── main.py            # Ana işleme motoru
    ├── main_enhanced.py   # Gelişmiş özellikler
    └── output_json/       # Çıktı dosyaları
```

## 🎯 Kullanım Senaryoları

### 📄 PDF'den Soru-Cevap Üretmek İstiyorsanız:
- **Basit kullanım**: `PythonNLP` klasörünü kullanın
- **Gelişmiş özellikler**: `PythonNLPRAG` klasörünü kullanın

### 🧹 JSON Verilerini Temizlemek İstiyorsanız:
- `kaynakkaldir` klasörünü kullanın
- Kaynak bilgilerini kaldırma ve veri çoğaltma işlemleri

### 📊 Veri Analizi ve Birleştirme İçin:
- `PythonNLP2` klasörünü kullanın
- CSV dosyalarını birleştirme ve analiz etme

## ⚙️ API Anahtarı Kurulumu

Tüm AI işlemler için Google Gemini API anahtarına ihtiyacınız vardır:

1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Yeni API anahtarı oluşturun
3. İlgili dosyalardaki `YOUR_API_KEY_HERE` kısımlarını değiştirin

## 🔧 Sorun Giderme

### Yaygın Hatalar:
- **ModuleNotFoundError**: `pip install -r requirements.txt` komutunu çalıştırın
- **API Key Error**: API anahtarınızı doğru konfigüre ettiğinizden emin olun
- **File Not Found**: Dosya yollarının doğru olduğunu kontrol edin

### Destek:
Her klasörde detaylı README dosyaları bulunmaktadır. Özel kullanım talimatları için ilgili klasörün README.md dosyasını inceleyin.

## 📈 Performans İpuçları

1. **API Limitleri**: Çok fazla eşzamanlı istek göndermekten kaçının
2. **Büyük Dosyalar**: Büyük PDF'leri parçalara bölerek işleyin
3. **Veri Yedekleme**: İşlem öncesi verilerinizi yedekleyin
4. **İnternet Bağlantısı**: Kararlı internet bağlantısı kullanın

## 📝 Lisans

Bu proje açık kaynak lisansı altında yayınlanmıştır. Detaylar için `LICENSE` dosyasını inceleyin.

## 🆕 Güncellemeler

- **v1.0**: Temel PDF işleme ve veri temizleme özellikleri
- **v1.1**: Gelişmiş AI entegrasyonu ve çoklu API desteği
- **v1.2**: Veri analizi ve birleştirme araçları eklendi

---

**Not**: Her modül için detaylı kullanım kılavuzları ilgili klasörlerdeki README.md dosyalarında bulunmaktadır.
