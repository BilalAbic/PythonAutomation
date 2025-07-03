# T3PROJE - AI Destekli Veri İşleme ve Soru-Cevap Üretim Sistemi

Bu proje, AI teknolojileri kullanarak çeşitli veri işleme görevlerini otomatikleştiren araçlar koleksiyonudur. Beslenme, sağlık ve genel konularda PDF'lerden soru-cevap çiftleri üretmek, veri temizleme, veri çoğaltma ve analiz işlemleri gerçekleştirebilirsiniz.

## 🚀 Proje Özeti

Bu proje 4 ana modülden oluşmaktadır:

1. **kaynakkaldir** - JSON veri temizleme ve AI ile veri çoğaltma araçları
2. **PythonNLP** - PDF'den soru-cevap üretimi (Gemini AI entegrasyonlu)
3. **PythonNLP2** - Veri analizi ve birleştirme araçları
4. **PythonNLPRAG** - Gelişmiş PDF işleme ve soru-cevap üretimi sistemi
5. **DataMin2x** - Ultra güvenli sağlık chatbot veri çoğaltma sistemi

## 🔐 GÜVENLİK VE KURULUM ÖNCESİ ÖNEMLİ NOTLAR

### ⚠️ API Anahtarı Güvenliği
Bu proje Gemini AI API anahtarları kullanır. **Güvenlik için aşağıdaki adımları mutlaka takip edin:**

1. **API anahtarlarınızı asla Git'e commit etmeyin**
2. **Her projede config_example.json'dan config.json oluşturun**
3. **Gerçek API anahtarlarınızı sadece config.json'a yazın**

### 🛠️ İlk Kurulum Adımları

#### 1. Konfigürasyon Dosyalarını Oluşturun
Her proje klasöründe:
```powershell
# Örnek dosyayı kopyalayın
copy config_example.json config.json

# Gerçek API anahtarlarınızı config.json'a ekleyin
```

