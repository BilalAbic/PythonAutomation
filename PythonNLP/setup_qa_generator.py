#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF'den Soru-Cevap Üretimi - Kurulum ve Kullanım Rehberi
"""

print("PDF'den Soru-Cevap Üretimi Kurulum Başlatılıyor...")
print("=" * 50)

import subprocess
import sys
import os
import json

def install_requirements():
    """Gerekli paketleri yükler"""
    print("Gerekli Python paketleri yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Paketler başarıyla yüklendi!")
    except subprocess.CalledProcessError:
        print("❌ Paket yükleme hatası!")
        return False
    return True

def setup_api_keys():
    """API anahtarlarını yapılandırır"""
    print("\n📋 API Anahtarı Kurulumu:")
    print("1. Google AI Studio'ya gidin: https://makersuite.google.com/app/apikey")
    print("2. Bir veya daha fazla API anahtarı oluşturun")
    print("3. API anahtarlarını aşağıya girin (boş bırakarak sonlandırın)")
    
    api_keys = []
    key_count = 1
    
    while True:
        api_key = input(f"\n{key_count}. API anahtarını girin (boş bırakarak bitirin): ").strip()
        if not api_key:
            break
            
        if len(api_key) > 20:  # Basit kontrol
            api_keys.append(api_key)
            key_count += 1
        else:
            print("❌ Geçersiz API anahtarı!")
    
    if not api_keys:
        print("❌ En az bir API anahtarı gerekli!")
        return False
    
    # Yapılandırma dosyasını oluştur/güncelle
    config = {
        "api_keys": api_keys,
        "retry_settings": {
            "max_retries": 3,
            "retry_delay": 5,
            "rate_limit_delay": 10
        },
        "chunk_settings": {
            "chunk_size": 3000,
            "chunk_overlap": 200
        }
    }
    
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print(f"\n✅ {len(api_keys)} API anahtarı kaydedildi!")
        return True
    except Exception as e:
        print(f"❌ Yapılandırma dosyası oluşturma hatası: {e}")
        return False

def setup_folders():
    """Gerekli klasörleri oluşturur"""
    folders = ['pdfs']
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ '{folder}' klasörü oluşturuldu")
        else:
            print(f"✓ '{folder}' klasörü mevcut")

def main():
    print("🚀 Kurulum başlatılıyor...\n")
    
    # Klasörleri oluştur
    setup_folders()
    
    # Paketleri yükle
    if not install_requirements():
        return
    
    # API anahtarlarını ayarla
    if not setup_api_keys():
        print("\n⚠️  API anahtarlarını manuel olarak config.json dosyasında ayarlayın.")
    
    print("\n🎉 Kurulum tamamlandı!")
    print("\nKullanım:")
    print("1. PDF dosyalarını 'pdfs' klasörüne kopyalayın")
    print("2. python main.py komutunu çalıştırın")
    print("3. Menüden istediğiniz işlemi seçin")

if __name__ == "__main__":
    main()
