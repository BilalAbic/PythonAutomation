#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON dosyalarından kaynak bilgilerini kaldıran betik
"""

import json
import os
import glob
from pathlib import Path

def kaynak_kaldir(json_dosyasi):
    """
    Tek bir JSON dosyasından kaynak bilgilerini kaldırır
    """
    try:
        # JSON dosyasını oku
        with open(json_dosyasi, 'r', encoding='utf-8') as f:
            veri = json.load(f)
        
        # Kaynak alanlarını kaldır (farklı isimler olabilir)
        kaynak_alanlari = ['kaynak', 'source', 'kaynaklar', 'sources', 'referans', 'reference']
        
        def kaynak_temizle(obj):
            if isinstance(obj, dict):
                # Dictionary'den kaynak alanlarını kaldır
                for alan in kaynak_alanlari:
                    obj.pop(alan, None)
                
                # Alt seviyedeki nesneleri de temizle
                for key, value in obj.items():
                    obj[key] = kaynak_temizle(value)
                    
            elif isinstance(obj, list):
                # Liste içindeki her elemanı temizle
                return [kaynak_temizle(item) for item in obj]
            
            return obj
        
        # Veriyi temizle
        temiz_veri = kaynak_temizle(veri)
        
        # Temizlenmiş veriyi dosyaya yaz
        with open(json_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(temiz_veri, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {json_dosyasi} başarıyla temizlendi")
        return True
        
    except Exception as e:
        print(f"✗ {json_dosyasi} işlenirken hata: {str(e)}")
        return False

def main():
    """
    Ana fonksiyon - mevcut klasördeki tüm JSON dosyalarını işler
    """
    print("JSON Kaynak Temizleyici")
    print("=" * 30)
    
    # Mevcut klasördeki JSON dosyalarını bul
    json_dosyalari = glob.glob("*.json")
    
    if not json_dosyalari:
        print("Mevcut klasörde JSON dosyası bulunamadı!")
        print("Lütfen betiği JSON dosyalarının bulunduğu klasörde çalıştırın.")
        return
    
    print(f"{len(json_dosyalari)} JSON dosyası bulundu:")
    for dosya in json_dosyalari:
        print(f"  - {dosya}")
    
    print("\nİşleme başlanıyor...")
    
    # Her JSON dosyasını işle
    basarili = 0
    basarisiz = 0
    
    for dosya in json_dosyalari:
        if kaynak_kaldir(dosya):
            basarili += 1
        else:
            basarisiz += 1
    
    print("\nİşlem tamamlandı!")
    print(f"Başarılı: {basarili}")
    print(f"Başarısız: {basarisiz}")

if __name__ == "__main__":
    main()
