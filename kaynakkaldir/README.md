# kaynakkaldir - JSON Temizleme ve AI Veri Çoğaltma Araçları

Bu modül, JSON dosyalarından kaynak bilgilerini temizleme ve AI teknolojileri kullanarak veri çoğaltma işlemleri gerçekleştiren Python araçlarını içerir.

## 🎯 Modül Özellikleri

- **JSON Kaynak Temizleme**: Veri setlerinden kaynak/referans bilgilerini kaldırma
- **AI Veri Çoğaltma**: Google Gemini API ile veri çeşitlendirme
- **Çoklu API Desteği**: Gemini ve OpenAI API entegrasyonu
- **Eşzamanlı İşleme**: Hızlı toplu veri işleme
- **Konfigürasyon Yönetimi**: Esnek API ve işlem ayarları

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

### 2. API Anahtarlarını Yapılandırın
`config.json` dosyasında API anahtarlarınızı güncelleyin:
```json
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": ["YOUR_GEMINI_API_KEY_HERE"],
        "enabled": true
      }
    ]
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

**Nasıl çalıştırılır:**
```powershell
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

**Nasıl çalıştırılır:**
```powershell
python gelismis_kaynak_kaldir.py
```

### Veri Çoğaltma Araçları

#### 3. `vericogaltma.py` - Basit AI Veri Çoğaltıcı
**Ne yapar:**
- Mevcut soru-cevap çiftlerinden yeni varyasyonlar oluşturur
- Google Gemini API kullanır
- Eşzamanlı işleme desteği

**Nasıl çalıştırılır:**
```powershell
# Önce API anahtarını dosyada güncelleyin
python vericogaltma.py
```

**Çalıştırmadan önce yapılması gerekenler:**
1. Dosyada `API_KEYS` listesini güncelleyin
2. `INPUT_FILE` ve `OUTPUT_FILE` yollarını kontrol edin
3. İşlem limitlerini ayarlayın (`PROCESS_LIMIT`, `MAX_CONCURRENT_REQUESTS`)

#### 4. `gelismis_vericogaltma.py` - Gelişmiş Veri Çoğaltıcı
**Ne yapar:**
- Çoklu API provider desteği (Gemini + OpenAI)
- Gelişmiş hata yönetimi ve yeniden deneme
- API anahtar rotasyonu
- Rate limiting ve adaptif gecikme

**Nasıl çalıştırılır:**
```powershell
python gelismis_vericogaltma.py
```

**Çalıştırmadan önce yapılması gerekenler:**
1. `config.json` dosyasını yapılandırın
2. API anahtarlarını ekleyin
3. İşlem ayarlarını düzenleyin

## 🚀 Kullanım Senaryoları

### Scenario 1: JSON Dosyalarını Temizleme
```powershell
# Basit temizleme işlemi
python kaynak_kaldir.py

# Gelişmiş temizleme işlemi
python gelismis_kaynak_kaldir.py
```

### Scenario 2: Veri Çoğaltma (Temel)
1. `vericogaltma.py` dosyasını açın
2. Satır 11-16 arası API anahtarlarınızı ekleyin
3. Satır 18-19'da dosya yollarını kontrol edin
4. Çalıştırın:
```powershell
python vericogaltma.py
```

### Scenario 3: Gelişmiş Veri Çoğaltma
1. `config.json` dosyasını düzenleyin:
```json
{
  "api_settings": {
    "providers": [
      {
        "name": "gemini",
        "api_keys": ["API_KEY_1", "API_KEY_2"],
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
```

2. Çalıştırın:
```powershell
python gelismis_vericogaltma.py
```

## 📊 Örnek Veri Dosyaları

Klasörde bulunan örnek dosyalar:
- `train.json` - Ana eğitim verisi
- `test.json` - Test verisi
- `quiz.json` - Quiz verileri
- `egitim.json` - Eğitim verileri

## ⚠️ Önemli Notlar

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

## 🔧 Sorun Giderme

### Yaygın Hatalar:
1. **ModuleNotFoundError**: `pip install -r requirements.txt`
2. **API Key Error**: Anahtarları doğru konfigüre edin
3. **Rate Limit Error**: İstek sayısını azaltın
4. **File Not Found**: Dosya yollarını kontrol edin

### Debug Modları:
Hata ayıklama için dosyalarda bulunan debug flaglerini aktifleştirin.

## 📈 İşlem İstatistikleri

Araçlar çalışırken size şu bilgileri sağlar:
- İşlenen dosya sayısı
- Oluşturulan veri sayısı  
- API çağrı istatistikleri
- Hata ve başarı oranları

## Özellikler

### Basit Versiyon
- Mevcut klasördeki tüm JSON dosyalarını işler
- Kaynak alanlarını otomatik bulur ve kaldırır
- UTF-8 kodlaması desteği

### Gelişmiş Versiyon
- 🎯 **Esnek kullanım**: Tek dosya, tüm klasör veya belirli klasör seçimi
- 💾 **Yedek alma**: Orijinal dosyaları güvenle saklar
- 📊 **Detaylı raporlama**: Hangi kaynak alanlarının kaldırıldığını gösterir
- 📏 **Boyut analizi**: Dosya boyutundaki değişimi raporlar
- 🔍 **Kaynak analizi**: İşlem öncesi kaynak alanlarını listeler

## Veri Çoğaltma Özellikleri

### Basit Versiyon (vericogaltma.py)
- Gemini API desteği
- Sabit 10 varyasyon üretimi
- Sıralı işlem

### Gelişmiş Versiyon (gelismis_vericogaltma.py)
- 🚀 **Çoklu API desteği**: Gemini ve OpenAI
- ⚡ **Eşzamanlı işlem**: Çoklu thread desteği
- 🎛️ **Dinamik konfigürasyon**: JSON dosyası ile ayarlanabilir
- 📈 **Esnek varyasyon sayısı**: Min-max aralığında ayarlanabilir
- 🔒 **Rate limiting**: API limitlerine uygun gecikme
- 💾 **Otomatik yedekleme**: İşlem öncesi veri yedeği
- 📊 **Detaylı loglama**: İşlem takibi ve hata raporlama
- 🎯 **Akıllı dağılım**: Load balancing ile API kullanımı

## Konfigürasyon (config.json)

### API Ayarları
- Çoklu API sağlayıcı desteği
- Provider başına enable/disable
- Rate limiting ayarları
- Model seçimi

### Çoğaltma Ayarları
- Dinamik varyasyon sayısı (5-20 arası)
- Varyasyon tiplerinin dağılımı
- Batch işlem boyutu

### İşlem Ayarları
- Eşzamanlı istek sayısı
- Girdi/çıktı dosya yolları
- Yedekleme seçenekleri

## Kaldırılan Alan Adları

Betik aşağıdaki alan adlarını arar ve kaldırır:
- `kaynak`
- `source`
- `kaynaklar`
- `sources`
- `referans`
- `reference`

## Güvenlik

- Gelişmiş versiyonda otomatik yedek oluşturma
- UTF-8 karakter desteği
- Hata durumunda dosya bozulmasını önleme

## Örnek

**Önce:**
```json
{
  "soru": "Python nedir?",
  "cevap": "Python bir programlama dilidir",
  "kaynak": "Python Documentation"
}
```

**Sonra:**
```json
{
  "soru": "Python nedir?",
  "cevap": "Python bir programlama dilidir"
}
```
