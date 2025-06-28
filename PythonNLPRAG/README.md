# PythonNLPRAG - Gelişmiş PDF İşleme ve Soru-Cevap Üretimi Sistemi

Bu modül, profesyonel düzeyde PDF'den soru-cevap dataset üretimi için gelişmiş özellikler sunan production-ready bir sistemdir. Çoklu makine desteği, adaptif rate limiting ve güçlü API anahtar yönetimi ile donatılmıştır.

## 🚀 Modül Özellikleri

- **Production-Ready Mimari**: Endüstriyel seviye kod kalitesi
- **Çoklu Makine Desteği**: Dağıtık işleme için multi-machine support
- **Adaptif Rate Limiting**: Akıllı API çağrı yönetimi
- **Güçlü API Yönetimi**: Otomatik anahtar rotasyonu ve failover
- **Resume Functionality**: Kesintiye uğrayan işlemleri kaldığı yerden devam ettirme
- **Detaylı Logging**: Kapsamlı hata takibi ve performans izleme
- **Yapılandırılabilir Çıktı**: Esnek dataset formatları

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

### 2. Konfigürasyon Dosyasını Ayarlayın
`config.json` dosyasını düzenleyin:

```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",
    "YOUR_GEMINI_API_KEY_3"
  ],
  "pdf_directory": "pdfs",
  "output_directory": "output_json",
  "questions_per_page": 3,
  "min_delay_between_calls": 1,
  "max_delay_between_calls": 5,
  "machine_id": 0,
  "total_machines": 1
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

**Nasıl çalıştırılır:**
```powershell
# Temel kullanım
python main.py

# Komut satırı parametreleri ile
python main.py --config config.json --output-dir output_json --questions-per-page 5
```

**Çalıştırmadan önce yapılması gerekenler:**
1. `config.json` dosyasını yapılandırın
2. PDF dosyalarını `pdfs/` klasörüne yerleştirin
3. API anahtarlarınızı ekleyin
4. Çıktı klasörü permissionlarını kontrol edin

#### 2. `main_enhanced.py` - Gelişmiş Özelliklerle
**Ne yapar:**
- Gelişmiş görsel işleme
- Multi-modal AI entegrasyonu
- Zengin metadata çıktısı
- Performans optimizasyonları

**Nasıl çalıştırılır:**
```powershell
python main_enhanced.py --verbose --debug
```

#### 3. `main_backup.py` - Yedek Sistem
**Ne yapar:**
- Ana sistemin yedek versiyonu
- Basitleştirilmiş işleme mantığı
- Emergency fallback

### Konfigürasyon Yönetimi

#### 4. `config.json` - Sistem Konfigürasyonu
**İçeriği:**
```json
{
  "api_keys": ["key1", "key2", "key3"],
  "pdf_directory": "pdfs",
  "output_directory": "output_json", 
  "questions_per_page": 3,
  "min_delay_between_calls": 1,
  "max_delay_between_calls": 5,
  "machine_id": 0,
  "total_machines": 1,
  "enable_image_processing": true,
  "enable_resume": true,
  "log_level": "INFO",
  "max_retries": 3,
  "timeout_seconds": 30
}
```

## 🚀 Kullanım Senaryoları

### Scenario 1: Tek Makine Basit İşleme
```powershell
# 1. Konfigürasyonu hazırlayın
cp config.json.example config.json
# API anahtarlarınızı ekleyin

# 2. PDF'leri yerleştirin
mkdir pdfs
# PDF dosyalarınızı pdfs/ klasörüne kopyalayın

# 3. İşlemi başlatın
python main.py
```

### Scenario 2: Çoklu Makine Dağıtık İşleme
**Makine 1:**
```json
{
  "machine_id": 0,
  "total_machines": 3,
  "api_keys": ["key1", "key2"]
}
```

**Makine 2:**
```json
{
  "machine_id": 1,
  "total_machines": 3,
  "api_keys": ["key3", "key4"]
}
```

**Makine 3:**
```json
{
  "machine_id": 2,
  "total_machines": 3,
  "api_keys": ["key5", "key6"]
}
```

```powershell
# Her makinede aynı anda çalıştırın
python main.py --config config_machine1.json
```

### Scenario 3: Kesintiye Uğrayan İşlemi Devam Ettirme
```powershell
# İşlem otomatik olarak kaldığı yerden devam eder
python main.py --resume
```

### Scenario 4: Debug ve Monitoring
```powershell
# Detaylı logging ile
python main.py --log-level DEBUG --verbose

