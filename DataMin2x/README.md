# 🛡️ Ultra Safe Sağlık Chatbot Veri Çoğaltma Sistemi

## 📋 Özellikler

- ✅ **12 API Key** desteği ile paralel işlem
- 🛡️ **Ultra Safe** güvenlik kontrolleri
- 🏥 **Medikal doğrulama** sistemi
- 🇹🇷 **Türkçe** dil bilgisi kontrolleri
- 🔍 **Citation koruma** sistemi
- 📊 **Duplicate detection** algoritması
- 💾 **Checkpoint** ve **auto backup** sistemi
- 📈 **Real-time monitoring** ve raporlama
- 🚨 **Emergency stop** mekanizması
- 💰 **Maliyet takibi** ve optimizasyon

## 🔄 **YENİ ÖZELLİK: CANLI API KEY YÖNETİMİ**

### **Çalışma Esnasında API Key Ekleme**

Sistem çalışırken durdurmadan yeni API key ekleyebilirsiniz!

```bash
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
```bash
# Terminal 1: Ana işlem çalışıyor
python data_augmenter.py

# Terminal 2: Yeni key ekle
python add_api_key.py
# -> 1. Yeni API key ekle seçin
# -> Yeni key'i girin
# -> Otomatik test edilir ve eklenir
```

**Senaryo 2: Performans artırmak için key ekleme**
```bash
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

### **⚡ High Performance**
- **14+ API key** paralel kullanım
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

## 🚀 Hızlı Başlangıç

### 1. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 2. API Keylerini Ekleyin
`config.json` dosyasını açın ve API keylerini ekleyin:
```json
{
  "api_keys": [
    "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "AIzaSyYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
    // ... 12 adede kadar
  ]
}
```

### 3. Çalıştırın
```bash
python data_augmenter.py
```

## 📂 Dosya Yapısı

```
DataMin2x/
├── 250630AllData.json         # Orijinal veri (11,467 çift)
├── config.json                # API keys + ayarlar
├── data_augmenter.py          # Ana script
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

## ⚙️ Konfigürasyon

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
- **Süre:** 2-3 saat (12 API key ile)
- **Kalite:** %95+ başarı oranı

## 🔧 İzleme ve Kontrole

### Real-time İzleme
- Terminal'de canlı progress bar
- `logs/` klasöründe detaylı loglar
- `output/final_report.json`'da tam rapor

### Emergency Stop
Acil durumda şu dosyayı oluşturun:
```bash
touch EMERGENCY_STOP
```

### Checkpoint'ten Devam
Sistem otomatik olarak kaldığı yerden devam eder.

## 🚨 Güvenlik Özellikleri

### Medikal Doğrulama
- Tehlikeli ifadeler engellenir
- Medikal terminoloji korunur
- Professional ton zorunluluğu

### API Güvenliği
- Rate limiting
- Automatic failover
- Cost monitoring
- Token limit kontrolü

### Veri Güvenliği
- Otomatik backup
- Checkpoint sistemi
- Duplicate protection
- Memory management

## 🔍 Sorun Giderme

### API Key Sorunları
```bash
# Log dosyasını kontrol edin
tail -f logs/ultra_safe_*.log

# API key test edin
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

### Memory Sorunları
```bash
# Memory kullanımını kontrol edin
python -c "import psutil; print(f'Memory: %{psutil.virtual_memory().percent}')"
```

### Token Limit Sorunları
- `batch_size`'ı azaltın (config.json)
- `max_tokens_per_request`'i düşürün

## 📞 Destek

Sorun yaşarsanız:
1. `logs/` klasöründeki en son log dosyasını kontrol edin
2. `output/final_report.json`'da hata raporlarını inceleyin
3. Emergency shutdown'dan sonra `emergency_shutdown.json`'u kontrol edin

## 🎯 Performans Optimizasyonu

### Hızlandırma İçin:
- `batch_size`'ı artırın (6 → 8)
- `delay_between_requests`'i azaltın (7 → 5)
- Daha fazla API key ekleyin

### Güvenlik İçin:
- `batch_size`'ı azaltın (6 → 4)
- `delay_between_requests`'i artırın (7 → 10)
- `validation_strictness`'i "ultra_high" yapın

---

## 📈 Örnek Çıktı

```
🛡️ Ultra Safe Data Augmenter başlatılıyor...
🔑 API Key 1 test ediliyor...
✅ API Key 1 aktif
🔑 API Key 2 test ediliyor...
✅ API Key 2 aktif
...
🎯 12/12 API key aktif
🚀 Ultra Safe Data Augmentation başlatıldı
📊 Toplam 11,467 çift yüklendi
📦 1,911 batch oluşturuldu
📈 İlerleme: %15.2 - Batch 291
✅ Batch 291 başarılı (12 varyant)
...
🎉 === ULTRA SAFE AUGMENTATION TAMAMLANDI! ===
📊 Orijinal: 11,467 çift
🆕 Yeni üretilen: 18,423 çift  
📈 Toplam: 29,890 çift
🔢 Çarpan: 2.6x
💾 Dosyalar: output/ klasöründe
```

**Sistem hazır! 🚀 İyi çalışmalar!** 