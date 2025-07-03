# 🤖 Advanced PDF to ML Training Dataset Generator

Bu proje, PDF dosyalarından makine öğrenmesi modelleri için **yüksek kaliteli eğitim verisi** üretmek için geliştirilmiş gelişmiş bir sistemdir. GPT-4, Claude, Gemini gibi büyük dil modellerinin eğitiminde kullanılabilir seviyede soru-cevap çiftleri oluşturur.

## 🚀 Özellikler

### ✨ Gelişmiş Özellikler
- **🎯 ML-Optimized**: Model eğitimi için özel olarak tasarlanmış
- **📊 Kalite Kontrolü**: Otomatik kalite skorlaması ve filtreleme
- **🏷️ Kategori Çeşitliliği**: 5 farklı soru kategorisi (Faktuel, Kavramsal, Analitik, Uygulama, Eleştirel)
- **📈 Zorluk Seviyeleri**: Temel, Orta, İleri seviyelerinde dengeli dağılım
- **🔍 Anahtar Kelime Çıkarımı**: Her soru için otomatik anahtar kelime üretimi
- **📝 Metadata Zenginleştirme**: ML eğitimi için gerekli metadata'lar

### 🛡️ Güvenlik ve Stabilite
- **🔄 API Key Rotation**: Çoklu API key desteği ve otomatik rotasyon
- **⏱️ Rate Limiting**: Akıllı rate limiting ve quota yönetimi
- **🚨 Emergency Stop**: Acil durum durdurma sistemi
- **💾 Checkpoint**: Süreç devam ettirme özelliği
- **📊 Monitoring**: Gerçek zamanlı performans izleme

### 📊 Veri Kalitesi
- **🎯 Kalite Skoru**: Her soru-cevap çifti için 0-100 arası kalite skoru
- **🚫 Filtre Sistemi**: Yasak referansları, belirsiz dili otomatik tespit
- **📏 Uzunluk Kontrolü**: Optimal soru-cevap uzunluğu garantisi
- **🔍 Duplikasyon Kontrolü**: Tekrar eden soruları engelleme

## 📦 Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### API Key Kurulumu
1. `config_example.json`'ı `config.json` olarak kopyalayın
2. Gemini API key'lerinizi ekleyin:
```json
{
  "api_keys": [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2"
  ]
}
```

## 🎯 Kullanım

### 1. Temel Kullanım
```bash
# Ana script ile çalıştırma
python main.py --config config.json

# Enhanced processor ile çalıştırma  
python enhanced_pdf_processor.py
```

### 2. PDF'leri Hazırlama
```bash
# pdfs/ klasörüne PDF dosyalarınızı yerleştirin
mkdir pdfs
cp *.pdf pdfs/
```

### 3. Veri Kalitesi Analizi
```bash
# Üretilen veriyi analiz etme
python data_quality_analyzer.py --data-file output_json/toplam_egitim_veriseti.jsonl
```

## 📊 Çıktı Formatı

### ML Training Format
```json
{
  "soru": "Makine öğrenmesinde overfitting nasıl önlenir?",
  "cevap": "Overfitting, modelin eğitim verisine aşırı uyum sağlayıp...",
  "kategori": "Kavramsal Anlama",
  "zorluk": "Orta", 
  "anahtar_kelimeler": ["overfitting", "regularizasyon", "validation"],
  "kaynak_tipi": "metin",
  "kalite_skoru": 85,
  "kelime_sayisi": 127,
  "karakter_sayisi": 892,
  "kaynak_dosya": "ml_book_chapter1",
  "uretim_tarihi": "2024-01-15T10:30:00",
  "model_versiyonu": "gemini-1.5-flash-latest"
}
```

## 🎛️ Konfigürasyon

### Ana Parametreler
```json
{
  "pdf_processing": {
    "max_questions_per_pdf": 25,
    "model_name": "gemini-1.5-flash-latest"
  },
  "quality_control": {
    "quality_threshold": 70,
    "min_answer_length": 100,
    "max_answer_length": 1600
  },
  "ml_training": {
    "target_dataset_size": 1000,
    "min_quality_score": 75
  }
}
```

## 📈 Kalite Metrikleri

