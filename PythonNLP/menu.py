#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from collections import Counter
import pandas as pd
from typing import List, Dict

def load_qa_data() -> List[Dict]:
    """Soru-cevap verilerini yükler"""
    # Önce final dosyayı kontrol et
    if os.path.exists('qa_output.json'):
        with open('qa_output.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Final dosya yoksa interim dosyayı kontrol et
    if os.path.exists('interim_qa_output.json'):
        with open('interim_qa_output.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []

def analyze_data(qa_data: List[Dict]):
    """Soru-cevap verilerini analiz eder"""
    if not qa_data:
        print("❌ Analiz edilecek veri bulunamadı!")
        print("Önce soru-cevap üretimi yapmalısınız.")
        return
    
    # Temel istatistikler
    total_qa = len(qa_data)
    sources = Counter(qa['kaynak'] for qa in qa_data)
    
    print("\n📊 VERİ ANALİZİ")
    print("=" * 40)
    print(f"Toplam Soru-Cevap Çifti: {total_qa}")
    print(f"Kaynak PDF Sayısı: {len(sources)}")
    
    # Kaynak bazlı analiz
    print("\n📚 KAYNAK BAZLI ANALİZ")
    print("-" * 40)
    print(f"{'PDF Adı':<50} {'Soru Sayısı':>10}")
    print("-" * 40)
    for source, count in sources.most_common():
        print(f"{source[:47] + '...' if len(source) > 47 else source:<50} {count:>10}")
    
    # Soru uzunluğu analizi
    soru_uzunluklari = [len(qa['soru'].split()) for qa in qa_data]
    cevap_uzunluklari = [len(qa['cevap'].split()) for qa in qa_data]
    
    print("\n📝 SORU-CEVAP ANALİZİ")
    print("-" * 40)
    print(f"Ortalama Soru Uzunluğu: {sum(soru_uzunluklari)/len(soru_uzunluklari):.1f} kelime")
    print(f"Ortalama Cevap Uzunluğu: {sum(cevap_uzunluklari)/len(cevap_uzunluklari):.1f} kelime")
    
    # Örnek soru-cevap çiftleri
    print("\n📖 ÖRNEK SORU-CEVAP ÇİFTLERİ")
    print("-" * 40)
    for i, qa in enumerate(qa_data[:3], 1):
        print(f"\n{i}. Soru: {qa['soru']}")
        print(f"   Cevap: {qa['cevap'][:200]}...")
        print(f"   Kaynak: {qa['kaynak']}")

def show_examples():
    """Örnek soru-cevap çiftlerini gösterir"""
    qa_data = load_qa_data()
    if not qa_data:
        print("❌ Gösterilecek örnek bulunamadı!")
        print("Önce soru-cevap üretimi yapmalısınız.")
        return
    
    print("\n📖 ÖRNEK SORU-CEVAP ÇİFTLERİ")
    print("=" * 40)
    
    # Rastgele 5 örnek göster
    import random
    samples = random.sample(qa_data, min(5, len(qa_data)))
    
    for i, qa in enumerate(samples, 1):
        print(f"\n{i}. Soru: {qa['soru']}")
        print(f"   Cevap: {qa['cevap']}")
        print(f"   Kaynak: {qa['kaynak']}")
        print("-" * 40)

def cleanup():
    """Geçici dosyaları temizler"""
    files_to_clean = ['interim_qa_output.json']
    
    for file in files_to_clean:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ {file} silindi")
            except Exception as e:
                print(f"❌ {file} silinirken hata oluştu: {e}")

def show_menu():
    """Ana menüyü gösterir"""
    while True:
        print("\n📋 SEÇENEKLER:")
        print("1. 🚀 PDF'leri işle ve soru-cevap üret")
        print("2. 📊 Mevcut verileri analiz et")
        print("3. ⚙️  Sistem kurulumu yap")
        print("4. 📖 Örnek verileri göster")
        print("5. 🧹 Temizlik yap")
        print("0. ❌ Çıkış")
        
        try:
            choice = input("\nSeçiminizi yapın (0-5): ")
            
            if choice == "1":
                # PDF işleme modülünü çağır
                import pdf_to_qa_gemini
                pdf_to_qa_gemini.main()
            
            elif choice == "2":
                print("\n📊 Veri analizi başlatılıyor...")
                analyze_data(load_qa_data())
            
            elif choice == "3":
                # Kurulum modülünü çağır
                import setup_qa_generator
                setup_qa_generator.main()
            
            elif choice == "4":
                show_examples()
            
            elif choice == "5":
                cleanup()
            
            elif choice == "0":
                print("\n👋 Güle güle!")
                break
            
            else:
                print("\n❌ Geçersiz seçim!")
            
            input("\nDevam etmek için Enter'a basın...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Program sonlandırıldı.")
            break
        except Exception as e:
            print(f"\n❌ Bir hata oluştu: {e}")
            input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    show_menu() 