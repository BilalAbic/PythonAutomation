# PythonNLP - PDF'den Soru-Cevap Üretimi Sistemi

Bu modül, beslenme ve sağlık konularındaki PDF dosyalarından Google Gemini AI kullanarak otomatik soru-cevap çiftleri oluşturan kapsamlı bir sistemdir.

## 🔐 GÜVENLİK VE KURULUM ÖNCESİ ÖNEMLİ NOTLAR

### ⚠️ API Anahtarı Güvenliği
**MUTLAKA OKUMANIZ GEREKEN GÜVENLİK BİLGİLERİ:**

1. **API anahtarlarınızı asla Git'e commit etmeyin**
2. **`config_example.json`'dan `config.json` oluşturun**
3. **Gerçek API anahtarlarınızı sadece `config.json`'a yazın**

### 🛠️ Güvenli Kurulum Adımları

#### 1. Config Dosyası Oluşturun
```powershell
# Bu klasörde (PythonNLP):
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

- **Otomatik PDF İşleme**: Klasördeki tüm PDF'leri otomatik olarak işler
- **AI Destekli Soru-Cevap Üretimi**: Google Gemini API ile kaliteli soru-cevap çiftleri
- **Çoklu Format Desteği**: JSON, CSV, JSONL formatlarında çıktı
- **Veri Analizi**: Oluşturulan verilerin detaylı analizi
- **Kalite Filtreleme**: Düşük kaliteli verileri otomatik filtreleme
- **Konu Bazlı Gruplama**: Kaynaklara göre veri gruplama
- **Kullanıcı Dostu Arayüz**: Menü tabanlı kontrol sistemi
- **Güvenli API Yönetimi**: Config dosyası tabanlı anahtar yönetimi

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

### Yöntem 1: Hızlı Güvenli Kurulum (Önerilen)
```powershell
# 1. Config dosyası oluşturun
copy config_example.json config.json

# 2. config.json'ı düzenleyip API anahtarlarınızı ekleyin

# 3. Ana sistemi başlatın
python main.py

# 4. Menüden "1 - Sistem kurulumu yap" seçeneğini seçin
```

### Yöntem 2: Manuel Kurulum
```powershell
# 1. Gerekli paketleri yükle
pip install -r requirements.txt

# 2. Config dosyası oluştur
copy config_example.json config.json

# 3. API anahtarlarını config.json'a ekle

# 4. Kurulum scriptini çalıştır
python setup_qa_generator.py

# 5. API anahtarını test et
python setup_api_key.py
```

### 3. Güvenli API Anahtarı Yapılandırması
1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
2. Yeni API anahtarı oluşturun
3. `config.json` dosyasında `YOUR_GEMINI_API_KEY_X` kısımlarını gerçek anahtarlarınızla değiştirin

**UYARI:** Artık API anahtarlarını doğrudan kod dosyalarına yazmayın!

## 📁 Dosya Yapısı ve İşlevleri

### Ana Kontrol Sistemi

#### 1. `main.py` - Ana Menü ve Sistem Yöneticisi
**Ne yapar:**
- Sistem durumunu kontrol eder
- Kullanıcı dostu menü sağlar
- Tüm işlemleri koordine eder
- Kurulum ve konfigürasyon yönetimi
- Güvenli config dosyası yönetimi

**Güvenli çalıştırma:**
```powershell
# Önce config.json oluşturun:
copy config_example.json config.json
# Sonra API anahtarlarınızı config.json'a ekleyin

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
- Config dosyasından API anahtarlarını okur
- Çoklu format çıktı sağlar
- Hata yönetimi ve logging

**Güvenli çalıştırma:**
```powershell
# Config dosyası hazır olduğundan emin olun
python pdf_to_qa_gemini.py
```

### Konfigürasyon Dosyaları

#### 3. `config_example.json` - Güvenli Config Şablonu
**İçeriği:**
```json
{
    "api_keys": [
        "YOUR_GEMINI_API_KEY_1",
        "YOUR_GEMINI_API_KEY_2",
        "YOUR_GEMINI_API_KEY_3"
    ],
    "retry_settings": {
        "max_retries": 3,
        "retry_delay": 5,
        "rate_limit_delay": 10
    },
    "chunk_settings": {
        "chunk_size": 3000,
        "chunk_overlap": 200
    }
}
```

**Önemli:** Bu dosya Git'e commit edilir ama gerçek API anahtarları içermez.

#### 4. `config.json` - Gerçek Konfigürasyon
**Önemli:** Bu dosya `.gitignore` ile Git'ten hariç tutulmuştur.

### Yardımcı Araçlar

