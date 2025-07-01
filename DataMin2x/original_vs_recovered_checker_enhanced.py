#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Original vs Recovered Data Duplicate Checker
Orijinal veri seti ile kurtarılan backup verilerini karşılaştırır
ENHANCED: Daha detaylı progress raporları ve gerçek zamanlı istatistikler
"""

import json
import hashlib
import os
import time
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher

class EnhancedOriginalVsRecoveredChecker:
    """Gelişmiş orijinal ve kurtarılan veri karşılaştırma sınıfı"""
    
    def __init__(self):
        self.stats = {
            'original_count': 0,
            'recovered_count': 0,
            'exact_duplicates': 0,
            'similar_duplicates': 0,
            'unique_augmented': 0,
            'total_checked': 0,
            'processing_start_time': None,
            'current_max_similarity': 0,
            'current_min_similarity': 1.0,
            'avg_similarity_so_far': 0,
            'similarities_found': []
        }
        self.similarity_threshold = 0.85  # %85 benzerlik
        self.progress_update_frequency = 250  # Her 250 item'da bir update
        self.detailed_update_frequency = 50   # Her 50 item'da bir detaylı update
        
    def log(self, message: str, level: str = "INFO"):
        """Gelişmiş log mesajı"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def log_progress(self, message: str):
        """Progress log mesajı - daha göze çarpan"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔄 [{timestamp}] {message}")
        
    def get_memory_usage(self) -> str:
        """Mevcut bellek kullanımını al"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return f"{memory_mb:.1f}MB"
        
    def calculate_eta(self, processed: int, total: int, start_time: float) -> str:
        """Tahmini kalan süreyi hesapla"""
        if processed == 0:
            return "hesaplanıyor..."
            
        elapsed = time.time() - start_time
        rate = processed / elapsed  # item/saniye
        remaining = total - processed
        eta_seconds = remaining / rate if rate > 0 else 0
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            return f"{eta_seconds/60:.1f}m"
        else:
            return f"{eta_seconds/3600:.1f}h"
            
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
        
    def update_similarity_stats(self, similarity: float):
        """Benzerlik istatistiklerini güncelle"""
        self.stats['similarities_found'].append(similarity)
        
        if similarity > self.stats['current_max_similarity']:
            self.stats['current_max_similarity'] = similarity
            
        if similarity < self.stats['current_min_similarity']:
            self.stats['current_min_similarity'] = similarity
            
        # Ortalama hesapla
        if self.stats['similarities_found']:
            self.stats['avg_similarity_so_far'] = sum(self.stats['similarities_found']) / len(self.stats['similarities_found'])
            
    def print_detailed_progress(self, current: int, total: int, start_time: float, 
                              similar_found: int, high_similarities: List[float]):
        """Detaylı progress raporu"""
        elapsed = time.time() - start_time
        rate = current / elapsed if elapsed > 0 else 0
        eta = self.calculate_eta(current, total, start_time)
        progress_pct = (current / total) * 100
        
        print(f"\n📊 === DETAYLI İLERLEME RAPORU ===")
        print(f"⏱️  Süre: {elapsed:.1f}s | Hız: {rate:.1f} item/s | ETA: {eta}")
        print(f"📈 İlerleme: {current:,}/{total:,} (%{progress_pct:.1f})")
        print(f"🔍 Benzerlik: Maks: %{self.stats['current_max_similarity']*100:.1f} | "
              f"Min: %{self.stats['current_min_similarity']*100:.1f} | "
              f"Ort: %{self.stats['avg_similarity_so_far']*100:.1f}")
        print(f"🔄 Bulunan similar: {similar_found:,} adet")
        print(f"💾 Bellek: {self.get_memory_usage()}")
        
        if high_similarities:
            print(f"🎯 Son yüksek benzerlikler: {[f'%{s*100:.1f}' for s in high_similarities[-3:]]}")
        print(f"{'='*50}")
        
    def load_original_data(self, file_path: str) -> List[Dict]:
        """Orijinal veri setini yükle"""
        try:
            self.log(f"📖 Orijinal veri yükleniyor: {file_path}")
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
            self.log(f"📖 Kurtarılan veri yükleniyor: {file_path}")
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
        self.log_progress("EXACT DUPLICATE KONTROLÜ BAŞLATILIYOR")
        start_time = time.time()
        
        # Orijinal veri hash'leri
        self.log("🔨 Orijinal veri hash'leri oluşturuluyor...")
        original_hashes = set()
        for i, qa in enumerate(original_data):
            hash_val = self.get_qa_hash(qa)
            original_hashes.add(hash_val)
            
            if (i + 1) % 5000 == 0:
                progress = ((i + 1) / len(original_data)) * 100
                self.log(f"   📈 Hash oluşturma: %{progress:.1f} ({i+1:,}/{len(original_data):,})")
                
        # Kurtarılan veride exact duplicate'leri bul
        self.log("🔍 Kurtarılan veride duplicate kontrolü...")
        exact_duplicates = set()
        clean_recovered = []
        
        for i, qa in enumerate(recovered_data):
            hash_val = self.get_qa_hash(qa)
            if hash_val in original_hashes:
                exact_duplicates.add(hash_val)
            else:
                clean_recovered.append(qa)
                
            if (i + 1) % 2000 == 0:
                progress = ((i + 1) / len(recovered_data)) * 100
                elapsed = time.time() - start_time
                eta = self.calculate_eta(i + 1, len(recovered_data), start_time)
                self.log(f"   📈 Duplicate kontrol: %{progress:.1f} | Süre: {elapsed:.1f}s | ETA: {eta}")
                
        elapsed = time.time() - start_time
        self.stats['exact_duplicates'] = len(exact_duplicates)
        
        self.log_progress(f"EXACT DUPLICATE KONTROLÜ TAMAMLANDI ({elapsed:.1f}s)")
        self.log(f"🔄 Exact duplicate: {len(exact_duplicates):,} adet")
        self.log(f"✅ Temiz kalan: {len(clean_recovered):,} adet")
        
        return exact_duplicates, clean_recovered
        
    def find_similar_duplicates(self, original_data: List[Dict], clean_recovered: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Benzer duplicate'leri bul (%85+ benzerlik) - ENHANCED"""
        self.log_progress(f"BENZERLİK ANALİZİ BAŞLATILIYOR (%{self.similarity_threshold*100:.0f}+ benzerlik)")
        
        similar_pairs = []
        ultra_clean_recovered = []
        high_similarities = []  # Yüksek benzerlik skorlarını takip et
        
        total_comparisons = len(clean_recovered) * len(original_data)
        start_time = time.time()
        self.stats['processing_start_time'] = start_time
        
        self.log(f"📊 Toplam karşılaştırma: {total_comparisons:,} işlem")
        self.log(f"🔍 Benzerlik threshold: %{self.similarity_threshold*100:.0f}")
        self.log(f"⚡ Progress raporu: Her {self.detailed_update_frequency} item")
        
        processed_comparisons = 0
        
        for i, recovered_qa in enumerate(clean_recovered):
            is_similar = False
            max_similarity = 0
            best_match = None
            item_start_time = time.time()
            
            for j, original_qa in enumerate(original_data):
                similarity = self.calculate_similarity(recovered_qa, original_qa)
                self.update_similarity_stats(similarity)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = original_qa
                    
                if similarity >= self.similarity_threshold:
                    is_similar = True
                    high_similarities.append(similarity)
                    break
                    
                processed_comparisons += 1
                
                # Her 50 karşılaştırmada bir hız kontrolü
                if j % 50 == 0 and j > 0:
                    item_elapsed = time.time() - item_start_time
                    if item_elapsed > 2:  # 2 saniyeden uzun sürüyorsa uyar
                        comparisons_per_sec = j / item_elapsed
                        self.log(f"   ⏳ Yavaş item #{i+1}: {comparisons_per_sec:.1f} karş./s")
                        
            # İşlem sonucu
            if is_similar:
                similar_pairs.append({
                    'recovered': recovered_qa,
                    'original': best_match,
                    'similarity': max_similarity
                })
            else:
                ultra_clean_recovered.append(recovered_qa)
                
            # Progress raporları
            if (i + 1) % self.detailed_update_frequency == 0:
                self.print_detailed_progress(
                    i + 1, len(clean_recovered), start_time, 
                    len(similar_pairs), high_similarities
                )
                
            elif (i + 1) % self.progress_update_frequency == 0:
                progress = ((i + 1) / len(clean_recovered)) * 100
                elapsed = time.time() - start_time
                eta = self.calculate_eta(i + 1, len(clean_recovered), start_time)
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                
                self.log_progress(f"İlerleme: %{progress:.1f} ({i+1:,}/{len(clean_recovered):,}) | "
                                f"Hız: {rate:.1f} item/s | ETA: {eta} | "
                                f"Similar: {len(similar_pairs):,}")
                
            # Bellek kontrolü (her 1000 item'da bir)
            if (i + 1) % 1000 == 0:
                memory_usage = self.get_memory_usage()
                if float(memory_usage.replace('MB', '')) > 2048:  # 2GB üzeri uyarı
                    self.log(f"⚠️ Yüksek bellek kullanımı: {memory_usage}", "WARNING")
                    
        total_elapsed = time.time() - start_time
        avg_rate = len(clean_recovered) / total_elapsed if total_elapsed > 0 else 0
        
        self.stats['similar_duplicates'] = len(similar_pairs)
        self.stats['unique_augmented'] = len(ultra_clean_recovered)
        
        self.log_progress(f"BENZERLİK ANALİZİ TAMAMLANDI ({total_elapsed:.1f}s)")
        self.log(f"⚡ Ortalama hız: {avg_rate:.1f} item/saniye")
        self.log(f"🔄 Benzer duplicate: {len(similar_pairs):,} adet")
        self.log(f"✅ Benzersiz augmented: {len(ultra_clean_recovered):,} adet")
        self.log(f"🎯 En yüksek benzerlik: %{self.stats['current_max_similarity']*100:.1f}")
        self.log(f"📊 Ortalama benzerlik: %{self.stats['avg_similarity_so_far']*100:.1f}")
        
        return similar_pairs, ultra_clean_recovered
        
    def create_detailed_report(self, exact_duplicates: Set[str], similar_pairs: List[Dict], 
                              original_data: List[Dict], recovered_data: List[Dict], 
                              ultra_clean_data: List[Dict]) -> Dict:
        """Gelişmiş detaylı rapor oluştur"""
        
        total_processing_time = time.time() - self.stats['processing_start_time'] if self.stats['processing_start_time'] else 0
        
        # Benzerlik dağılımı - daha detaylı
        similarity_distribution = {
            '95-100%': 0, '90-95%': 0, '85-90%': 0, 
            '80-85%': 0, '70-80%': 0, '<70%': 0
        }
        
        for pair in similar_pairs:
            sim = pair['similarity']
            if sim >= 0.95:
                similarity_distribution['95-100%'] += 1
            elif sim >= 0.90:
                similarity_distribution['90-95%'] += 1
            elif sim >= 0.85:
                similarity_distribution['85-90%'] += 1
            elif sim >= 0.80:
                similarity_distribution['80-85%'] += 1
            elif sim >= 0.70:
                similarity_distribution['70-80%'] += 1
            else:
                similarity_distribution['<70%'] += 1
                
        # Performance metrikleri
        performance_metrics = {
            "total_processing_time_seconds": round(total_processing_time, 2),
            "average_items_per_second": round(len(recovered_data) / total_processing_time, 2) if total_processing_time > 0 else 0,
            "memory_usage_mb": self.get_memory_usage(),
            "similarity_calculations_performed": len(self.stats['similarities_found']),
            "max_similarity_found": round(self.stats['current_max_similarity'], 4),
            "min_similarity_found": round(self.stats['current_min_similarity'], 4),
            "avg_similarity_overall": round(self.stats['avg_similarity_so_far'], 4)
        }
        
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
                "detailed_similarity_distribution": similarity_distribution
            },
            "final_results": {
                "original_data_count": len(original_data),
                "unique_augmented_count": len(ultra_clean_data),
                "total_final_dataset": len(original_data) + len(ultra_clean_data),
                "multiplication_factor": round((len(original_data) + len(ultra_clean_data)) / len(original_data), 2)
            },
            "data_quality": {
                "duplicate_removal_rate": f"{((len(exact_duplicates) + len(similar_pairs)) / len(recovered_data) * 100):.1f}%",
                "augmentation_success_rate": f"{(len(ultra_clean_data) / len(recovered_data) * 100):.1f}%",
                "data_uniqueness_score": f"{(len(ultra_clean_data) / (len(original_data) + len(ultra_clean_data)) * 100):.1f}%"
            },
            "performance_metrics": performance_metrics,
            "sample_similar_pairs": similar_pairs[:10] if similar_pairs else [],  # İlk 10 örnek
            "recommendations": []
        }
        
        # Gelişmiş öneriler
        exact_ratio = len(exact_duplicates) / len(recovered_data) if recovered_data else 0
        similar_ratio = len(similar_pairs) / len(recovered_data) if recovered_data else 0
        
        if exact_ratio > 0.1:  # %10'dan fazla exact duplicate
            report["recommendations"].append(f"⚠️ Yüksek exact duplicate oranı (%{exact_ratio*100:.1f}) - augmentation algoritması kontrol edilmeli")
            
        if similar_ratio > 0.3:  # %30'dan fazla similar duplicate
            report["recommendations"].append(f"⚠️ Yüksek similar duplicate oranı (%{similar_ratio*100:.1f}) - yaratıcılık parametreleri artırılmalı")
        else:
            report["recommendations"].append("✅ İyi augmentation kalitesi - düşük duplicate oranı")
            
        if len(ultra_clean_data) < len(original_data) * 0.3:  # %30'dan az augmentation
            report["recommendations"].append("⚠️ Düşük augmentation verimi - sistem parametreleri gözden geçirilmeli")
        elif len(ultra_clean_data) > len(original_data) * 1.5:  # %150'den fazla augmentation
            report["recommendations"].append("✅ Mükemmel augmentation verimi - hedefler aşıldı")
        else:
            report["recommendations"].append("✅ Başarılı augmentation verimi")
            
        if performance_metrics["average_items_per_second"] < 1:
            report["recommendations"].append("⚠️ Düşük işlem hızı - algoritma optimizasyonu gerekebilir")
        else:
            report["recommendations"].append("✅ İyi işlem performansı")
            
        return report
        
    def run_full_analysis(self, original_file: str, recovered_file: str) -> Tuple[List[Dict], List[Dict], Dict]:
        """Tam analiz sürecini çalıştır - ENHANCED"""
        self.log_progress("ENHANCED DUPLICATE ANALYSIS BAŞLATILDI")
        overall_start = time.time()
        
        # 1. Verileri yükle
        original_data = self.load_original_data(original_file)
        recovered_data = self.load_recovered_data(recovered_file)
        
        if not original_data or not recovered_data:
            self.log("❌ Veri yükleme başarısız!", "ERROR")
            return [], [], {}
            
        # 2. Exact duplicate kontrolü
        exact_duplicates, clean_recovered = self.find_exact_duplicates(original_data, recovered_data)
        
        # 3. Benzerlik kontrolü (Enhanced)
        similar_pairs, ultra_clean_recovered = self.find_similar_duplicates(original_data, clean_recovered)
        
        # 4. Final veri seti oluştur
        final_dataset = original_data + ultra_clean_recovered
        
        # 5. Gelişmiş rapor oluştur
        report = self.create_detailed_report(exact_duplicates, similar_pairs, original_data, 
                                           recovered_data, ultra_clean_recovered)
        
        total_time = time.time() - overall_start
        
        self.log_progress(f"ENHANCED ANALYSIS TAMAMLANDI ({total_time:.1f}s)")
        self.log(f"📊 Orijinal: {len(original_data):,}")
        self.log(f"🆕 Benzersiz augmented: {len(ultra_clean_recovered):,}")
        self.log(f"📈 Final toplam: {len(final_dataset):,}")
        self.log(f"🔢 Çarpan: {len(final_dataset) / len(original_data):.2f}x")
        self.log(f"⚡ Toplam süre: {total_time:.1f} saniye")
        self.log(f"🎯 Ortalama benzerlik: %{self.stats['avg_similarity_so_far']*100:.1f}")
        
        return final_dataset, ultra_clean_recovered, report

