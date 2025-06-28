#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Soru-Cevap Verileri Analiz ve Dönüştürme Aracı
Bu script oluşturulan soru-cevap verilerini analiz eder ve farklı formatlara dönüştürür.
"""

import json
import pandas as pd
import os
from collections import Counter
from typing import List, Dict

class QAAnalyzer:
    def __init__(self, qa_file: str):
        self.qa_file = qa_file
        self.qa_data = self.load_qa_data()
    
    def load_qa_data(self) -> List[Dict]:
        """Soru-cevap verilerini yükler"""
        try:
            with open(self.qa_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {len(data)} soru-cevap çifti yüklendi")
            return data
        except FileNotFoundError:
            print(f"❌ {self.qa_file} dosyası bulunamadı!")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {e}")
            return []
    
    def analyze_data(self):
        """Verileri analiz eder"""
        if not self.qa_data:
            print("❌ Analiz edilecek veri bulunamadı!")
            return
        
        print("\n📊 VERİ ANALİZİ")
        print("=" * 30)
        
        # Toplam sayılar
        total_qa = len(self.qa_data)
        print(f"Toplam Soru-Cevap Çifti: {total_qa}")
        
        # Kaynak analizi
        sources = [item.get('kaynak', 'Bilinmeyen') for item in self.qa_data]
        source_counts = Counter(sources)
        
        print(f"\nKaynak Dağılımı:")
        for source, count in source_counts.most_common(10):
            print(f"  {source}: {count} adet")
        
        # Soru uzunluk analizi
        question_lengths = [len(item.get('soru', '').split()) for item in self.qa_data]
        answer_lengths = [len(item.get('cevap', '').split()) for item in self.qa_data]
        
        print(f"\nSoru İstatistikleri:")
        print(f"  Ortalama kelime sayısı: {sum(question_lengths)/len(question_lengths):.1f}")
        print(f"  En kısa soru: {min(question_lengths)} kelime")
        print(f"  En uzun soru: {max(question_lengths)} kelime")
        
        print(f"\nCevap İstatistikleri:")
        print(f"  Ortalama kelime sayısı: {sum(answer_lengths)/len(answer_lengths):.1f}")
        print(f"  En kısa cevap: {min(answer_lengths)} kelime")
        print(f"  En uzun cevap: {max(answer_lengths)} kelime")
    
    def export_to_csv(self, output_file: str = "qa_pairs_export.csv"):
        """CSV formatına dönüştürür"""
        if not self.qa_data:
            print("❌ Dönüştürülecek veri bulunamadı!")
            return
        
        df = pd.DataFrame(self.qa_data)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ CSV dosyası oluşturuldu: {output_file}")
    
    def export_to_training_format(self, output_file: str = "training_data.jsonl"):
        """AI eğitimi için uygun formata dönüştürür"""
        if not self.qa_data:
            print("❌ Dönüştürülecek veri bulunamadı!")
            return
        
        training_data = []
        for item in self.qa_data:
            training_format = {
                "instruction": item.get('soru', ''),
                "input": "",
                "output": item.get('cevap', ''),
                "source": item.get('kaynak', '')
            }
            training_data.append(training_format)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"✅ Eğitim verisi oluşturuldu: {output_file}")
    
    def create_topic_groups(self, output_file: str = "qa_by_topics.json"):
        """Konulara göre gruplandırır"""
        if not self.qa_data:
            print("❌ Gruplandırılacak veri bulunamadı!")
            return
        
        # Kaynaklara göre grupla
        grouped_data = {}
        for item in self.qa_data:
            source = item.get('kaynak', 'Diğer')
            if source not in grouped_data:
                grouped_data[source] = []
            grouped_data[source].append(item)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(grouped_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Konulara göre gruplandırılmış veri: {output_file}")
    
    def filter_quality_data(self, min_answer_length: int = 10, output_file: str = "quality_qa_pairs.json"):
        """Kaliteli verileri filtreler"""
        if not self.qa_data:
            print("❌ Filtrelenecek veri bulunamadı!")
            return
        
        quality_data = []
        for item in self.qa_data:
            question = item.get('soru', '')
            answer = item.get('cevap', '')
            
            # Kalite kriterleri
            if (len(answer.split()) >= min_answer_length and 
                len(question.split()) >= 5 and
                '?' in question and
                len(answer) > len(question)):
                quality_data.append(item)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(quality_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Kaliteli veri filtresi: {len(quality_data)}/{len(self.qa_data)} çift seçildi")
        print(f"   Dosya: {output_file}")
    
    def show_sample_data(self, count: int = 3):
        """Örnek verileri gösterir"""
        if not self.qa_data:
            print("❌ Gösterilecek veri bulunamadı!")
            return
        
        print(f"\n📝 ÖRNEK VERİLER (İlk {count} adet)")
        print("=" * 50)
        
        for i, item in enumerate(self.qa_data[:count]):
            print(f"\n[{i+1}] Kaynak: {item.get('kaynak', 'Bilinmeyen')}")
            print(f"Soru: {item.get('soru', 'Soru bulunamadı')}")
            print(f"Cevap: {item.get('cevap', 'Cevap bulunamadı')[:200]}...")

def main():
    print("📊 Soru-Cevap Verileri Analiz Aracı")
    print("=" * 40)
    
    # Ana dosyayı kontrol et
    qa_file = "pdf_qa_pairs.json"
    if not os.path.exists(qa_file):
        print(f"❌ {qa_file} dosyası bulunamadı!")
        print("Önce PDF'leri işlemek için run_qa_generation.py çalıştırın.")
        return
    
    # Analyzer'ı başlat
    analyzer = QAAnalyzer(qa_file)
    
    if not analyzer.qa_data:
        return
    
    # Analiz yap
    analyzer.analyze_data()
    
    # Örnek verileri göster
    analyzer.show_sample_data()
    
    # Dönüştürme işlemleri
    print("\n🔄 DÖNÜŞTÜRME İŞLEMLERİ")
    print("=" * 30)
    
    analyzer.export_to_csv()
    analyzer.export_to_training_format()
    analyzer.create_topic_groups()
    analyzer.filter_quality_data()
    
    print("\n🎉 Analiz ve dönüştürme işlemleri tamamlandı!")
    print("\nOluşturulan dosyalar:")
    print("  - qa_pairs_export.csv (Excel için)")
    print("  - training_data.jsonl (AI eğitimi için)")
    print("  - qa_by_topics.json (Konulara göre)")
    print("  - quality_qa_pairs.json (Kaliteli veriler)")

if __name__ == "__main__":
    main()
