#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Original vs Recovered Data Duplicate Checker
Orijinal veri seti ile kurtarılan backup verilerini karşılaştırır
Duplicate'leri tespit eder ve temiz augmented veri üretir
"""

import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher

class OriginalVsRecoveredChecker:
    """Orijinal ve kurtarılan veri karşılaştırma sınıfı"""
    
    def __init__(self):
        self.stats = {
            'original_count': 0,
            'recovered_count': 0,
            'exact_duplicates': 0,
            'similar_duplicates': 0,
            'unique_augmented': 0,
            'total_checked': 0
        }
        self.similarity_threshold = 0.85  # %85 benzerlik
        
    def log(self, message: str, level: str = "INFO"):
        """Log mesajı"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_qa_hash(self, qa_pair: Dict) -> str:
        """Q&A çifti için exact hash"""
        soru = qa_pair.get('soru', '').strip().lower()
        cevap = qa_pair.get('cevap', '').strip().lower()
        text = f"{soru}|{cevap}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def get_content_fingerprint(self, qa_pair: Dict) -> str:
        """İçerik için daha esnek fingerprint (citation'lar hariç)"""
        soru = qa_pair.get('soru', '').strip().lower()
        cevap = qa_pair.get('cevap', '').strip().lower()
        
        # Citation'ları temizle
        import re
        cevap = re.sub(r'\[cite[:\s]*\d+[,\s\d]*\]', '', cevap)
        cevap = re.sub(r'\[cite_start\]', '', cevap)
        
        # Noktalama ve boşlukları normalize et
        soru = re.sub(r'[^\w\s]', '', soru)
        cevap = re.sub(r'[^\w\s]', '', cevap)
        
        text = f"{soru}|{cevap}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def calculate_similarity(self, qa1: Dict, qa2: Dict) -> float:
        """İki Q&A çifti arasında benzerlik hesapla"""
        soru1 = qa1.get('soru', '').strip().lower()
        cevap1 = qa1.get('cevap', '').strip().lower()
        
        soru2 = qa2.get('soru', '').strip().lower()
        cevap2 = qa2.get('cevap', '').strip().lower()
        
        # Soru benzerliği
        soru_similarity = SequenceMatcher(None, soru1, soru2).ratio()
        
        # Cevap benzerliği (citation'lar hariç)
        import re
        cevap1_clean = re.sub(r'\[cite[:\s]*\d+[,\s\d]*\]', '', cevap1)
        cevap2_clean = re.sub(r'\[cite[:\s]*\d+[,\s\d]*\]', '', cevap2)
        
        cevap_similarity = SequenceMatcher(None, cevap1_clean, cevap2_clean).ratio()
        
        # Ağırlıklı ortalama (soru %40, cevap %60)
        overall_similarity = (soru_similarity * 0.4) + (cevap_similarity * 0.6)
        
        return overall_similarity
        
    def load_original_data(self, file_path: str) -> List[Dict]:
        """Orijinal veri setini yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Orijinal veri list formatında değil")
                
            self.stats['original_count'] = len(data)
            self.log(f"✅ Orijinal veri yüklendi: {len(data):,} Q&A çifti")
            return data
            
        except Exception as e:
            self.log(f"❌ Orijinal veri yüklenemedi: {e}", "ERROR")
            return []
            
    def load_recovered_data(self, file_path: str) -> List[Dict]:
        """Kurtarılan veriyi yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Kurtarılan veri list formatında değil")
                
            self.stats['recovered_count'] = len(data)
            self.log(f"✅ Kurtarılan veri yüklendi: {len(data):,} Q&A çifti")
            return data
            
        except Exception as e:
            self.log(f"❌ Kurtarılan veri yüklenemedi: {e}", "ERROR")
            return []
            
    def find_exact_duplicates(self, original_data: List[Dict], recovered_data: List[Dict]) -> Tuple[Set[str], List[Dict]]:
        """Exact duplicate'leri bul"""
        self.log("\n🔍 === EXACT DUPLICATE KONTROLÜ ===")
        
        # Orijinal veri hash'leri
        original_hashes = set()
        for qa in original_data:
            hash_val = self.get_qa_hash(qa)
            original_hashes.add(hash_val)
            
        # Kurtarılan veride exact duplicate'leri bul
        exact_duplicates = set()
        clean_recovered = []
        
        for qa in recovered_data:
            hash_val = self.get_qa_hash(qa)
            if hash_val in original_hashes:
                exact_duplicates.add(hash_val)
            else:
                clean_recovered.append(qa)
                
        self.stats['exact_duplicates'] = len(exact_duplicates)
        self.log(f"🔄 Exact duplicate: {len(exact_duplicates):,} adet")
        self.log(f"✅ Temiz kalan: {len(clean_recovered):,} adet")
        
        return exact_duplicates, clean_recovered
        
    def find_similar_duplicates(self, original_data: List[Dict], clean_recovered: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Benzer duplicate'leri bul (%85+ benzerlik)"""
        self.log(f"\n🔍 === BENZERLİK KONTROLÜ (%{self.similarity_threshold*100:.0f}+ benzerlik) ===")
        
        similar_pairs = []
        ultra_clean_recovered = []
        
        self.log("📊 Benzerlik analizi yapılıyor...")
        total_comparisons = len(clean_recovered) * len(original_data)
        processed = 0
        
        for i, recovered_qa in enumerate(clean_recovered):
            is_similar = False
            max_similarity = 0
            best_match = None
            
            for original_qa in original_data:
                similarity = self.calculate_similarity(recovered_qa, original_qa)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = original_qa
                    
                if similarity >= self.similarity_threshold:
                    is_similar = True
                    break
                    
            processed += len(original_data)
            if (i + 1) % 1000 == 0:
                progress = (processed / total_comparisons) * 100
                self.log(f"   📈 İlerleme: %{progress:.1f} ({i+1:,}/{len(clean_recovered):,})")
                
            if is_similar:
                similar_pairs.append({
                    'recovered': recovered_qa,
                    'original': best_match,
                    'similarity': max_similarity
                })
            else:
                ultra_clean_recovered.append(recovered_qa)
                
        self.stats['similar_duplicates'] = len(similar_pairs)
        self.stats['unique_augmented'] = len(ultra_clean_recovered)
        
        self.log(f"🔄 Benzer duplicate: {len(similar_pairs):,} adet")
        self.log(f"✅ Benzersiz augmented: {len(ultra_clean_recovered):,} adet")
        
        return similar_pairs, ultra_clean_recovered
        
    def create_detailed_report(self, exact_duplicates: Set[str], similar_pairs: List[Dict], 
                              original_data: List[Dict], recovered_data: List[Dict], 
                              ultra_clean_data: List[Dict]) -> Dict:
        """Detaylı rapor oluştur"""
        
        # Benzerlik dağılımı
        similarity_distribution = {'90-100%': 0, '85-90%': 0}
        for pair in similar_pairs:
            sim = pair['similarity']
            if sim >= 0.9:
                similarity_distribution['90-100%'] += 1
            elif sim >= 0.85:
                similarity_distribution['85-90%'] += 1
                
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "input_summary": {
                "original_data_count": len(original_data),
                "recovered_data_count": len(recovered_data),
                "total_analyzed": len(original_data) + len(recovered_data)
            },
            "duplicate_analysis": {
                "exact_duplicates": len(exact_duplicates),
                "similar_duplicates": len(similar_pairs),
                "similarity_threshold": f"{self.similarity_threshold*100:.0f}%",
                "similarity_distribution": similarity_distribution
            },
            "final_results": {
                "original_data_count": len(original_data),
                "unique_augmented_count": len(ultra_clean_data),
                "total_final_dataset": len(original_data) + len(ultra_clean_data),
                "multiplication_factor": (len(original_data) + len(ultra_clean_data)) / len(original_data)
            },
            "data_quality": {
                "duplicate_removal_rate": f"{((len(exact_duplicates) + len(similar_pairs)) / len(recovered_data) * 100):.1f}%",
                "augmentation_success_rate": f"{(len(ultra_clean_data) / len(recovered_data) * 100):.1f}%"
            },
            "sample_similar_pairs": similar_pairs[:5] if similar_pairs else [],  # İlk 5 örnek
            "recommendations": []
        }
        
        # Öneriler
        if len(exact_duplicates) > 100:
            report["recommendations"].append("⚠️ Çok sayıda exact duplicate - augmentation algoritması kontrol edilmeli")
            
        if len(similar_pairs) > len(ultra_clean_data):
            report["recommendations"].append("⚠️ Benzer duplicate'ler fazla - yaratıcılık artırılmalı")
        else:
            report["recommendations"].append("✅ İyi augmentation kalitesi")
            
        if len(ultra_clean_data) < len(original_data) * 0.5:
            report["recommendations"].append("⚠️ Düşük augmentation verimi - parametreler gözden geçirilmeli")
        else:
            report["recommendations"].append("✅ Başarılı augmentation verimi")
            
        return report
        
    def run_full_analysis(self, original_file: str, recovered_file: str) -> Tuple[List[Dict], List[Dict], Dict]:
        """Tam analiz sürecini çalıştır"""
        self.log("🚀 === DUPLICATE ANALYSIS BAŞLATILDI ===")
        
        # 1. Verileri yükle
        original_data = self.load_original_data(original_file)
        recovered_data = self.load_recovered_data(recovered_file)
        
        if not original_data or not recovered_data:
            self.log("❌ Veri yükleme başarısız!", "ERROR")
            return [], [], {}
            
        # 2. Exact duplicate kontrolü
        exact_duplicates, clean_recovered = self.find_exact_duplicates(original_data, recovered_data)
        
        # 3. Benzerlik kontrolü
        similar_pairs, ultra_clean_recovered = self.find_similar_duplicates(original_data, clean_recovered)
        
        # 4. Final veri seti oluştur
        final_dataset = original_data + ultra_clean_recovered
        
        # 5. Rapor oluştur
        report = self.create_detailed_report(exact_duplicates, similar_pairs, original_data, 
                                           recovered_data, ultra_clean_recovered)
        
        self.log(f"\n🎉 === ANALİZ TAMAMLANDI ===")
        self.log(f"📊 Orijinal: {len(original_data):,}")
        self.log(f"🆕 Benzersiz augmented: {len(ultra_clean_recovered):,}")
        self.log(f"📈 Final toplam: {len(final_dataset):,}")
        self.log(f"🔢 Çarpan: {len(final_dataset) / len(original_data):.2f}x")
        
        return final_dataset, ultra_clean_recovered, report