#### 5. `run_qa_generation.py` - Hızlı Başlatma Scripti
**Ne yapar:**
- Tek komutla PDF işleme başlatır
- Config dosyası kontrolü yapar
- Ön kontrolleri yapar
- Hızlı kurulum sağlar

#### 6. `analyze_qa_data.py` - Veri Analizi ve Dönüştürme
**Ne yapar:**
- Oluşturulan verileri analiz eder
- İstatistik raporları üretir
- Format dönüştürmeleri yapar
- Kalite kontrolü

#### 7. `setup_qa_generator.py` - Kurulum Scripti
**Ne yapar:**
- Sistem gereksinimlerini kontrol eder
- Klasör yapısını oluşturur
- Config dosyası varlığını kontrol eder
- Test işlemleri yapar

#### 8. `setup_api_key.py` - API Anahtar Yapılandırıcı
**Ne yapar:**
- Config dosyasından API anahtarlarını okur
- Anahtar geçerliliğini test eder
- Güvenli anahtar doğrulama

## 🚀 Kullanım Senaryoları

### Scenario 1: İlk Kez Güvenli Kullanım
```powershell
# 1. Config dosyası oluşturun
copy config_example.json config.json

# 2. API anahtarlarınızı config.json'a ekleyin
# config.json dosyasını açın ve YOUR_GEMINI_API_KEY_X kısımlarını değiştirin

# 3. Ana sistemi başlatın
python main.py

# 4. Menüden "1" seçin (Sistem kurulumu)
# 5. PDF'lerinizi pdfs/ klasörüne yerleştirin
# 6. Menüden "2" seçin (PDF işleme)
```

### Scenario 2: PDF'leri Toplu İşleme
```powershell
# Config hazır olduğundan emin olun
python run_qa_generation.py
```

### Scenario 3: Veri Analizi
```powershell
# Oluşturulan verileri analiz etmek için
python analyze_qa_data.py
```

### Scenario 4: API Anahtarı Test
```powershell
# API anahtarlarınızın çalışıp çalışmadığını test edin
python setup_api_key.py
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

## ⚠️ Güvenlik Özellikleri

### API Anahtarı Koruması
- ✅ `config.json` Git'ten hariç tutuldu
- ✅ `config_example.json` sadece placeholder içerir
- ✅ Gerçek anahtarlar sadece local'de saklanır
- ✅ `.gitignore` kuralları eksiksiz

### Veri Güvenliği
- Otomatik backup sistemi
- Hata toleransı
- Rate limiting koruması
- Güvenli dosya işleme

### Proje Güvenliği
```
# Bu dosyalar Git'e gönderilmez:
config.json           # Gerçek API anahtarları
logs/                 # Log dosyaları
output/               # Çıktı dosyaları
*.log                 # Log dosyaları
```

## 🔧 Sorun Giderme

### Yaygın Hatalar:
1. **Config Not Found**: `copy config_example.json config.json` komutunu çalıştırın
2. **API Key Error**: `config.json`'da gerçek API anahtarlarınızı kontrol edin
3. **Module Not Found**: `pip install -r requirements.txt` çalıştırın
4. **File Not Found**: PDF'lerin `pdfs/` klasöründe olduğunu kontrol edin

### Güvenlik Kontrolleri:
```powershell
# Config dosyasının Git'te olmadığını kontrol edin:
git status

# config.json dosyası "Untracked files" altında görünmelidir
```

### Debug Modları:
Hata ayıklama için dosyalarda bulunan debug flaglerini aktifleştirin.

## 📈 Performans İpuçları

1. **Çoklu API Anahtarı**: `config.json`'da birden fazla anahtar kullanın
2. **Rate Limiting**: API limitlerini aşmamaya dikkat edin
3. **Chunk Settings**: Büyük PDF'ler için chunk ayarlarını optimize edin
4. **Retry Settings**: Hata durumlarında yeniden deneme ayarları

## 📝 Dosya Güvenliği

### Git İçin Güvenli Dosyalar:
- `README.md`
- `requirements.txt`
- `config_example.json`
- `*.py` dosyaları

### Git'e Gönderilmeyen Dosyalar:
- `config.json` (gerçek API anahtarları)
- `logs/` (log dosyaları)
- `*.log` (log dosyaları)
- `pdfs/` (PDF dosyaları)

---

**⚠️ GÜVENLİK HATIRLATMASI**: 
- API anahtarlarınızı asla Git'e commit etmeyin
- Her zaman `config_example.json`'dan `config.json` oluşturun
- Gerçek anahtarlarınızı sadece `config.json`'a yazın
- `git status` ile config.json'ın tracked olmadığını kontrol edin
