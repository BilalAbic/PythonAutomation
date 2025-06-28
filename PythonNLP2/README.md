# PythonNLP2 - Veri Analizi ve Birleştirme Araçları

Bu modül, çeşitli veri formatlarında (CSV, JSON) bulunan dosyaları analiz etme, birleştirme ve temizleme işlemlerini gerçekleştiren Python araçlarını içerir.

## 🎯 Modül Özellikleri

- **CSV Dosya Birleştirme**: Çoklu CSV dosyalarını tek dosyada birleştirme
- **Veri Temizleme**: Mükerrer kayıtları temizleme ve veri kalitesi kontrolü
- **Format Dönüştürme**: CSV, JSON formatları arası dönüştürme
- **Veri Analizi**: İstatistiksel analiz ve raporlama
- **Tekrar Eden Veri Kontrolü**: Veri setlerinde tekrar kontrolü

## 📋 Gereksinimler

- **Python 3.7+**
- **pandas**: Veri manipülasyonu için
- **numpy**: Sayısal işlemler için

### Python Paketleri:
```
pandas>=1.3.0
numpy>=1.20.0
```

## ⚙️ Kurulum

```powershell
# Gerekli paketleri yükleyin
pip install pandas numpy
```

## 📁 Dosya Yapısı ve İşlevleri

### Veri Birleştirme Araçları

#### 1. `test.py` - CSV Dosya Birleştirici
**Ne yapar:**
- Belirli bir klasördeki tüm CSV dosyalarını okur
- Dosyaları tek bir CSV dosyasında birleştirir
- Hata durumlarını yönetir
- İşlem sonucu hakkında bilgi verir

**Nasıl çalıştırılır:**
```powershell
python test.py
```

**Çalıştırmadan önce yapılması gerekenler:**
1. Birleştirilecek CSV dosyalarını `csv_klasoru` klasörüne yerleştirin
2. Dosya yolunu gerekirse güncelleyin (satır 4: `klasor_yolu`)
3. Çıktı dosya adını istediğiniz gibi değiştirin (satır 28)

**Kod yapısı:**
```python
# CSV dosyalarının bulunduğu klasör
klasor_yolu = "csv_klasoru"

# Birleştirilmiş veriyi tutacak liste
birlesik_veri = []

# Klasördeki tüm CSV dosyalarını oku
for dosya in os.listdir(klasor_yolu):
    if dosya.endswith(".csv"):
        # CSV dosyasını oku ve listeye ekle
        df = pd.read_csv(dosya_yolu)
        birlesik_veri.append(df)

# Tüm DataFrame'leri birleştir
final_df = pd.concat(birlesik_veri, ignore_index=True)
# Sonuçları yeni bir CSV dosyasına yaz
final_df.to_csv("birlesik_verii.csv", index=False)
```

#### 2. `test2.py` - Gelişmiş Veri Analizi
**Ne yapar:**
- Daha karmaşık veri analizi işlemleri
- İstatistiksel hesaplamalar
- Veri kalitesi kontrolü

**Nasıl çalıştırılır:**
```powershell
python test2.py
```

### Veri Temizleme Araçları

#### 3. `veritemizleme.py` - Veri Temizleme ve Filtreleme
**Ne yapar:**
- Mükerrer kayıtları temizler
- Eksik veri kontrolü yapar
- Veri formatı standardizasyonu
- Kalite filtreleme

**Nasıl çalıştırılır:**
```powershell
python veritemizleme.py
```

#### 4. `tekraredenyapivarmi.py` - Tekrar Eden Veri Kontrolü
**Ne yapar:**
- Veri setlerinde tekrarlayan kayıtları tespit eder
- Benzerlik analizi yapar
- Temizlik önerileri sunar

**Nasıl çalıştırılır:**
```powershell
python tekraredenyapivarmi.py
```

## 📊 Mevcut Veri Dosyaları

Klasörde bulunan örnek veri dosyaları:

