#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BASIT VE HIZLI VERİ BİRLEŞTİRME VE KARŞILAŞTIRMA
650 batch'e kadar olan backup'ları al, orijinalle karşılaştır
"""

import json
import glob
from difflib import SequenceMatcher

def load_json(file_path):
    """JSON dosyası yükle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def text_similarity(a, b):
    """İki metin arasındaki benzerlik %"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def quick_merge_and_check():
    """Hızlı birleştirme ve kontrol"""
    print("🚀 HIZLI VERİ BİRLEŞTİRME BAŞLADI")
    
    # 1. Orijinal veriyi yükle
    print("📂 Orijinal veri yükleniyor...")
    original_data = load_json('250630AllData.json')
    print(f"✅ Orijinal: {len(original_data):,} Q&A")
    
    # 2. Backup dosyalarını bul (650'ye kadar)
    backup_files = []
    for i in range(0, 651, 50):  # 0, 50, 100, 150, ... 650
        pattern = f'backups/backup_batch_{i}_*.json'
        files = glob.glob(pattern)
        if files:
            backup_files.extend(files)
    
    backup_files.sort()
    print(f"📁 {len(backup_files)} backup dosyası bulundu")
    
    # 3. Backup'ları birleştir
    print("🔄 Backup'lar birleştiriliyor...")
    all_backup_data = []
    for file_path in backup_files:
        data = load_json(file_path)
        all_backup_data.extend(data)
        print(f"   📄 {file_path}: {len(data):,} veri")
    
    print(f"✅ Toplam backup: {len(all_backup_data):,} Q&A")
    
    # 4. Basit duplicate temizleme (backup içinde)
    print("🧹 Backup içi duplicate temizleme...")
    seen_texts = set()
    clean_backup = []
    
    for qa in all_backup_data:
        qa_text = qa.get('soru', '') + qa.get('cevap', '')
        if qa_text not in seen_texts:
            seen_texts.add(qa_text)
            clean_backup.append(qa)
    
    print(f"✅ Temiz backup: {len(clean_backup):,} Q&A")
    print(f"🗑️ Kaldırılan duplicate: {len(all_backup_data) - len(clean_backup):,}")
    
    # 5. Orijinal ile karşılaştırma
    print("🔍 Orijinal ile benzerlik kontrolü...")
    similar_count = 0
    unique_backup = []
    
    for i, backup_qa in enumerate(clean_backup):
        if i % 1000 == 0:
            print(f"   📊 İlerleme: {i:,}/{len(clean_backup):,}")
        
        is_similar = False
        backup_text = backup_qa.get('soru', '') + ' ' + backup_qa.get('cevap', '')
        
        for orig_qa in original_data:
            orig_text = orig_qa.get('soru', '') + ' ' + orig_qa.get('cevap', '')
            
            if text_similarity(backup_text, orig_text) > 0.85:
                similar_count += 1
                is_similar = True
                break
        
        if not is_similar:
            unique_backup.append(backup_qa)
    
    # 6. Sonuçlar
    print("\n🎯 === SONUÇLAR ===")
    print(f"📊 Orijinal veri: {len(original_data):,}")
    print(f"📊 Backup veri (temiz): {len(clean_backup):,}")
    print(f"🔄 Benzer olanlar: {similar_count:,}")
    print(f"✨ Benzersiz yeni: {len(unique_backup):,}")
    print(f"🎉 TOPLAM: {len(original_data) + len(unique_backup):,}")
    
    # 7. Final birleştirme
    final_dataset = original_data + unique_backup
    
    # 8. Kaydet
    output_file = f'final_merged_dataset_{len(final_dataset)}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Kaydedildi: {output_file}")
    print("✅ TAMAMLANDI!")
    
    return len(original_data), len(unique_backup), len(final_dataset)

if __name__ == "__main__":
    quick_merge_and_check() 