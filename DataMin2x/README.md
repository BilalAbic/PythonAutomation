# 🛡️ Ultra Safe Sağlık Chatbot Veri Çoğaltma Sistemi

## 🔐 GÜVENLİK VE KURULUM ÖNCESİ ÖNEMLİ NOTLAR

### ⚠️ API Anahtarı Güvenliği
**MUTLAKA OKUMANIZ GEREKEN GÜVENLİK BİLGİLERİ:**

1. **API anahtarlarınızı asla Git'e commit etmeyin**
2. **`config_example.json`'dan `config.json` oluşturun**
3. **Gerçek API anahtarlarınızı sadece `config.json`'a yazın**

### 🛠️ Güvenli Kurulum Adımları

#### 1. Config Dosyası Oluşturun
```powershell
# Bu klasörde (DataMin2x):
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
- Yeni API anahtarları oluşturun (önerilen: 5+ anahtar)
- **Bu anahtarları güvenli şekilde saklayın**

## 📋 Özellikler

- ✅ **33+ API Key** desteği ile paralel işlem
- 🛡️ **Ultra Safe** güvenlik kontrolleri
- 🏥 **Medikal doğrulama** sistemi
- 🇹🇷 **Türkçe** dil bilgisi kontrolleri
- 🔍 **Citation koruma** sistemi
- 📊 **Duplicate detection** algoritması
- 💾 **Checkpoint** ve **auto backup** sistemi
- 📈 **Real-time monitoring** ve raporlama
- 🚨 **Emergency stop** mekanizması
- 💰 **Maliyet takibi** ve optimizasyon
- 🔐 **Güvenli Config Yönetimi**: API anahtarları Git'ten korunur

## 🔄 **YENİ ÖZELLİK: CANLI API KEY YÖNETİMİ**

### **Çalışma Esnasında API Key Ekleme**

Sistem çalışırken durdurmadan yeni API key ekleyebilirsiniz!

```powershell
# Başka bir terminal açın
python add_api_key.py
```

**Özellikler:**
- 🔄 **Hot Reload**: Sistem durmuyor
- 🧪 **Auto Test**: Yeni keyler otomatik test edilir
- 📁 **Auto Backup**: Config değişikliklerinde backup
- ⚡ **Instant Update**: 5 batch içinde algılanır
- 📊 **Live Monitoring**: Aktif key sayısı takibi

### **API Key Yönetim Menüsü**

```
🔑 API KEY YÖNETİM SCRIPTI
========================================
1. 🆕 Yeni API key ekle
2. 📋 Mevcut keyleri listele  
3. 🗑️ API key sil
4. 🧪 Config'deki tüm keyleri test et
5. ❌ Çıkış
```

### **Kullanım Senaryoları**

**Senaryo 1: İşlem sırasında keyler quota aştı**
```powershell
# Terminal 1: Ana işlem çalışıyor
python data_augmenter.py

# Terminal 2: Yeni key ekle
python add_api_key.py
# -> 1. Yeni API key ekle seçin
# -> Yeni key'i girin
# -> Otomatik test edilir ve eklenir
```

**Senaryo 2: Performans artırmak için key ekleme**
```powershell
# Hızlandırmak için daha fazla key ekleyin
python add_api_key.py
# Sistem 5 batch içinde yeni keyleri algılayacak
```

---

## 📊 **Sistem Özellikleri**

### **🔐 Ultra Safe Güvenlik**
- Medical content validation  
- Turkish grammar validation
- Citation preservation
- Duplicate detection (85% threshold)
- Content filtering & profanity detection
- Emergency stop mechanism
- Secure API key management

### **⚡ High Performance**
- **33+ API key** paralel kullanım
- **3 saniye** rate limiting
- **10 Q&A** per batch
- **0.9 saat** tahmini süre
- **Auto failover** quota aşımında

### **🛡️ Monitoring & Safety**
- Real-time cost tracking
- Memory usage monitoring  
- Performance analytics
- Checkpoint/resume capability
- Auto-backup every 50 batches
- Emergency shutdown triggers

---

## 🚀 Hızlı Güvenli Başlangıç

### 1. Gereksinimleri Yükleyin
```powershell
pip install -r requirements.txt
```

### 2. Güvenli Config Kurulumu
```powershell
# Config dosyası oluşturun
copy config_example.json config.json