- **`birlesik_veri.csv`**: Birleştirilmiş CSV verisi
- **`birlesik_verii.csv`**: Güncellenmiş birleştirilmiş veri
- **`combined_output.json`**: JSON formatında birleştirilmiş veri
- **`FitAsistan_Bolgesel_SoruCevap.csv`**: Fitness asistanı soru-cevap verileri
- **`qa_pairs.json`**: Soru-cevap çiftleri JSON formatında

## 🚀 Kullanım Senaryoları

### Scenario 1: Çoklu CSV Dosyalarını Birleştirme

```powershell
# 1. CSV dosyalarınızı hazırlayın
mkdir csv_klasoru
# CSV dosyalarınızı csv_klasoru klasörüne kopyalayın

# 2. Birleştirme işlemini başlatın
python test.py

# 3. Sonuç: birlesik_verii.csv dosyası oluşturulur
```

### Scenario 2: Veri Temizleme İşlemi

```powershell
# 1. Temizlenecek veri dosyasını hazırlayın
# 2. Temizleme scriptini çalıştırın
python veritemizleme.py

# 3. Temizlenmiş veri çıktısını kontrol edin
```

### Scenario 3: Tekrar Eden Veri Kontrolü

```powershell
# Veri setinizde tekrarları kontrol edin
python tekraredenyapivarmi.py
```

## ⚙️ Konfigürasyon ve Özelleştirme

### CSV Birleştirme Özelleştirme (`test.py`):

```python
# Klasör yolunu değiştirme
klasor_yolu = "sizin_klasor_yolunuz"

# Çıktı dosya adını değiştirme
final_df.to_csv("yeni_birlesik_dosya.csv", index=False)

# Sadece belirli CSV dosyalarını işleme
if dosya.startswith("belirli_") and dosya.endswith(".csv"):
    # İşleme kodu
```

### Veri Filtreleme Seçenekleri:

```python
# Boş değerleri kaldırma
df = df.dropna()

# Tekrarlı satırları kaldırma
df = df.drop_duplicates()

# Belirli koşullara göre filtreleme
df = df[df['kolon_adi'] > belirli_deger]
```

## 📈 Veri Analizi Özellikleri

### Temel İstatistikler:
- Satır ve sütun sayısı
- Eksik veri oranları
- Veri türü dağılımları
- Tekrar eden kayıt sayısı

### Kalite Kontrol:
- Veri bütünlüğü kontrolü
- Format tutarlılığı
- Değer aralığı kontrolü

## ⚠️ Önemli Notlar

### Performans Considerations:
- **Büyük dosyalar**: Çok büyük CSV dosyaları için chunk-based okuma kullanın
- **Bellek kullanımı**: RAM kapasitesine dikkat edin
- **İşlem süresi**: Büyük veri setleri için zaman alabilir

### Veri Güvenliği:
- İşlem öncesi verilerinizi yedekleyin
- Çıktı dosyalarını kontrol edin
- Hassas verileri güvenli tutun

## 🔧 Sorun Giderme

### Yaygın Hatalar:

1. **FileNotFoundError:**
```powershell
# Dosya yollarını kontrol edin
import os
print(os.path.exists("csv_klasoru"))
```

2. **Memory Error:**
```powershell
# Büyük dosyalar için chunk processing kullanın
chunk_size = 10000
for chunk in pd.read_csv("buyuk_dosya.csv", chunksize=chunk_size):
    # İşleme kodu
```

3. **Encoding Hatası:**
```python
# Farklı encoding'ler deneyin
df = pd.read_csv("dosya.csv", encoding='utf-8')
# veya
df = pd.read_csv("dosya.csv", encoding='latin-1')
```

### Debug İpuçları:
```python
# Veri yapısını kontrol etme
print(df.info())
print(df.describe())
print(df.head())

# Eksik veri kontrolü
print(df.isnull().sum())
```

## 📊 Çıktı Formatları

### CSV Çıktı:
```csv
kolon1,kolon2,kolon3
değer1,değer2,değer3
değer4,değer5,değer6
```

### JSON Çıktı:
```json
[
  {
    "kolon1": "değer1",
    "kolon2": "değer2",
    "kolon3": "değer3"
  }
]
```

Bu modül ile veri analizi ve birleştirme işlemlerinizi verimli bir şekilde gerçekleştirebilirsiniz.