### Kalite Skorlaması (0-100)
- **Uzunluk Kontrolü** (25 puan): Optimal soru-cevap uzunluğu
- **İçerik Kalitesi** (20 puan): Yasak referanslar, netlik
- **Kategori Uyumu** (10 puan): Doğru kategori ataması
- **Zorluk Uyumu** (10 puan): Uygun zorluk seviyesi
- **Anahtar Kelime** (10 puan): Kaliteli anahtar kelimeler
- **Dil Kalitesi** (10 puan): Belirsiz ifade kontrolü
- **Spesifiklik** (5 puan): Spesifik içerik göstergeleri

### ML Hazırlık Skoru
- **Veri Hacmi** (20 puan): Toplam soru-cevap sayısı
- **Kategori Çeşitliliği** (20 puan): Farklı kategori sayısı
- **Ortalama Kalite** (25 puan): Kalite skorları ortalaması
- **Uzunluk Dağılımı** (15 puan): İdeal uzunluk aralığında olanlar
- **Veri Tutarlılığı** (20 puan): Hata oranı ve duplikasyon

## 📊 Analiz ve Raporlama

### Veri Kalitesi Raporu
```bash
python data_quality_analyzer.py
```

Çıktılar:
- `output/data_quality_report.txt`: İnsan-okunabilir rapor
- `output/data_quality_analysis.json`: Detaylı analiz verileri

### Örnek Analiz Çıktısı
```
🎯 VERİ KALİTESİ ANALİZ ÖZETİ
================================================================================
📊 Toplam veri: 847 kayıt
⭐ ML Hazırlık Skoru: 85/100 (85.0%)
🏆 Değerlendirme: Good - Ready for ML training with minor improvements
📈 Ortalama kalite: 78.5
```

## 🛡️ Güvenlik Özellikleri

### API Key Yönetimi
- Çoklu API key desteği
- Otomatik key rotasyonu
- Quota aşım tespiti
- Health monitoring

### Hata Toleransı
- Exponential backoff
- Graceful shutdown
- Emergency stop mekanizması
- Checkpoint/resume özelliği

## 🔧 Gelişmiş Kullanım

### Çoklu Makine Desteği
```json
{
  "multi_machine": {
    "machine_id": 0,
    "total_machines": 3
  }
}
```

### Performance Tuning
```json
{
  "pdf_processing": {
    "num_workers": 4,
    "api_timeout_seconds": 600
  },
  "safety_settings": {
    "min_delay_between_calls": 3,
    "adaptive_delay": true
  }
}
```

## 📁 Proje Yapısı

```
PythonNLPRAG/
├── main.py                     # Ana işlem scripti
├── enhanced_pdf_processor.py   # Gelişmiş processor
├── pdf_api_manager.py         # API key yönetimi
├── data_quality_analyzer.py   # Kalite analizi
├── config_example.json        # Örnek konfig
├── requirements.txt           # Python bağımlılıkları
├── pdfs/                      # PDF dosyaları
├── output_json/               # Üretilen veriler
├── output/                    # Analiz raporları
├── logs/                      # Log dosyaları
└── checkpoints/               # Checkpoint dosyaları
```

## 🎯 En İyi Pratikler

### Veri Kalitesi İçin
1. **Çeşitli PDF'ler**: Farklı konularda, farklı yapılarda PDF'ler kullanın
2. **Kalite Kontrolü**: Düzenli olarak `data_quality_analyzer.py` çalıştırın
3. **Prompt Optimizasyonu**: Düşük kalite skorunda prompt'u iyileştirin
4. **Kategori Dengesi**: Tüm kategorilerden yeterli örnek olduğundan emin olun

### Performans İçin
1. **API Key Sayısı**: En az 3-5 API key kullanın
2. **Rate Limiting**: Conservative ayarlarla başlayın
3. **Batch Processing**: Büyük PDF'leri chunk'lara bölün
4. **Monitoring**: Log dosyalarını düzenli kontrol edin

## 🐛 Sorun Giderme

### Yaygın Sorunlar
1. **API Quota Aşımı**: Daha fazla API key ekleyin
2. **Düşük Kalite Skoru**: Prompt'u iyileştirin
3. **Yavaş İşlem**: `num_workers` artırın
4. **Memory Error**: Chunk size'ı küçültün

### Log Kontrolü
```bash
tail -f logs/pdf_processor_*.log
```

## 📄 Lisans

Bu proje açık kaynaklıdır ve MIT lisansı altında dağıtılmaktadır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 Destek

Sorularınız için:
- Issue açın: GitHub Issues
- Dokümantasyon: Bu README dosyası
- Log analizi: `logs/` klasörünü kontrol edin

---

⭐ **Bu proje ile yüksek kaliteli ML eğitim verisi üretin!** ⭐