def main():
    """Ana fonksiyon"""
    print("🔍 Original vs Recovered Duplicate Checker")
    print("=" * 50)
    
    # Dosya yollarını belirle
    original_file = "250630AllData.json"  # Orijinal veri seti
    
    # En yeni recovered dosyasını bul
    import glob
    recovered_files = glob.glob("output/recovered_data_*.json")
    if not recovered_files:
        print("❌ Kurtarılan veri dosyası bulunamadı!")
        print("   Önce backup_recovery_script.py çalıştırın.")
        return
        
    recovered_file = max(recovered_files)  # En yeni dosya
    print(f"📁 Orijinal dosya: {original_file}")
    print(f"📁 Kurtarılan dosya: {recovered_file}")
    
    # Dosya varlığını kontrol et
    if not os.path.exists(original_file):
        print(f"❌ Orijinal dosya bulunamadı: {original_file}")
        return
        
    if not os.path.exists(recovered_file):
        print(f"❌ Kurtarılan dosya bulunamadı: {recovered_file}")
        return
        
    # Analiz yap
    checker = OriginalVsRecoveredChecker()
    final_dataset, clean_augmented, report = checker.run_full_analysis(original_file, recovered_file)
    
    if not final_dataset:
        print("❌ Analiz başarısız!")
        return
        
    # Sonuçları kaydet
    os.makedirs('output', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Final temiz veri seti
    final_file = f'output/final_clean_dataset_{timestamp}.json'
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    print(f"💾 Final temiz veri seti: {final_file}")
    
    # Sadece augmented veriler
    augmented_file = f'output/clean_augmented_only_{timestamp}.json'
    with open(augmented_file, 'w', encoding='utf-8') as f:
        json.dump(clean_augmented, f, ensure_ascii=False, indent=2)
    print(f"💾 Temiz augmented veriler: {augmented_file}")
    
    # Analiz raporu
    report_file = f'output/duplicate_analysis_report_{timestamp}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📋 Duplicate analiz raporu: {report_file}")
    
    # Özet rapor
    print(f"\n📊 === ÖZET RAPOR ===")
    print(f"📥 Orijinal veri: {report['input_summary']['original_data_count']:,}")
    print(f"📦 Kurtarılan veri: {report['input_summary']['recovered_data_count']:,}")
    print(f"🔄 Exact duplicate: {report['duplicate_analysis']['exact_duplicates']:,}")
    print(f"🔄 Benzer duplicate: {report['duplicate_analysis']['similar_duplicates']:,}")
    print(f"✅ Benzersiz augmented: {report['final_results']['unique_augmented_count']:,}")
    print(f"📈 Final toplam: {report['final_results']['total_final_dataset']:,}")
    print(f"🔢 Çarpan: {report['final_results']['multiplication_factor']:.2f}x")
    print(f"📊 Augmentation başarı: {report['data_quality']['augmentation_success_rate']}")
    
    print(f"\n✅ Duplicate temizliği tamamlandı!")

if __name__ == "__main__":
    main() 