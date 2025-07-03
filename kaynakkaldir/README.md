# kaynakkaldir - JSON Temizleme ve AI Veri Çoğaltma Araçları

Bu modül, JSON dosyalarından kaynak bilgilerini temizleme ve AI teknolojileri kullanarak veri çoğaltma işlemleri gerçekleştiren Python araçlarını içerir.

## 🔐 GÜVENLİK VE KURULUM ÖNCESİ ÖNEMLİ NOTLAR

### ⚠️ API Anahtarı Güvenliği
**MUTLAKA OKUMANIZ GEREKEN GÜVENLİK BİLGİLERİ:**

1. **API anahtarlarınızı asla Git'e commit etmeyin**
2. **`config_example.json`'dan `config.json` oluşturun**
3. **Gerçek API anahtarlarınızı sadece `config.json`'a yazın**

### 🛠️ Güvenli Kurulum Adımları

#### 1. Config Dosyası Oluşturun
```powershell
# Bu klasörde (kaynakkaldir):
copy config_example.json config.json
```

#### 2. API Anahtarları Ekleyin
`config.json` dosyasını açın ve placeholder'ları değiştirin:
```json
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": ["AIzaSyYour_Real_API_Key_Here_1", "AIzaSyYour_Real_API_Key_Here_2"],
        "enabled": true
      }
    ]
  }
}
```

