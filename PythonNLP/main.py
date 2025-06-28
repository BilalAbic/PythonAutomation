#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF'den Soru-Cevap Üretimi - Ana Kontrol Sistemi
Bu script tüm süreci yönetir ve kullanıcıya seçenekler sunar.
"""

import os
import sys
import json

def print_banner():
    """Program başlığını yazdırır"""
    print("🤖 PDF'den Soru-Cevap Üretimi Sistemi")
    print("=" * 45)
    print("Beslenme ve Sağlık PDF'lerinden Gemini AI ile")
    print("otomatik soru-cevap çiftleri oluşturur.\n")

def check_system():
    """Sistem durumunu kontrol eder"""
    print("🔍 Sistem Durumu:")
    
    # PDF klasörü
    pdf_count = 0
    if os.path.exists("pdfs"):
        pdf_files = [f for f in os.listdir("pdfs") if f.endswith('.pdf')]
        pdf_count = len(pdf_files)
        print(f"  ✅ PDF klasörü: {pdf_count} dosya")
    else:
        print("  ❌ PDF klasörü bulunamadı")
    
    # Mevcut sonuçlar
    results_exist = os.path.exists("pdf_qa_pairs.json")
    if results_exist:
        try:
            with open("pdf_qa_pairs.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✅ Mevcut veriler: {len(data)} soru-cevap çifti")
        except:
            print("  ⚠️  Mevcut veri dosyası bozuk")
            results_exist = False
    else:
        print("  📝 Henüz soru-cevap verisi oluşturulmamış")
    
    # Gerekli dosyalar
    required_files = [
        "pdf_to_qa_gemini.py",
        "run_qa_generation.py", 
        "analyze_qa_data.py",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"  ❌ Eksik dosyalar: {', '.join(missing_files)}")
    else:
        print("  ✅ Tüm sistem dosyaları mevcut")
    
    return pdf_count, results_exist, not missing_files

def show_menu():
    """Ana menüyü gösterir"""
    print("\n📋 SEÇENEKLER:")
    print("1. 🚀 PDF'leri işle ve soru-cevap üret")
    print("2. 📊 Mevcut verileri analiz et")
    print("3. 🧹 Verileri temizle ve kalite kontrol yap")
    print("4. ⚙️  Sistem kurulumu yap")
    print("5. 📖 Örnek verileri göster")
    print("6. 🗑️  Dosya temizliği yap")
    print("0. ❌ Çıkış")
    
    choice = input("\nSeçiminizi yapın (0-6): ").strip()
    return choice

def run_setup():
    """Kurulum işlemini çalıştırır"""
    print("\n⚙️  Sistem kurulumu başlatılıyor...")
    os.system("python setup_qa_generator.py")

def run_generation():
    """Soru-cevap üretimini çalıştırır"""
    print("\n🚀 Soru-cevap üretimi başlatılıyor...")
    print("⚠️  Bu işlem uzun sürebilir ve internet bağlantısı gerektirir!")
    
    confirm = input("Devam etmek istiyor musunuz? (e/h): ").lower()
    if confirm in ['e', 'evet', 'y', 'yes']:
        os.system("python run_qa_generation.py")
    else:
        print("İşlem iptal edildi.")

def run_analysis():
    """Veri analizini çalıştırır"""
    print("\n📊 Veri analizi başlatılıyor...")
    
    if not os.path.exists("pdf_qa_pairs.json"):
        print("❌ Analiz edilecek veri bulunamadı!")
        print("Önce soru-cevap üretimi yapmalısınız.")
        return
    
    os.system("python analyze_qa_data.py")

def run_data_cleaning():
    """Veri temizleme işlemini çalıştırır"""
    print("\n🧹 Veri temizleme başlatılıyor...")
    
    if not os.path.exists("iki_kaynak_birlesimi.json"):
        print("❌ Temizlenecek veri bulunamadı!")
        print("Önce soru-cevap üretimi yapmalısınız.")
        return
    
    print("⚠️  Bu işlem mevcut verileri analiz edip kalitesiz olanları kaldıracak!")
    confirm = input("Devam etmek istiyor musunuz? (e/h): ").lower()
    if confirm in ['e', 'evet', 'y', 'yes']:
        os.system("python data_cleaner.py")
    else:
        print("İşlem iptal edildi.")

def show_sample_data():
    """Örnek verileri gösterir"""
    print("\n📖 Örnek veriler:")
    
    if not os.path.exists("pdf_qa_pairs.json"):
        print("❌ Veri dosyası bulunamadı!")
        return
    
    try:
        with open("pdf_qa_pairs.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ Veri dosyası boş!")
            return
        
        print(f"\nToplam {len(data)} soru-cevap çifti bulundu.")
        print("\nİlk 3 örnek:")
        print("-" * 40)
        
        for i, item in enumerate(data[:3]):
            print(f"\n[{i+1}] Kaynak: {item.get('kaynak', 'Bilinmeyen')}")
            print(f"Soru: {item.get('soru', 'Soru bulunamadı')}")
            print(f"Cevap: {item.get('cevap', 'Cevap bulunamadı')[:150]}...")
            
    except Exception as e:
        print(f"❌ Veri okuma hatası: {e}")

def cleanup():
    """Dosya temizlik işlemleri"""
    print("\n🗑️  Dosya temizlik seçenekleri:")
    print("1. Ara dosyaları sil (interim_*.json)")
    print("2. Tüm sonuç dosyalarını sil")
    print("3. Sadece analiz dosyalarını sil")
    print("4. Temizlenmiş veri dosyalarını sil")
    print("5. Yedek dosyaları sil")
    print("0. İptal")
    
    choice = input("Seçiminiz: ").strip()
    
    if choice == "1":
        count = 0
        for file in os.listdir("."):
            if file.startswith("interim_") and file.endswith(".json"):
                os.remove(file)
                print(f"Silindi: {file}")
                count += 1
        print(f"Toplam {count} ara dosya silindi.")
    
    elif choice == "2":
        files_to_remove = [
            "pdf_qa_pairs.json",
            "cleaned_qa_pairs.json",
            "qa_pairs_export.csv",
            "training_data.jsonl",
            "qa_by_topics.json",
            "quality_qa_pairs.json"
        ]
        count = 0
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                print(f"Silindi: {file}")
                count += 1
        print(f"Toplam {count} sonuç dosyası silindi.")
    
    elif choice == "3":
        analysis_files = [
            "qa_pairs_export.csv",
            "training_data.jsonl", 
            "qa_by_topics.json",
            "quality_qa_pairs.json"
        ]
        count = 0
        for file in analysis_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Silindi: {file}")
                count += 1
        print(f"Toplam {count} analiz dosyası silindi.")
    
    elif choice == "4":
        cleaning_files = [
            "cleaned_qa_pairs.json"
        ]
        count = 0
        for file in cleaning_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Silindi: {file}")
                count += 1
        print(f"Toplam {count} temizlenmiş veri dosyası silindi.")
    
    elif choice == "5":
        count = 0
        for file in os.listdir("."):
            if file.startswith("backup_") and file.endswith(".json"):
                os.remove(file)
                print(f"Silindi: {file}")
                count += 1
        print(f"Toplam {count} yedek dosya silindi.")
    
    elif choice == "0":
        print("İptal edildi.")
    
    else:
        print("Geçersiz seçim!")

def main():
    """Ana program döngüsü"""
    while True:
        print_banner()
        
        # Sistem durumunu kontrol et
        pdf_count, results_exist, system_ok = check_system()
        
        if not system_ok:
            print("\n❌ Sistem dosyaları eksik! Önce kurulum yapın.")
        
        # Menüyü göster ve seçim al
        choice = show_menu()
        
        if choice == "0":
            print("\n👋 Görüşmek üzere!")
            break
        
        elif choice == "1":
            if pdf_count == 0:
                print("\n❌ PDF dosyası bulunamadı!")
                print("'pdfs' klasörüne PDF dosyalarını ekleyin.")
            elif not system_ok:
                print("\n❌ Önce sistem kurulumu yapın!")
            else:
                run_generation()
        
        elif choice == "2":
            run_analysis()
        
        elif choice == "3":
            run_data_cleaning()
        
        elif choice == "4":
            run_setup()
        
        elif choice == "5":
            show_sample_data()
        
        elif choice == "6":
            cleanup()
        
        else:
            print("\n❌ Geçersiz seçim! Lütfen 0-5 arası bir sayı girin.")
        
        # Devam için bekle
        input("\nDevam etmek için Enter'a basın...")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        print("Destek için sistem yöneticisine başvurun.")
