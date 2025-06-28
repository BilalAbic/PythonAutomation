#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF'den Soru-Cevap Sistemi - Demo ve Test
"""

import os
import json

def test_system():
    """Sistemi test eder"""
    print("🧪 PDF'den Soru-Cevap Sistemi - Test")
    print("=" * 40)
    
    # PDF klasörü kontrolü
    pdf_folder = "pdfs"
    if not os.path.exists(pdf_folder):
        print("❌ 'pdfs' klasörü bulunamadı!")
        return False
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"✅ {len(pdf_files)} PDF dosyası bulundu")
    
    if pdf_files:
        print("İlk 5 PDF dosyası:")
        for i, pdf in enumerate(pdf_files[:5]):
            print(f"  {i+1}. {pdf}")
        if len(pdf_files) > 5:
            print(f"  ... ve {len(pdf_files)-5} dosya daha")
    
    # Gerekli dosyaları kontrol et
    required_files = [
        "pdf_to_qa_gemini.py",
        "run_qa_generation.py",
        "analyze_qa_data.py",
        "main.py"
    ]
    
    print(f"\n📁 Sistem Dosyaları:")
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
            all_exist = False
    
    # Mevcut sonuçları kontrol et
    result_files = [
        ("pdf_qa_pairs.json", "Ana soru-cevap verisi"),
        ("qa_pairs_export.csv", "CSV formatı"),
        ("training_data.jsonl", "AI eğitim verisi"),
        ("qa_by_topics.json", "Konulara göre gruplu"),
        ("quality_qa_pairs.json", "Kaliteli veriler")
    ]
    
    print(f"\n📊 Sonuç Dosyaları:")
    for file, desc in result_files:
        if os.path.exists(file):
            try:
                if file.endswith('.json'):
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"  ✅ {file} - {len(data)} kayıt")
                else:
                    print(f"  ✅ {file}")
            except:
                print(f"  ⚠️  {file} - bozuk dosya")
        else:
            print(f"  📝 {file} - henüz oluşturulmamış")
    
    print(f"\n🎯 Kullanım Talimatları:")
    print("1. Google AI Studio'dan API anahtarı alın:")
    print("   https://makersuite.google.com/app/apikey")
    print("2. pdf_to_qa_gemini.py dosyasındaki API_KEY'i güncelleyin")
    print("3. Ana sistemi çalıştırın:")
    print("   python main.py")
    print("4. Veya hızlı başlatma için:")
    print("   python run_qa_generation.py")
    
    return all_exist and len(pdf_files) > 0

if __name__ == "__main__":
    try:
        success = test_system()
        if success:
            print(f"\n🎉 Sistem kullanıma hazır!")
        else:
            print(f"\n⚠️  Eksiklikler mevcut, kontrol edin.")
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