#### 3. API Anahtarını Alın
- [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin
- Yeni API anahtarları oluşturun
- **Bu anahtarları güvenli şekilde saklayın**

## 🎯 Modül Özellikleri

- **JSON Kaynak Temizleme**: Veri setlerinden kaynak/referans bilgilerini kaldırma
- **AI Veri Çoğaltma**: Google Gemini API ile veri çeşitlendirme
- **Çoklu API Desteği**: Gemini ve OpenAI API entegrasyonu
- **Eşzamanlı İşleme**: Hızlı toplu veri işleme
- **Konfigürasyon Yönetimi**: Esnek API ve işlem ayarları
- **Güvenli Config Yönetimi**: API anahtarları Git'ten korunur

## 📋 Gereksinimler

- **Python 3.7+**
- **Google Gemini API Anahtarı** (veri çoğaltma için)
- **İnternet Bağlantısı** (AI işlemler için)

### Python Paketleri:
```
google-generativeai>=0.3.0
openai>=0.28.0
```

## ⚙️ Kurulum

### 1. Gerekli Paketleri Yükleyin
```powershell
pip install -r requirements.txt
```

### 2. Güvenli API Anahtarı Yapılandırması
```powershell
# Config dosyası oluşturun
copy config_example.json config.json

# config.json'ı düzenleyip gerçek API anahtarlarınızı ekleyin
```

### 3. Konfigürasyon Ayarları
`config.json` dosyasında API anahtarlarınızı güncelleyin:
```json
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": ["YOUR_GEMINI_API_KEY_1", "YOUR_GEMINI_API_KEY_2"],
        "model": "gemini-1.5-flash-latest",
        "enabled": true,
        "rate_limit_delay": 1.0,
        "max_requests_per_minute": 60,
        "key_rotation_strategy": "round_robin"
      }
    ]
  },
  "augmentation_settings": {
    "variations_per_question": 10,
    "min_variations": 5,
    "max_variations": 20
  }
}
```

## 📁 Dosya Yapısı ve İşlevleri

### Kaynak Temizleme Araçları

#### 1. `kaynak_kaldir.py` - Basit JSON Temizleyici
**Ne yapar:**
- JSON dosyalarından kaynak/source alanlarını kaldırır
- Tek dosya veya klasör bazında işlem yapar
- Yedek dosya oluşturur

**Güvenli çalıştırma:**
```powershell
# İnternet bağlantısı gerektirmez
python kaynak_kaldir.py
```

**Gereksinimleri:**
- Sadece standart Python kütüphaneleri
- İnternet bağlantısı gerektirmez

#### 2. `gelismis_kaynak_kaldir.py` - Gelişmiş Temizleyici
**Ne yapar:**
- Daha karmaşık JSON yapılarını işler
- Çoklu kaynak alan türlerini destekler
- Hata yönetimi ve logging

**Güvenli çalıştırma:**
```powershell
python gelismis_kaynak_kaldir.py
```

### Veri Çoğaltma Araçları

#### 3. `vericogaltma.py` - AI Veri Çoğaltıcı (Güncellendi)
**Ne yapar:**
- Mevcut soru-cevap çiftlerinden yeni varyasyonlar oluşturur
- Config dosyasından API anahtarlarını okur ✅
- Eşzamanlı işleme desteği

**Güvenli çalıştırma:**
```powershell
# Önce config.json oluşturun ve API anahtarlarınızı ekleyin
copy config_example.json config.json
# API anahtarlarınızı config.json'a ekleyin

python vericogaltma.py
```

**Önemli:** Artık API anahtarları kodda hardcode değil, config dosyasından okunuyor.

#### 4. `gelismis_vericogaltma.py` - Gelişmiş Veri Çoğaltıcı
**Ne yapar:**
- Çoklu API provider desteği (Gemini + OpenAI)
- Gelişmiş hata yönetimi ve yeniden deneme
- API anahtar rotasyonu
- Rate limiting ve adaptif gecikme
- Config dosyası tabanlı yönetim

**Güvenli çalıştırma:**
```powershell
# Config dosyası hazır olduğundan emin olun
python gelismis_vericogaltma.py
```

### Konfigürasyon Dosyaları

#### 5. `config_example.json` - Güvenli Config Şablonu
**İçeriği:**
```json
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": [
          "YOUR_GEMINI_API_KEY_1",
          "YOUR_GEMINI_API_KEY_2",
          "YOUR_GEMINI_API_KEY_3"
        ],
        "model": "gemini-1.5-flash-latest",
        "enabled": true,
        "rate_limit_delay": 1.0,
        "max_requests_per_minute": 60,
        "key_rotation_strategy": "round_robin"
      }
    ]
  }
}
```

**Önemli:** Bu dosya Git'e commit edilir ama gerçek API anahtarları içermez.

#### 6. `config.json` - Gerçek Konfigürasyon
**Önemli:** Bu dosya `.gitignore` ile Git'ten hariç tutulmuştur.

## 🚀 Kullanım Senaryoları

### Scenario 1: JSON Dosyalarını Temizleme
```powershell
# Basit temizleme işlemi (güvenli)
python kaynak_kaldir.py

# Gelişmiş temizleme işlemi (güvenli)
python gelismis_kaynak_kaldir.py
```

### Scenario 2: İlk Kez Güvenli Veri Çoğaltma
```powershell
# 1. Config dosyası oluşturun
copy config_example.json config.json

# 2. config.json'ı açın ve API anahtarlarınızı ekleyin
# YOUR_GEMINI_API_KEY_X kısımlarını gerçek anahtarlarla değiştirin

# 3. Çalıştırın
python vericogaltma.py
```

### Scenario 3: Gelişmiş Veri Çoğaltma
```powershell
# 1. Config dosyasını hazırlayın
copy config_example.json config.json

# 2. config.json'ı düzenleyin:
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": ["YOUR_REAL_API_KEY_1", "YOUR_REAL_API_KEY_2"],
        "enabled": true
      }
    ]
  },
  "augmentation_settings": {
    "variations_per_question": 5,
    "variation_types": {
      "kisisel_senaryo": 1,
      "samimi_gunluk": 1,
      "basit_direkt": 1,
      "yazim_hatali": 1,
      "farkli_soru_koku": 1
    }
  }
}

# 3. Çalıştırın
python gelismis_vericogaltma.py
```

## 📊 Örnek Veri Dosyaları

Klasörde bulunan örnek dosyalar:
- `train.json` - Ana eğitim verisi
- `test.json` - Test verisi
- `quiz.json` - Quiz verileri
- `egitim.json` - Eğitim verileri

## ⚠️ Güvenlik Özellikleri

### API Anahtarı Koruması
- ✅ `config.json` Git'ten hariç tutuldu
- ✅ `config_example.json` sadece placeholder içerir
- ✅ Gerçek anahtarlar sadece local'de saklanır
- ✅ `vericogaltma.py` artık config dosyası kullanıyor
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
*.log                 # Log dosyaları
```

## 🔧 Sorun Giderme

### Yaygın Hatalar:
1. **Config Not Found**: `copy config_example.json config.json` komutunu çalıştırın
2. **API Key Error**: `config.json`'da gerçek API anahtarlarınızı kontrol edin
3. **ModuleNotFoundError**: `pip install -r requirements.txt`
4. **Rate Limit Error**: İstek sayısını azaltın
5. **File Not Found**: Dosya yollarını kontrol edin

### Güvenlik Kontrolleri:
```powershell
# Config dosyasının Git'te olmadığını kontrol edin:
git status

# config.json dosyası "Untracked files" altında görünmelidir
```

### Debug Modları:
Hata ayıklama için dosyalarda bulunan debug flaglerini aktifleştirin.

## 📈 Performans İpuçları

### API Limitleri:
- Gemini API: Dakikada 60 istek limiti
- Çok fazla eşzamanlı istek yapmayın
- API anahtarlarını rotasyonla kullanın

### Veri Güvenliği:
- İşlem öncesi verilerinizi yedekleyin
- API anahtarlarını güvenli tutun
- Çıktı dosyalarını kontrol edin

### Performans İpuçları:
- Büyük dosyalar için `PROCESS_LIMIT` kullanın
- `MAX_CONCURRENT_REQUESTS` değerini API limitine göre ayarlayın
- Kararlı internet bağlantısı kullanın
- Çoklu API anahtarı kullanarak hızlandırın

## 📝 Dosya Güvenliği

### Git İçin Güvenli Dosyalar:
- `README.md`
- `requirements.txt`
- `config_example.json`
- `*.py` dosyaları
- Örnek veri dosyaları (`*.json`)

### Git'e Gönderilmeyen Dosyalar:
- `config.json` (gerçek API anahtarları)
- `logs/` (log dosyaları)
- `*.log` (log dosyaları)

## 🎯 Güncelleme Notları

### v2.0 Güvenlik Güncellemesi:
- ✅ `vericogaltma.py` artık config dosyası kullanıyor
- ✅ Hardcode API anahtarları kaldırıldı
- ✅ `.gitignore` kuralları eklendi
- ✅ `config_example.json` şablonu oluşturuldu

### Eski Versiyondan Geçiş:
```powershell
# 1. Config dosyası oluşturun
copy config_example.json config.json

# 2. Eski API anahtarlarınızı config.json'a taşıyın
# 3. Artık kod dosyalarını düzenlemeniz gerekmez
```

---

**⚠️ GÜVENLİK HATIRLATMASI**: 
- API anahtarlarınızı asla Git'e commit etmeyin
- Her zaman `config_example.json`'dan `config.json` oluşturun
- Gerçek anahtarlarınızı sadece `config.json`'a yazın
- `git status` ile config.json'ın tracked olmadığını kontrol edin