def main():
    """Ana fonksiyon"""
    print("🔍 Enhanced Original vs Recovered Duplicate Checker")
    print("🚀 Gelişmiş progress raporları ve gerçek zamanlı istatistikler")
    print("=" * 60)
    
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
        
    # Enhanced analiz yap
    checker = EnhancedOriginalVsRecoveredChecker()
    final_dataset, clean_augmented, report = checker.run_full_analysis(original_file, recovered_file)
    
    if not final_dataset:
        print("❌ Analiz başarısız!")
        return
        
    # Sonuçları kaydet
    os.makedirs('output', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Final temiz veri seti
    final_file = f'output/enhanced_final_clean_dataset_{timestamp}.json'
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    print(f"💾 Final temiz veri seti: {final_file}")
    
    # Sadece augmented veriler
    augmented_file = f'output/enhanced_clean_augmented_only_{timestamp}.json'
    with open(augmented_file, 'w', encoding='utf-8') as f:
        json.dump(clean_augmented, f, ensure_ascii=False, indent=2)
    print(f"💾 Temiz augmented veriler: {augmented_file}")
    
    # Enhanced analiz raporu
    report_file = f'output/enhanced_duplicate_analysis_report_{timestamp}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📋 Enhanced duplicate analiz raporu: {report_file}")
    
    # Detaylı özet rapor
    print(f"\n📊 === ENHANCED ÖZET RAPOR ===")
    print(f"📥 Orijinal veri: {report['input_summary']['original_data_count']:,}")
    print(f"📦 Kurtarılan veri: {report['input_summary']['recovered_data_count']:,}")
    print(f"🔄 Exact duplicate: {report['duplicate_analysis']['exact_duplicates']:,}")
    print(f"🔄 Benzer duplicate: {report['duplicate_analysis']['similar_duplicates']:,}")
    print(f"✅ Benzersiz augmented: {report['final_results']['unique_augmented_count']:,}")
    print(f"📈 Final toplam: {report['final_results']['total_final_dataset']:,}")
    print(f"🔢 Çarpan: {report['final_results']['multiplication_factor']:.2f}x")
    print(f"📊 Augmentation başarı: {report['data_quality']['augmentation_success_rate']}")
    print(f"⚡ İşlem hızı: {report['performance_metrics']['average_items_per_second']:.1f} item/s")
    print(f"🎯 Maks benzerlik: %{report['performance_metrics']['max_similarity_found']*100:.1f}")
    print(f"📊 Ort benzerlik: %{report['performance_metrics']['avg_similarity_overall']*100:.1f}")
    print(f"💾 Bellek kullanımı: {report['performance_metrics']['memory_usage_mb']}")
    
    print(f"\n✅ Enhanced duplicate temizliği tamamlandı!")

if __name__ == "__main__":
    main() 