# Performans izleme ile
python main.py --enable-monitoring
```

## 📊 Çıktı Formatları

### JSONL Format (ML için optimize)
```jsonl
{"question": "Hangi besinler protein açısından zengindir?", "answer": "Et, balık, yumurta, baklagiller...", "source": "beslenme.pdf", "page": 15, "metadata": {"confidence": 0.95, "timestamp": "2025-06-28T10:30:00Z"}}
{"question": "Günlük su ihtiyacı nedir?", "answer": "Yetişkin bir kişi günde 2-3 litre su...", "source": "beslenme.pdf", "page": 16, "metadata": {"confidence": 0.92, "timestamp": "2025-06-28T10:30:05Z"}}
```

### JSON Format
```json
[
  {
    "question": "Hangi besinler protein açısından zengindir?",
    "answer": "Et, balık, yumurta, baklagiller protein açısından zengin besinlerdir...",
    "source": "beslenme.pdf",
    "page": 15,
    "metadata": {
      "confidence": 0.95,
      "processing_time": 2.3,
      "api_key_used": "key1",
      "timestamp": "2025-06-28T10:30:00Z"
    }
  }
]
```

## ⚙️ Gelişmiş Özellikler

### 1. Adaptif Rate Limiting
```python
# Sistem otomatik olarak API limitlerini yönetir
# Rate limit algılandığında gecikme süresi artırılır
# Başarılı çağrılarda gecikme azaltılır
```

### 2. API Anahtar Rotasyonu
```python
# Çoklu API anahtarı otomatik rotasyonu
# Hatalı anahtarlar otomatik blacklist
# Failover mekanizması
```

### 3. Resume Functionality
```python
# İşlenen dosyalar otomatik kaydedilir
# Kesinti sonrası otomatik devam
# Duplicate prevention
```

### 4. Multi-Machine Coordination
```python
# Machine ID bazlı dosya dağıtımı
# Collision prevention
# Distributed load balancing
```

## 📈 Performans Optimizasyonu

### Memory Management:
```python
# Büyük PDF'ler için sayfa bazlı işleme
# Garbage collection optimizasyonu
# Memory leak prevention
```

### API Optimizasyonu:
```python
# Intelligent request batching
# Connection pooling
# Retry strategies with exponential backoff
```

### Logging ve Monitoring:
```python
# Structured logging (JSON format)
# Performance metrics
# Error tracking
# API usage statistics
```

## 🔧 Sorun Giderme

### Yaygın Hatalar ve Çözümleri:

#### 1. API Key Hatası
```powershell
# API anahtarlarını test edin
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Test')
print('API Key çalışıyor!')
"
```

#### 2. Memory Error
```json
{
  "questions_per_page": 2,
  "process_in_chunks": true,
  "chunk_size": 10
}
```

#### 3. Rate Limit Aşımı
```json
{
  "min_delay_between_calls": 3,
  "max_delay_between_calls": 10,
  "max_retries": 5
}
```

#### 4. PDF İşleme Hatası
```powershell
# PDF'in durumunu kontrol edin
python -c "
import fitz
doc = fitz.open('pdfs/problematic.pdf')
print(f'Sayfa sayısı: {len(doc)}')
print(f'İlk sayfa metni: {doc[0].get_text()[:100]}')
"
```

### Debug Komutları:
```powershell
# Detaylı hata mesajları
python main.py --debug --log-level DEBUG

# API çağrı istatistikleri
python main.py --show-api-stats

# Memory usage monitoring
python main.py --monitor-memory
```

## 📊 Log Analizi

### Log Dosyası Konumu:
```
data_generator.log
```

### Log Format Örneği:
```
2025-06-28 10:30:00,123 - INFO - PDFToQAGenerator - Starting PDF processing
2025-06-28 10:30:01,456 - INFO - PDFToQAGenerator - Processing: beslenme.pdf (25 pages)
2025-06-28 10:30:02,789 - DEBUG - PDFToQAGenerator - API call successful, response time: 1.2s
2025-06-28 10:30:05,012 - WARNING - PDFToQAGenerator - Rate limit approached, increasing delay
2025-06-28 10:30:10,345 - ERROR - PDFToQAGenerator - API error: 429 Too Many Requests
2025-06-28 10:30:15,678 - INFO - PDFToQAGenerator - Retrying with delay: 5s
```

## 🎯 Best Practices

1. **API Anahtar Yönetimi**: En az 3 farklı anahtar kullanın
2. **Dosya Organizasyonu**: PDF'leri kategori bazlı klasörlerde organize edin
3. **Backup Strategy**: Çıktı dosyalarını düzenli yedekleyin
4. **Monitoring**: Log dosyalarını düzenli kontrol edin
5. **Resource Management**: Sistem kaynaklarını izleyin

Bu gelişmiş sistem ile büyük ölçekli PDF işleme ve dataset üretimi projelerinizi professional seviyede gerçekleştirebilirsiniz.
