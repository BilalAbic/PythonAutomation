#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF'den Soru-Cevap Üretimi - Hızlı Başlatma
Bu script PDF dosyalarını Gemini API kullanarak soru-cevap formatına dönüştürür.
"""

import os
import sys
from pdf_to_qa_gemini import PDFToQAConverter

def check_requirements():
    """Gerekli dosya ve klasörlerin varlığını kontrol eder"""
    print("🔍 Sistem kontrolü yapılıyor...")
    
    # PDF klasörü kontrolü
    if not os.path.exists("pdfs"):
        print("❌ 'pdfs' klasörü bulunamadı!")
        return False
    
    # PDF dosyalarını say
    pdf_files = [f for f in os.listdir("pdfs") if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ 'pdfs' klasöründe PDF dosyası bulunamadı!")
        return False
    
    # Config dosyası kontrolü
    if not os.path.exists("config.json"):
        print("❌ 'config.json' dosyası bulunamadı!")
        print("Lütfen setup_qa_generator.py'yi çalıştırarak kurulumu tamamlayın.")
        return False
    
    print(f"✅ {len(pdf_files)} PDF dosyası bulundu")
    return True

def main():
    print("🤖 PDF'den Soru-Cevap Üreticisi")
    print("=" * 40)
    
    # Sistem kontrolü
    if not check_requirements():
        print("\n❌ Sistem kontrolü başarısız! Çıkılıyor...")
        return
    
    print(f"\n🚀 İşlem başlatılıyor...")
    print("⏳ Bu işlem uzun sürebilir, lütfen bekleyiniz...")
    
    # Converter'ı başlat
    try:
        converter = PDFToQAConverter()  # config.json'dan okuyacak
        
        # Ayarlar
        pdf_folder = "pdfs"
        output_file = "pdf_qa_pairs.json"
        
        # İşlemi başlat
        converter.process_all_pdfs(pdf_folder, output_file)
        
        print("\n🎉 İşlem başarıyla tamamlandı!")
        print(f"📄 Sonuçlar '{output_file}' dosyasına kaydedildi.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından iptal edildi.")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        print("Detaylar için pdf_to_qa_gemini.py dosyasını kontrol edin.")

if __name__ == "__main__":
    main()
