# PythonNLPRAG - Gelişmiş PDF İşleme ve Soru-Cevap Üretimi Sistemi

Bu modül, profesyonel düzeyde PDF'den soru-cevap dataset üretimi için gelişmiş özellikler sunan production-ready bir sistemdir. Çoklu makine desteği, adaptif rate limiting ve güçlü API anahtar yönetimi ile donatılmıştır.

## 🔐 GÜVENLİK VE KURULUM ÖNCESİ ÖNEMLİ NOTLAR

### ⚠️ API Anahtarı Güvenliği
**MUTLAKA OKUMANIZ GEREKEN GÜVENLİK BİLGİLERİ:**

1. **API anahtarlarınızı asla Git'e commit etmeyin**
2. **`config_example.json`'dan `config.json` oluşturun**
3. **Gerçek API anahtarlarınızı sadece `config.json`'a yazın**

### 🛠️ Güvenli Kurulum Adımları

#### 1. Config Dosyası Oluşturun
```powershell
# Bu klasörde (PythonNLPRAG):
copy config_example.json config.json
```

#### 2. API Anahtarları Ekleyin
`config.json` dosyasını açın ve placeholder'ları değiştirin:
```json
{
  "api_keys": [
    "AIzaSyYour_Real_API_Key_Here_1",
    "AIzaSyYour_Real_API_Key_Here_2",
    "AIzaSyYour_Real_API_Key_Here_3"
  ]
}
```

