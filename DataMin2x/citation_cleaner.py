#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Citation Cleaner Script
Türkçe sağlık verilerindeki tüm [cite: xxx] referanslarını temizler
"""

import json
import re
import os
import glob
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

class CitationCleaner:
    """Citation temizleme sınıfı"""
    
    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'total_qa_pairs': 0,
            'citations_found': 0,
            'citations_removed': 0,
            'citation_patterns': defaultdict(int),
            'avg_citations_per_answer': 0
        }
        
        # Tüm citation pattern'leri
        self.citation_patterns = [
            r'\[cite:\s*\d+(?:,\s*\d+)*\]',  # [cite: 262] veya [cite: 270, 271]
            r'\[cite_start\]',                # [cite_start]
            r'\[cite\s*:\s*\d+\]',           # Boşluklu variant
            r'\[cite\s*\d+\]',               # Kısa format
            r'\[cite[^\]]*\]',               # Genel catch-all
        ]
        
        # Birleşik pattern
        self.combined_pattern = '|'.join(self.citation_patterns)
        
    def log(self, message: str, level: str = "INFO"):
        """Log mesajı"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def analyze_citations(self, text: str) -> List[str]:
        """Metindeki tüm citation'ları tespit et ve analiz et"""
        citations = re.findall(self.combined_pattern, text, re.IGNORECASE)
        
        # Her pattern tipini say
        for citation in citations:
            self.stats['citation_patterns'][citation] += 1
            
        return citations
        
    def clean_citations_from_text(self, text: str) -> Tuple[str, int]:
        """Metinden citation'ları temizle"""
        original_citations = self.analyze_citations(text)
        citation_count = len(original_citations)
        
        # Tüm citation'ları kaldır
        cleaned_text = re.sub(self.combined_pattern, '', text, flags=re.IGNORECASE)
        
        # Fazla boşlukları temizle
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Çoklu boşluklar
        cleaned_text = re.sub(r'\s*\.\s*\.', '.', cleaned_text)  # Çift nokta
        cleaned_text = re.sub(r'\s*,\s*,', ',', cleaned_text)  # Çift virgül
        cleaned_text = re.sub(r'\s+([,.!?])', r'\1', cleaned_text)  # Noktalama öncesi boşluk
        
        # Başlangıç ve bitiş boşluklarını temizle
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text, citation_count
        
    def clean_qa_pair(self, qa_pair: Dict) -> Tuple[Dict, int]:
        """Tek Q&A çiftini temizle"""
        cleaned_qa = qa_pair.copy()
        total_citations = 0
        
        # Soru temizliği
        if 'soru' in cleaned_qa:
            cleaned_soru, soru_citations = self.clean_citations_from_text(cleaned_qa['soru'])
            cleaned_qa['soru'] = cleaned_soru
            total_citations += soru_citations
            
        # Cevap temizliği
        if 'cevap' in cleaned_qa:
            cleaned_cevap, cevap_citations = self.clean_citations_from_text(cleaned_qa['cevap'])
            cleaned_qa['cevap'] = cleaned_cevap
            total_citations += cevap_citations
            
        return cleaned_qa, total_citations
        
    def clean_dataset(self, data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Tüm veri setini temizle"""
        self.log(f"🧹 {len(data):,} Q&A çifti temizleniyor...")
        
        cleaned_data = []
        total_citations_removed = 0
        
        for i, qa_pair in enumerate(data):
            cleaned_qa, citations_count = self.clean_qa_pair(qa_pair)
            cleaned_data.append(cleaned_qa)
            total_citations_removed += citations_count
            
            # İlerleme raporu
            if (i + 1) % 1000 == 0:
                progress = ((i + 1) / len(data)) * 100
                self.log(f"   📈 İlerleme: %{progress:.1f} ({i+1:,}/{len(data):,})")
                
        self.stats['total_qa_pairs'] = len(data)
        self.stats['citations_removed'] = total_citations_removed
        self.stats['avg_citations_per_answer'] = total_citations_removed / len(data) if data else 0
        
        # Cleaning raporu
        cleaning_report = {
            'original_count': len(data),
            'cleaned_count': len(cleaned_data),
            'citations_removed': total_citations_removed,
            'avg_citations_per_qa': round(self.stats['avg_citations_per_answer'], 2),
            'citation_pattern_distribution': dict(self.stats['citation_patterns'])
        }
        
        self.log(f"✅ Temizlik tamamlandı: {total_citations_removed:,} citation kaldırıldı")
        
        return cleaned_data, cleaning_report
        
    def create_sample_comparison(self, original_data: List[Dict], cleaned_data: List[Dict], sample_size: int = 5) -> List[Dict]:
        """Önce/sonra karşılaştırma örnekleri oluştur"""
        samples = []
        
        for i in range(min(sample_size, len(original_data))):
            # Citation'lı bir örnek bul
            original_qa = original_data[i]
            cleaned_qa = cleaned_data[i]
            
            # Citation var mı kontrol et
            citations_in_answer = re.findall(self.combined_pattern, original_qa.get('cevap', ''), re.IGNORECASE)
            
            if citations_in_answer:
                samples.append({
                    'sample_index': i,
                    'original_question': original_qa.get('soru', ''),
                    'original_answer': original_qa.get('cevap', ''),
                    'cleaned_question': cleaned_qa.get('soru', ''),
                    'cleaned_answer': cleaned_qa.get('cevap', ''),
                    'citations_found': citations_in_answer,
                    'citations_count': len(citations_in_answer)
                })
                
        return samples
        
    def validate_cleaning(self, cleaned_data: List[Dict]) -> Dict:
        """Temizlik kalitesini doğrula"""
        validation_report = {
            'remaining_citations': 0,
            'empty_questions': 0,
            'empty_answers': 0,
            'too_short_answers': 0,
            'validation_passed': True,
            'issues': []
        }
        
        for i, qa_pair in enumerate(cleaned_data):
            # Kalan citation kontrolü
            remaining_cites = re.findall(self.combined_pattern, str(qa_pair), re.IGNORECASE)
            if remaining_cites:
                validation_report['remaining_citations'] += len(remaining_cites)
                
            # Boş soru kontrolü
            if not qa_pair.get('soru', '').strip():
                validation_report['empty_questions'] += 1
                
            # Boş cevap kontrolü
            if not qa_pair.get('cevap', '').strip():
                validation_report['empty_answers'] += 1
                
            # Çok kısa cevap kontrolü (10 karakterden az)
            if len(qa_pair.get('cevap', '').strip()) < 10:
                validation_report['too_short_answers'] += 1
                
        # Sorun varsa işaretle
        if validation_report['remaining_citations'] > 0:
            validation_report['issues'].append(f"{validation_report['remaining_citations']} citation kaldırılamadı")
            validation_report['validation_passed'] = False
            
        if validation_report['empty_questions'] > 0:
            validation_report['issues'].append(f"{validation_report['empty_questions']} boş soru")
            validation_report['validation_passed'] = False
            
        if validation_report['empty_answers'] > 0:
            validation_report['issues'].append(f"{validation_report['empty_answers']} boş cevap")
            validation_report['validation_passed'] = False
            
        return validation_report
        
    def process_file(self, input_file: str, output_file: str = None) -> Dict:
        """Tek dosyayı işle"""
        self.log(f"📁 Dosya işleniyor: {input_file}")
        
        # Dosyayı yükle
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Veri list formatında değil")
                
        except Exception as e:
            self.log(f"❌ Dosya yüklenemedi: {e}", "ERROR")
            return {}
            
        # Temizlik yap
        cleaned_data, cleaning_report = self.clean_dataset(data)
        
        # Validasyon yap
        validation_report = self.validate_cleaning(cleaned_data)
        
        # Karşılaştırma örnekleri
        samples = self.create_sample_comparison(data, cleaned_data, 5)
        
        # Output dosya adını belirle
        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            output_file = f"output/{base_name}_cleaned_{timestamp}.json"
            
        # Temizlenmiş veriyi kaydet
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
        # Kapsamlı rapor oluştur
        full_report = {
            "file_info": {
                "input_file": input_file,
                "output_file": output_file,
                "processing_timestamp": datetime.now().isoformat()
            },
            "cleaning_summary": cleaning_report,
            "validation_results": validation_report,
            "sample_comparisons": samples,
            "statistics": {
                "files_processed": 1,
                "processing_success": validation_report['validation_passed']
            }
        }
        
        self.stats['files_processed'] += 1
        
        # Rapor dosyasını kaydet
        report_file = output_file.replace('.json', '_cleaning_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, ensure_ascii=False, indent=2)
            
        self.log(f"💾 Temizlenmiş veri: {output_file}")
        self.log(f"📋 Rapor: {report_file}")
        
        return full_report

def main():
    """Ana fonksiyon"""
    print("🧹 Citation Cleaner Script")
    print("=" * 40)
    
    # Cleaner oluştur
    cleaner = CitationCleaner()
    
    # İşlenecek dosyaları bul
    input_files = []
    
    # Ana veri dosyaları
    main_files = [
        "250630AllData.json",
        "output/recovered_data_*.json",
        "output/final_clean_dataset_*.json"
    ]
    
    for pattern in main_files:
        files = glob.glob(pattern)
        input_files.extend(files)
        
    if not input_files:
        print("❌ İşlenecek dosya bulunamadı!")
        print("   Kontrol edilecek dosyalar:")
        for pattern in main_files:
            print(f"   - {pattern}")
        return
        
    # Mevcut dosyaları listele
    print(f"📁 {len(input_files)} dosya bulundu:")
    for i, file in enumerate(input_files, 1):
        file_size = os.path.getsize(file) / 1024 / 1024  # MB
        print(f"   {i}. {file} ({file_size:.1f} MB)")
        
    # Kullanıcıya seçim yaptır
    while True:
        try:
            choice = input(f"\nHangi dosya(lar) işlensin? (1-{len(input_files)}, 'all' veya 'q' çıkış): ").strip().lower()
            
            if choice == 'q':
                print("❌ İşlem iptal edildi.")
                return
            elif choice == 'all':
                selected_files = input_files
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(input_files):
                    selected_files = [input_files[idx]]
                    break
                else:
                    print(f"⚠️ Geçersiz seçim. 1-{len(input_files)} arası sayı girin.")
            else:
                print("⚠️ Geçersiz giriş. Sayı, 'all' veya 'q' girin.")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ İşlem iptal edildi.")
            return
            
    # Seçilen dosyaları işle
    all_reports = []
    
    for file_path in selected_files:
        print(f"\n" + "="*50)
        report = cleaner.process_file(file_path)
        if report:
            all_reports.append(report)
            
            # Özet göster
            summary = report['cleaning_summary']
            validation = report['validation_results']
            
            print(f"\n📊 === DOSYA ÖZETİ ===")
            print(f"📥 Orijinal: {summary['original_count']:,} Q&A çifti")
            print(f"🧹 Temizlenen: {summary['cleaned_count']:,} Q&A çifti")
            print(f"🔗 Kaldırılan citation: {summary['citations_removed']:,} adet")
            print(f"📈 Ortalama citation/QA: {summary['avg_citations_per_qa']}")
            print(f"✅ Validasyon: {'BAŞARILI' if validation['validation_passed'] else 'SORUNLU'}")
            
            if not validation['validation_passed']:
                print("⚠️ Sorunlar:")
                for issue in validation['issues']:
                    print(f"   - {issue}")
                    
    # Genel özet
    if all_reports:
        total_cleaned = sum(r['cleaning_summary']['cleaned_count'] for r in all_reports)
        total_citations = sum(r['cleaning_summary']['citations_removed'] for r in all_reports)
        
        print(f"\n🎉 === GENEL ÖZET ===")
        print(f"📁 İşlenen dosya: {len(all_reports)}")
        print(f"📦 Toplam temizlenen veri: {total_cleaned:,}")
        print(f"🧹 Toplam kaldırılan citation: {total_citations:,}")
        print(f"💾 Çıktı dosyaları: output/ klasöründe")
        print(f"✅ İşlem tamamlandı!")
    else:
        print("❌ Hiçbir dosya işlenemedi!")

if __name__ == "__main__":
    main() 