# config.json'ı düzenleyip gerçek API anahtarlarınızı ekleyin
```

### 3. API Keylerini Ekleyin
`config.json` dosyasını açın ve API keylerini ekleyin:
```json
{
  "api_keys": [
    "AIzaSyYour_Real_API_Key_1",
    "AIzaSyYour_Real_API_Key_2",
    "AIzaSyYour_Real_API_Key_3",
    // ... 33 adede kadar
  ],
  "safety_settings": {
    // diğer ayarlar...
  }
}
```

### 4. Güvenli Çalıştırma
```powershell
# Config hazır olduğundan emin olun
python data_augmenter.py
```

## 📂 Dosya Yapısı

```
DataMin2x/
├── 250630AllData.json         # Orijinal veri (11,467 çift)
├── config_example.json        # Güvenli config şablonu ✅
├── config.json                # Gerçek config (Git'te değil) ✅
├── data_augmenter.py          # Ana script
├── add_api_key.py            # Canlı API key yönetimi
├── validators.py              # Veri doğrulama
├── safety_monitor.py          # Güvenlik izleme
├── utils.py                   # Yardımcı fonksiyonlar
├── requirements.txt           # Python gereksinimleri
├── README.md                  # Bu dosya
├── output/                    # Çıktı dosyaları
│   ├── augmented_data_YYYYMMDD_HHMM.json
│   ├── final_dataset_YYYYMMDD_HHMM.json
│   └── final_report.json
├── checkpoints/               # Checkpoint dosyaları
├── backups/                   # Otomatik yedekler
└── logs/                      # Log dosyaları
```

## ⚙️ Güvenli Konfigürasyon

### Konfigürasyon Dosyaları

#### `config_example.json` - Güvenli Şablon
```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",
    "YOUR_GEMINI_API_KEY_3"
  ],
  "safety_settings": {
    "batch_size": 6,
    "delay_between_requests": 7,
    "max_retries": 5,
    "duplicate_threshold": 0.85,
    "auto_backup_frequency": 50,
    "max_fails_per_hour": 8,
    "emergency_shutdown_threshold": 25
  },
  "quality_controls": {
    "medical_accuracy_check": true,
    "turkish_grammar_validation": true,
    "citation_preservation": true,
    "content_length_validation": true,
    "profanity_filter": true,
    "duplicate_detection": true
  }
}
```

#### `config.json` - Gerçek Konfigürasyon
**Önemli:** Bu dosya `.gitignore` ile Git'ten hariç tutulmuştur.

### Güvenlik Ayarları
```json
"safety_settings": {
  "batch_size": 6,                    // Batch başına soru sayısı
  "delay_between_requests": 7,        // İstekler arası bekleme (saniye)
  "max_retries": 5,                   // Maksimum deneme sayısı
  "duplicate_threshold": 0.85,        // Duplicate algılama eşiği
  "auto_backup_frequency": 50,        // Kaç batch'te bir backup
  "max_fails_per_hour": 8,           // Saatlik maksimum hata
  "emergency_shutdown_threshold": 25  // Emergency stop eşiği
}
```

### Kalite Kontrolleri
```json
"quality_controls": {
  "medical_accuracy_check": true,     // Medikal doğrulama
  "turkish_grammar_validation": true, // Türkçe kontrolü
  "citation_preservation": true,      // Citation koruma
  "content_length_validation": true,  // Uzunluk kontrolü
  "profanity_filter": true,          // İçerik filtresi
  "duplicate_detection": true        // Duplicate algılama
}
```

## 📊 Beklenen Sonuçlar

- **Girdi:** 11,467 soru-cevap çifti
- **Çıktı:** ~25,000-30,000 çift (2.5x artış)
- **Süre:** 2-3 saat (33+ API key ile)
- **Kalite:** %95+ başarı oranı

## 🔧 İzleme ve Kontrole

### Real-time İzleme
- Terminal'de canlı progress bar
- `logs/` klasöründe detaylı loglar
- `output/final_report.json`'da tam rapor

### Emergency Stop
Acil durumda şu dosyayı oluşturun:
```powershell
touch EMERGENCY_STOP
```

### Checkpoint'ten Devam
Sistem otomatik olarak kaldığı yerden devam eder.

## ⚠️ Güvenlik Özellikleri

### API Anahtarı Koruması
- ✅ `config.json` Git'ten hariç tutuldu
- ✅ `config_example.json` sadece placeholder içerir
- ✅ Gerçek anahtarlar sadece local'de saklanır
- ✅ Canlı API key ekleme sistemi
- ✅ `.gitignore` kuralları eksiksiz

### Medikal Doğrulama
- Tehlikeli ifadeler engellenir
- Medikal terminoloji korunur
- Professional ton zorunluluğu

### API Güvenliği
- Rate limiting
- Automatic failover
- Key rotation
- Usage monitoring

### Proje Güvenliği
```
# Bu dosyalar Git'e gönderilmez:
config.json           # Gerçek API anahtarları
logs/                 # Log dosyaları
output/               # Çıktı dosyaları
backups/              # Yedek dosyaları
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

### API Key Test:
```powershell
# API anahtarlarınızı test edin
python add_api_key.py
# Menüden "4. Config'deki tüm keyleri test et" seçin
```

## 📈 Performans İpuçları

1. **Çoklu API Anahtarı**: 5+ anahtar kullanarak hızlandırın
2. **Batch Settings**: Sistem ayarlarını optimize edin
3. **Monitoring**: Real-time izleme ile performansı takip edin
4. **Hot-Swap**: Çalışma sırasında yeni anahtarlar ekleyin

## 📝 Dosya Güvenliği

### Git İçin Güvenli Dosyalar:
- `README.md`
- `requirements.txt`
- `config_example.json`
- `*.py` dosyaları
- `250630AllData.json` (orijinal veri)

### Git'e Gönderilmeyen Dosyalar:
- `config.json` (gerçek API anahtarları)
- `logs/` (log dosyaları)
- `output/` (çıktı dosyaları)
- `backups/` (yedek dosyaları)
- `checkpoints/` (checkpoint dosyaları)

## 🎯 Güncelleme Notları

### v2.0 Güvenlik Güncellemesi:
- ✅ Config dosyası güvenliği eklendi
- ✅ `.gitignore` kuralları eklendi
- ✅ `config_example.json` şablonu oluşturuldu
- ✅ Canlı API key yönetimi güncellendi

---

**⚠️ GÜVENLİK HATIRLATMASI**: 
- API anahtarlarınızı asla Git'e commit etmeyin
- Her zaman `config_example.json`'dan `config.json` oluşturun
- Gerçek anahtarlarınızı sadece `config.json`'a yazın
- `git status` ile config.json'ın tracked olmadığını kontrol edin 