#### 3. API Anahtarını Alın
- [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
- Yeni API anahtarları oluşturun
- **Bu anahtarları güvenli şekilde saklayın**

## 🚀 Modül Özellikleri

- **Production-Ready Mimari**: Endüstriyel seviye kod kalitesi
- **Çoklu Makine Desteği**: Dağıtık işleme için multi-machine support
- **Adaptif Rate Limiting**: Akıllı API çağrı yönetimi
- **Güçlü API Yönetimi**: Otomatik anahtar rotasyonu ve failover
- **Resume Functionality**: Kesintiye uğrayan işlemleri kaldığı yerden devam ettirme
- **Detaylı Logging**: Kapsamlı hata takibi ve performans izleme
- **Yapılandırılabilir Çıktı**: Esnek dataset formatları
- **Gelişmiş API Manager**: Hot-swap API key desteği

## 📋 Gereksinimler

- **Python 3.8+** (Önerilen)
- **Google Gemini API Anahtarı** (Çoklu anahtar desteklenir)
- **Yeterli RAM** (Büyük PDF'ler için 4GB+)
- **Kararlı İnternet Bağlantısı**

### Python Paketleri:
```
google-generativeai
PyMuPDF
Pillow
```

## ⚙️ Kurulum

### 1. Gerekli Paketleri Yükleyin
```powershell
pip install -r requirements.txt
```

### 2. Güvenli Konfigürasyon
```powershell
# Config dosyası oluşturun
copy config_example.json config.json

# config.json'ı düzenleyip gerçek API anahtarlarınızı ekleyin
```

### 3. Konfigürasyon Ayarları
`config.json` dosyasında ayarlayın:

```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2", 
    "YOUR_GEMINI_API_KEY_3"
  ],
  "model_name": "gemini-1.5-flash-latest",
  "pdf_folder": "pdfs",
  "output_folder": "output_json",
  "output_filename": "toplam_egitim_veriseti.jsonl",
  "max_questions_per_pdf": 30,
  "num_workers": 2,
  "machine_id": 0,
  "total_machines": 1,
  "adaptive_delay": true,
  "min_delay_between_calls": 5,
  "max_delay_between_calls": 30
}
```

## 📁 Dosya Yapısı ve İşlevleri

### Ana İşleme Motoru

#### 1. `main.py` - Production-Ready İşleme Sistemi
**Ne yapar:**
- PDF dosyalarını sayfa sayfa işler
- Gemini AI ile soru-cevap üretir
- Adaptif rate limiting uygular
- Çoklu API anahtar yönetimi
- Hata toleransı ve recovery
- Thread-safe işlemler

**Güvenli çalıştırma:**
```powershell
# Önce config.json oluşturun ve API anahtarlarını ekleyin
copy config_example.json config.json

# Sonra çalıştırın
python main.py
```

#### 2. `enhanced_pdf_processor.py` - Gelişmiş PDF İşleyici
**Ne yapar:**
- Gelişmiş görsel işleme
- Multi-modal AI entegrasyonu
- Zengin metadata çıktısı
- Config hot-reload desteği

#### 3. `pdf_api_manager.py` - Gelişmiş API Yönetimi
**Ne yapar:**
- API anahtarlarını test eder
- Otomatik failover
- Hot-swap API key desteği
- Performans izleme

**Özellikler:**
- 🔄 **Hot Reload**: API anahtarları çalışma sırasında eklenebilir
- 🧪 **Auto Test**: Yeni anahtarlar otomatik test edilir
- 📊 **Live Monitoring**: Aktif anahtar sayısı takibi
- ⚡ **Instant Update**: Sistem durmuyor

#### 4. `add_api_key_pdf.py` - Canlı API Key Yönetimi
**Ne yapar:**
- Sistem çalışırken API anahtarı ekleme
- Otomatik test ve doğrulama
- Config dosyası güncelleme

**Kullanım:**
```powershell
# Ana sistem çalışırken başka bir terminal açın:
python add_api_key_pdf.py
```

### Konfigürasyon Yönetimi

#### 5. `config_example.json` - Güvenli Config Şablonu
**İçeriği:**
```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",
    "YOUR_GEMINI_API_KEY_3"
  ],
  // diğer ayarlar placeholder olarak
}
```

**Önemli:** Bu dosya Git'e commit edilir ama gerçek API anahtarları içermez.

#### 6. `config.json` - Gerçek Konfigürasyon
**Önemli:** Bu dosya `.gitignore` ile Git'ten hariç tutulmuştur.

## 🚀 Kullanım Senaryoları

### Scenario 1: İlk Kez Güvenli Kullanım
```powershell
# 1. Config dosyası oluşturun
copy config_example.json config.json

# 2. API anahtarlarınızı config.json'a ekleyin
# config.json dosyasını açın ve YOUR_GEMINI_API_KEY_X kısımlarını değiştirin

# 3. PDF'leri yerleştirin
mkdir pdfs
# PDF dosyalarınızı pdfs/ klasörüne kopyalayın

# 4. İşlemi başlatın
python main.py
```

### Scenario 2: Çoklu Makine Dağıtık İşleme
**Makine 1 (config.json):**
```json
{
  "machine_id": 0,
  "total_machines": 3,
  "api_keys": ["key1", "key2"]
}
```

**Makine 2 (config.json):**
```json
{
  "machine_id": 1,
  "total_machines": 3,
  "api_keys": ["key3", "key4"]
}
```

### Scenario 3: Çalışma Sırasında API Key Ekleme
```powershell
# Terminal 1: Ana işlem
python main.py

# Terminal 2: Yeni API key ekle
python add_api_key_pdf.py
# Sistem 5 batch içinde yeni anahtarları algılayacak
```

### Scenario 4: API Test ve Doğrulama
```powershell
# API anahtarlarınızı test edin
python api_test.py
```

## 📊 Çıktı Formatları

### JSONL Format (ML için optimize)
```jsonl
{"question": "Hangi besinler protein açısından zengindir?", "answer": "Et, balık, yumurta, baklagiller...", "source": "beslenme.pdf", "page": 15, "metadata": {"confidence": 0.95, "timestamp": "2025-06-28T10:30:00Z"}}
```

### JSON Format
```json
[
  {
    "question": "Hangi besinler protein açısından zengindir?",
    "answer": "Et, balık, yumurta, baklagiller...",
    "source": "beslenme.pdf",
    "page": 15,
    "metadata": {
      "confidence": 0.95,
      "timestamp": "2025-06-28T10:30:00Z"
    }
  }
]
```

## ⚠️ Güvenlik Özellikleri

### API Anahtarı Koruması
- ✅ `config.json` Git'ten hariç tutuldu
- ✅ `config_example.json` sadece placeholder içerir
- ✅ Gerçek anahtarlar sadece local'de saklanır
- ✅ `.gitignore` kuralları eksiksiz

### Veri Güvenliği
- Otomatik checkpoint sistemi
- Resume functionality
- Hata toleransı
- Rate limiting koruması

### Proje Güvenliği
```
# Bu dosyalar Git'e gönderilmez:
config.json           # Gerçek API anahtarları
logs/                 # Log dosyaları  
output_json/          # Çıktı dosyaları
checkpoints/          # Checkpoint dosyaları
```

## 🔧 Sorun Giderme

### Yaygın Hatalar:
1. **Config Not Found**: `copy config_example.json config.json` komutunu çalıştırın
2. **API Key Error**: `config.json`'da gerçek API anahtarlarınızı kontrol edin
3. **Permission Error**: Klasör yazma izinlerini kontrol edin
4. **Module Not Found**: `pip install -r requirements.txt` çalıştırın

### Güvenlik Kontrolleri:
```powershell
# Config dosyasının Git'te olmadığını kontrol edin:
git status

# config.json dosyası "Untracked files" altında görünmelidir
```

### Debug Modları:
```powershell
# Detaylı logging ile
python main.py --log-level DEBUG

# API test modu
python api_test.py
```

## 📈 Performans İpuçları

1. **Çoklu API Anahtarı**: Birden fazla anahtar kullanarak hızlandırın
2. **Adaptif Delay**: Sistem otomatik olarak uygun gecikme ayarlar
3. **Resume Feature**: Kesintilerde kaldığı yerden devam eder
4. **Hot-Swap Keys**: Çalışma sırasında yeni anahtarlar ekleyin

## 📝 Dosya Güvenliği

### Git İçin Güvenli Dosyalar:
- `README.md`
- `requirements.txt` 
- `config_example.json`
- `*.py` dosyaları

### Git'e Gönderilmeyen Dosyalar:
- `config.json` (gerçek API anahtarları)
- `logs/` (log dosyaları)
- `output_json/` (çıktı dosyaları)
- `checkpoints/` (checkpoint dosyaları)

---

**⚠️ GÜVENLİK HATIRLATMASI**: 
- API anahtarlarınızı asla Git'e commit etmeyin
- Her zaman `config_example.json`'dan `config.json` oluşturun
- Gerçek anahtarlarınızı sadece `config.json`'a yazın
- `git status` ile config.json'ın tracked olmadığını kontrol edin
