# JSON Kaynak Temizleyici ve Veri Çoğaltma Araçları

Bu Python betikleri JSON dosyalarınızdan kaynak bilgilerini kaldırmanızı ve AI ile veri çoğaltma yapmanızı sağlar.

## Dosyalar

### Kaynak Temizleme Araçları
1. **kaynak_kaldir.py** - Basit versiyon
2. **gelismis_kaynak_kaldir.py** - Gelişmiş özelliklerle

### Veri Çoğaltma Araçları
3. **vericogaltma.py** - Basit AI veri çoğaltma
4. **gelismis_vericogaltma.py** - Gelişmiş çoklu API ve eşzamanlı veri çoğaltma
5. **config.json** - Konfigürasyon dosyası

### Diğer Dosyalar
6. Örnek JSON dosyaları (test için)
7. **requirements.txt** - Gerekli Python paketleri

## Kullanım

### Basit Versiyon
```bash
python kaynak_kaldir.py
```

### Gelişmiş Versiyon
```bash
python gelismis_kaynak_kaldir.py
```

### Veri Çoğaltma Araçları

#### Kurulum
```bash
pip install -r requirements.txt
```

#### Basit Veri Çoğaltma
```bash
python vericogaltma.py
```

#### Gelişmiş Veri Çoğaltma
1. `config.json` dosyasını API anahtarlarınızla güncelleyin
2. Çalıştırın:
```bash
python gelismis_vericogaltma.py
```

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
