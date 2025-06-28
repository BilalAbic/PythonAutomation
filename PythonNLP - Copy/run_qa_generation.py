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
    
    print(f"✅ {len(pdf_files)} PDF dosyası bulundu")
    return True

def get_api_key():
    """API anahtarını kullanıcıdan alır veya dosyadan okur"""
    # Önce dosyadan kontrol et
    try:
        with open("pdf_to_qa_gemini.py", "r", encoding="utf-8") as f:
            content = f.read()
            if 'YOUR_GEMINI_API_KEY_HERE' not in content:
                # API anahtarı zaten ayarlanmış
                import re
                match = re.search(r'API_KEY = ["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except:
        pass
    
    print("\n🔑 API Anahtarı Gerekli!")
    print("Google AI Studio'dan API anahtarı alın: https://makersuite.google.com/app/apikey")
    
    api_key = input("API anahtarınızı girin: ").strip()
    
    if len(api_key) < 20:
        print("❌ Geçersiz API anahtarı!")
        return None
    
    return api_key

def main():
    print("🤖 PDF'den Soru-Cevap Üreticisi")
    print("=" * 40)
    
    # Sistem kontrolü
    if not check_requirements():
        print("\n❌ Sistem kontrolü başarısız! Çıkılıyor...")
        return
    
    # API anahtarını al
    api_key = get_api_key()
    if not api_key:
        print("\n❌ API anahtarı gerekli! Çıkılıyor...")
        return
    
    print(f"\n🚀 İşlem başlatılıyor...")
    print("⏳ Bu işlem uzun sürebilir, lütfen bekleyiniz...")
    
    # Converter'ı başlat
    try:
        converter = PDFToQAConverter(api_key)
        
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