#### 2. API Anahtarı Alın
- [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
- Yeni API anahtarı oluşturun
- **Bu anahtarı güvenli şekilde saklayın**

#### 3. Proje Konfigürasyonu
```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2"
  ],
  // diğer ayarlar...
}
```

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

# Ultra güvenli sağlık veri çoğaltma için
cd DataMin2x
```

### 4. Güvenli Konfigürasyon
```powershell
# Her projede önce config dosyası oluşturun
copy config_example.json config.json

# config.json'ı düzenleyip API anahtarınızı ekleyin
```

### 5. Gerekli Paketleri Yükleyin
Her klasörde `requirements.txt` dosyası bulunmaktadır:
```powershell
pip install -r requirements.txt
```

## 📁 Proje Yapısı

```
T3PROJE/
├── README.md                    # Bu dosya - Ana kılavuz
├── LICENSE                      # Lisans bilgileri
├── .gitignore                   # Git güvenlik kuralları
│
├── kaynakkaldir/               # JSON Temizleme ve Veri Çoğaltma
│   ├── README.md               # Detaylı kullanım kılavuzu
│   ├── requirements.txt        # Python gereksinimleri
│   ├── config_example.json     # Güvenli config şablonu
│   ├── kaynak_kaldir.py       # Basit JSON temizleme
│   ├── gelismis_kaynak_kaldir.py # Gelişmiş JSON temizleme
│   ├── vericogaltma.py        # Basit veri çoğaltma
│   ├── gelismis_vericogaltma.py # Gelişmiş veri çoğaltma
│   └── [test dosyaları].json  # Örnek veri dosyaları
│
├── PythonNLP/                 # PDF'den Soru-Cevap Üretimi
│   ├── README.md              # Detaylı kullanım kılavuzu
│   ├── requirements.txt       # Python gereksinimleri
│   ├── config_example.json    # Güvenli config şablonu
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
├── PythonNLPRAG/            # Gelişmiş PDF İşleme Sistemi
│   ├── README.md            # Detaylı kullanım kılavuzu
│   ├── requirements.txt     # Python gereksinimleri
│   ├── config_example.json  # Güvenli config şablonu
│   ├── main.py             # Ana işleme motoru
│   ├── enhanced_pdf_processor.py # Gelişmiş özellikler
│   ├── pdf_api_manager.py   # API yönetimi
│   └── output_json/         # Çıktı dosyaları
│
└── DataMin2x/               # Ultra Güvenli Sağlık Veri Çoğaltma
    ├── README.md            # Detaylı kullanım kılavuzu
    ├── requirements.txt     # Python gereksinimleri
    ├── config_example.json  # Güvenli config şablonu
    ├── data_augmenter.py   # Ana veri çoğaltma motoru
    ├── add_api_key.py      # Canlı API key yönetimi
    ├── safety_monitor.py   # Güvenlik izleme
    └── output/             # Çıktı dosyaları
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

### 🏥 Sağlık Verileri İçin Ultra Güvenli İşleme:
- `DataMin2x` klasörünü kullanın
- Medikal doğrulama ve güvenlik kontrolleri

## 🔐 Güvenlik Özellikleri

### API Anahtarı Koruması
- **`.gitignore`** ile config dosyaları Git'ten hariç tutulmuştur
- **`config_example.json`** dosyaları placeholder anahtarlar içerir
- **Gerçek API anahtarları** sadece local `config.json` dosyalarında saklanır

### Veri Güvenliği
- Otomatik backup sistemi
- Checkpoint/resume özelliği
- Emergency stop mekanizması
- Real-time monitoring

### Proje Güvenliği
```
# Bu dosyalar Git'e gönderilmez:
config.json           # Gerçek API anahtarları
logs/                 # Log dosyaları
output/               # Çıktı dosyaları
backups/              # Yedek dosyaları
checkpoints/          # Checkpoint dosyaları
```

## ⚙️ API Anahtarı Kurulumu

### 1. API Anahtarı Alın
1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
2. Yeni API anahtarı oluşturun
3. **Bu anahtarı güvenli şekilde kopyalayın**

### 2. Config Dosyası Oluşturun
```powershell
# Her proje klasöründe
copy config_example.json config.json
```

### 3. API Anahtarını Ekleyin
`config.json` dosyasını açın ve placeholder'ları değiştirin:
```json
{
  "api_keys": [
    "AIzaSyYour_Real_API_Key_Here"
  ]
}
```

## 🔧 Sorun Giderme

### Yaygın Hatalar:
- **ModuleNotFoundError**: `pip install -r requirements.txt` komutunu çalıştırın
- **API Key Error**: API anahtarınızı doğru konfigüre ettiğinizden emin olun
- **File Not Found**: Dosya yollarının doğru olduğunu kontrol edin
- **Config Error**: `config_example.json`'dan `config.json` oluşturduğunuzdan emin olun

### Güvenlik Sorunları:
- **API anahtarı görünür**: `git status` ile config.json'ın staged olmadığını kontrol edin
- **Permission denied**: Klasör yazma izinlerini kontrol edin

### Destek:
Her klasörde detaylı README dosyaları bulunmaktadır. Özel kullanım talimatları için ilgili klasörün README.md dosyasını inceleyin.

## 📈 Performans İpuçları

1. **API Limitleri**: Çok fazla eşzamanlı istek göndermekten kaçının
2. **Büyük Dosyalar**: Büyük PDF'leri parçalara bölerek işleyin
3. **Veri Yedekleme**: İşlem öncesi verilerinizi yedekleyin
4. **İnternet Bağlantısı**: Kararlı internet bağlantısı kullanın
5. **Çoklu API Anahtarı**: Hız için birden fazla API anahtarı kullanın

## 📝 Lisans

Bu proje açık kaynak lisansı altında yayınlanmıştır. Detaylar için `LICENSE` dosyasını inceleyin.

## 🆕 Güncellemeler

- **v1.0**: Temel PDF işleme ve veri temizleme özellikleri
- **v1.1**: Gelişmiş AI entegrasyonu ve çoklu API desteği
- **v1.2**: Veri analizi ve birleştirme araçları eklendi
- **v2.0**: 🔐 **GÜVENLİK GÜNCELLEMESİ** - Config güvenliği, .gitignore kuralları
- **v2.1**: Ultra güvenli sağlık veri işleme sistemi eklendi

---

**⚠️ GÜVENLİK HATIRLATMASI**: API anahtarlarınızı asla Git'e commit etmeyin. Her zaman `config_example.json`'dan `config.json` oluşturun ve gerçek anahtarlarınızı oraya yazın.
