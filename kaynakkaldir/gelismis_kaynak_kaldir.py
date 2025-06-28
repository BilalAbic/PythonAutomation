#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş JSON Kaynak Temizleyici
- Yedek alma özelliği
- Belirli klasör seçme
- Detaylı raporlama
"""

import json
import os
import glob
import shutil
from pathlib import Path
from datetime import datetime

def yedek_olustur(dosya_yolu):
    """
    Dosyanın yedeğini oluşturur
    """
    yedek_klasor = Path("yedek")
    yedek_klasor.mkdir(exist_ok=True)
    
    dosya_adi = Path(dosya_yolu).name
    zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_adi = f"{dosya_adi}.{zaman_damgasi}.backup"
    yedek_yolu = yedek_klasor / yedek_adi
    
    shutil.copy2(dosya_yolu, yedek_yolu)
    return yedek_yolu

def kaynak_analiz_et(veri, yol=""):
    """
    JSON verisindeki kaynak alanlarını analiz eder
    """
    bulunan_kaynaklar = []
    
    def kaynak_bul(obj, mevcut_yol=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                yeni_yol = f"{mevcut_yol}.{key}" if mevcut_yol else key
                
                # Kaynak alanı kontrolü
                if key.lower() in ['kaynak', 'source', 'kaynaklar', 'sources', 'referans', 'reference']:
                    bulunan_kaynaklar.append({
                        'yol': yeni_yol,
                        'tip': type(value).__name__,
                        'icerik': str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    })
                
                # Alt seviyeleri de kontrol et
                kaynak_bul(value, yeni_yol)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                yeni_yol = f"{mevcut_yol}[{i}]"
                kaynak_bul(item, yeni_yol)
    
    kaynak_bul(veri, yol)
    return bulunan_kaynaklar

def kaynak_kaldir_gelismis(json_dosyasi, yedek_al=True, rapor_goster=True):
    """
    Gelişmiş kaynak kaldırma işlemi
    """
    try:
        # JSON dosyasını oku
        with open(json_dosyasi, 'r', encoding='utf-8') as f:
            orijinal_veri = json.load(f)
        
        # Yedek al
        if yedek_al:
            yedek_yolu = yedek_olustur(json_dosyasi)
            if rapor_goster:
                print(f"  Yedek oluşturuldu: {yedek_yolu}")
        
        # Kaynak analizi
        if rapor_goster:
            kaynaklar = kaynak_analiz_et(orijinal_veri)
            if kaynaklar:
                print(f"  Bulunan kaynak alanları ({len(kaynaklar)} adet):")
                for kaynak in kaynaklar:
                    print(f"    - {kaynak['yol']}: {kaynak['tip']} = {kaynak['icerik']}")
        
        # Kaynak alanlarını kaldır
        kaynak_alanlari = ['kaynak', 'source', 'kaynaklar', 'sources', 'referans', 'reference']
        
        def kaynak_temizle(obj):
            if isinstance(obj, dict):
                # Dictionary'den kaynak alanlarını kaldır
                temiz_dict = {}
                for key, value in obj.items():
                    if key.lower() not in kaynak_alanlari:
                        temiz_dict[key] = kaynak_temizle(value)
                return temiz_dict
                    
            elif isinstance(obj, list):
                # Liste içindeki her elemanı temizle
                return [kaynak_temizle(item) for item in obj]
            
            return obj
        
        # Veriyi temizle
        temiz_veri = kaynak_temizle(orijinal_veri)
        
        # Temizlenmiş veriyi dosyaya yaz
        with open(json_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(temiz_veri, f, ensure_ascii=False, indent=2)
        
        # Boyut karşılaştırması
        if rapor_goster:
            orijinal_boyut = len(json.dumps(orijinal_veri))
            yeni_boyut = len(json.dumps(temiz_veri))
            print(f"  Boyut: {orijinal_boyut} → {yeni_boyut} byte ({orijinal_boyut - yeni_boyut} byte azaldı)")
        
        return True, len(kaynak_analiz_et(orijinal_veri))
        
    except Exception as e:
        print(f"✗ {json_dosyasi} işlenirken hata: {str(e)}")
        return False, 0

def main():
    """
    Ana fonksiyon
    """
    print("🧹 Gelişmiş JSON Kaynak Temizleyici")
    print("=" * 40)
    
    # Kullanıcı seçenekleri
    print("\nSeçenekler:")
    print("1. Mevcut klasördeki tüm JSON dosyalarını işle")
    print("2. Belirli bir klasörü seç")
    print("3. Tek dosya işle")
    
    secim = input("\nSeçiminiz (1-3): ").strip()
    
    if secim == "1":
        klasor = "."
    elif secim == "2":
        klasor = input("Klasör yolu: ").strip()
        if not os.path.exists(klasor):
            print("❌ Klasör bulunamadı!")
            return
    elif secim == "3":
        dosya = input("JSON dosya yolu: ").strip()
        if not os.path.exists(dosya):
            print("❌ Dosya bulunamadı!")
            return
        json_dosyalari = [dosya]
    else:
        print("❌ Geçersiz seçim!")
        return
    
    if secim != "3":
        # JSON dosyalarını bul
        json_pattern = os.path.join(klasor, "*.json")
        json_dosyalari = glob.glob(json_pattern)
    
    if not json_dosyalari:
        print("❌ JSON dosyası bulunamadı!")
        return
    
    print(f"\n📁 {len(json_dosyalari)} JSON dosyası bulundu:")
    for dosya in json_dosyalari:
        print(f"  📄 {os.path.basename(dosya)}")
    
    # Yedek alma seçeneği
    yedek_al = input("\n💾 Yedek oluşturulsun mu? (E/h): ").strip().lower() in ['e', 'evet', 'yes', 'y']
    
    print(f"\n🔄 İşleme başlanıyor...")
    print("=" * 40)
    
    # Her JSON dosyasını işle
    basarili = 0
    basarisiz = 0
    toplam_kaynak = 0
    
    for dosya in json_dosyalari:
        print(f"\n📝 İşleniyor: {os.path.basename(dosya)}")
        sonuc, kaynak_sayisi = kaynak_kaldir_gelismis(dosya, yedek_al)
        
        if sonuc:
            basarili += 1
            toplam_kaynak += kaynak_sayisi
            print(f"  ✅ Başarılı! ({kaynak_sayisi} kaynak alanı kaldırıldı)")
        else:
            basarisiz += 1
    
    print("\n" + "=" * 40)
    print("📊 İşlem Raporu:")
    print(f"✅ Başarılı: {basarili}")
    print(f"❌ Başarısız: {basarisiz}")
    print(f"🗑️  Toplam kaldırılan kaynak alanı: {toplam_kaynak}")
    
    if yedek_al and basarili > 0:
        print(f"💾 Yedekler 'yedek' klasöründe saklandı")

if __name__ == "__main__":
    main()
