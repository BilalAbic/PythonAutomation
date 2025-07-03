#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Quality Analyzer for ML Training
ML modeli eğitimi için üretilen veri setinin kalitesini analiz eder
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
import re
from datetime import datetime
import logging
import os

# Turkish language setup
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")

class MLDataQualityAnalyzer:
    """ML eğitimi için veri kalitesi analiz sistemi"""
    
    def __init__(self, data_file: str = "output_json/toplam_egitim_veriseti.jsonl"):
        self.data_file = Path(data_file)
        self.data = []
        self.df = None
        self.analysis_results = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """JSONL formatındaki veriyi yükle"""
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(f"Veri dosyası bulunamadı: {self.data_file}")
                
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data_point = json.loads(line.strip())
                        if data_point:  # Boş satırları atla
                            self.data.append(data_point)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Line {line_num} JSON hatası: {e}")
                        
            if not self.data:
                raise ValueError("Hiç veri yüklenemedi!")
                
            # DataFrame'e çevir
            self.df = pd.DataFrame(self.data)
            
            self.logger.info(f"✅ {len(self.data)} veri noktası yüklendi")
            
        except Exception as e:
            self.logger.error(f"Veri yüklenirken hata: {e}")
            raise
            
    def analyze_basic_statistics(self) -> Dict[str, Any]:
        """Temel istatistikler"""
        stats = {
            'total_records': len(self.df),
            'unique_sources': self.df['kaynak_dosya'].nunique() if 'kaynak_dosya' in self.df else 0,
            'date_range': {
                'earliest': self.df['uretim_tarihi'].min() if 'uretim_tarihi' in self.df else None,
                'latest': self.df['uretim_tarihi'].max() if 'uretim_tarihi' in self.df else None
            }
        }
        
        # Question ve answer length statistics
        if 'soru' in self.df.columns:
            stats['question_length'] = {
                'mean': self.df['soru'].str.len().mean(),
                'median': self.df['soru'].str.len().median(),
                'min': self.df['soru'].str.len().min(),
                'max': self.df['soru'].str.len().max(),
                'std': self.df['soru'].str.len().std()
            }
        
        if 'cevap' in self.df.columns:
            stats['answer_length'] = {
                'mean': self.df['cevap'].str.len().mean(),
                'median': self.df['cevap'].str.len().median(),
                'min': self.df['cevap'].str.len().min(),
                'max': self.df['cevap'].str.len().max(),
                'std': self.df['cevap'].str.len().std()
            }
            
        # Word count statistics
        if 'kelime_sayisi' in self.df.columns:
            stats['word_count'] = {
                'mean': self.df['kelime_sayisi'].mean(),
                'median': self.df['kelime_sayisi'].median(),
                'min': self.df['kelime_sayisi'].min(),
                'max': self.df['kelime_sayisi'].max(),
                'std': self.df['kelime_sayisi'].std()
            }
            
        # Quality score statistics
        if 'kalite_skoru' in self.df.columns:
            stats['quality_score'] = {
                'mean': self.df['kalite_skoru'].mean(),
                'median': self.df['kalite_skoru'].median(),
                'min': self.df['kalite_skoru'].min(),
                'max': self.df['kalite_skoru'].max(),
                'std': self.df['kalite_skoru'].std()
            }
        
        return stats
        
    def calculate_ml_readiness_score(self) -> Dict[str, Any]:
        """ML eğitimi için hazırlık skoru hesapla"""
        
        score_components = {}
        total_score = 0
        max_score = 100
        
        # 1. Data volume (20 points)
        data_count = len(self.df)
        if data_count >= 1000:
            volume_score = 20
        elif data_count >= 500:
            volume_score = 15
        elif data_count >= 100:
            volume_score = 10
        else:
            volume_score = 5
            
        score_components['data_volume'] = volume_score
        total_score += volume_score
        
        # 2. Category distribution (20 points)
        if 'kategori' in self.df.columns:
            categories = self.df['kategori'].value_counts()
            if len(categories) >= 5:
                category_score = 20
            elif len(categories) >= 3:
                category_score = 15
            else:
                category_score = 10
        else:
            category_score = 0
            
        score_components['category_diversity'] = category_score
        total_score += category_score
        
        # 3. Quality score (25 points)
        if 'kalite_skoru' in self.df.columns:
            avg_quality = self.df['kalite_skoru'].mean()
            if avg_quality >= 85:
                quality_score = 25
            elif avg_quality >= 75:
                quality_score = 20
            elif avg_quality >= 65:
                quality_score = 15
            else:
                quality_score = 10
        else:
            quality_score = 0
            
        score_components['average_quality'] = quality_score
        total_score += quality_score
        
        # 4. Length distribution (15 points)
        if 'kelime_sayisi' in self.df.columns:
            word_counts = self.df['kelime_sayisi']
            ideal_range = ((word_counts >= 50) & (word_counts <= 200)).sum()
            length_score = min(15, (ideal_range / len(self.df)) * 15)
        else:
            length_score = 0
            
        score_components['length_distribution'] = length_score
        total_score += length_score
        
        # Overall assessment
        if total_score >= 90:
            readiness_level = "Excellent - Ready for production ML training"
        elif total_score >= 75:
            readiness_level = "Good - Ready for ML training with minor improvements"
        elif total_score >= 60:
            readiness_level = "Fair - Needs improvements before ML training"
        elif total_score >= 40:
            readiness_level = "Poor - Significant improvements required"
        else:
            readiness_level = "Very Poor - Major overhaul needed"
            
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score) * 100,
            'score_components': score_components,
            'readiness_level': readiness_level
        }
        
    def run_full_analysis(self) -> Dict[str, Any]:
        """Tam analiz çalıştır"""
        self.logger.info("🔍 Veri kalitesi analizi başlatılıyor...")
        
        results = {}
        
        # Basic statistics
        results['basic_statistics'] = self.analyze_basic_statistics()
        
        # ML readiness
        results['ml_readiness'] = self.calculate_ml_readiness_score()
        
        # Save full report
        self.save_analysis_report(results)
        
        self.analysis_results = results
        return results
        
    def save_analysis_report(self, results: Dict[str, Any]):
        """Analiz raporunu kaydet"""
        os.makedirs('output', exist_ok=True)
        
        # JSON report
        with open('output/data_quality_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
        # Human-readable report
        with open('output/data_quality_report.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Basic stats
            stats = results['basic_statistics']
            f.write(f"📊 TEMEL İSTATİSTİKLER\n")
            f.write(f"Toplam kayıt sayısı: {stats['total_records']}\n")
            f.write(f"Benzersiz kaynak sayısı: {stats['unique_sources']}\n")
            
            if 'question_length' in stats:
                f.write(f"Ortalama soru uzunluğu: {stats['question_length']['mean']:.1f} karakter\n")
            if 'answer_length' in stats:
                f.write(f"Ortalama cevap uzunluğu: {stats['answer_length']['mean']:.1f} karakter\n")
            if 'quality_score' in stats:
                f.write(f"Ortalama kalite skoru: {stats['quality_score']['mean']:.1f}\n")
                
            # ML Readiness
            ml_readiness = results['ml_readiness']
            f.write(f"\n🤖 ML EĞİTİMİ HAZIRLIK DURUMU\n")
            f.write(f"Toplam skor: {ml_readiness['total_score']}/{ml_readiness['max_score']} ({ml_readiness['percentage']:.1f}%)\n")
            f.write(f"Değerlendirme: {ml_readiness['readiness_level']}\n\n")
            
        self.logger.info("📄 Analiz raporu output/ klasörüne kaydedildi")
        
    def print_summary(self):
        """Özet raporu yazdır"""
        if not self.analysis_results:
            self.logger.warning("Önce analiz çalıştırın!")
            return
            
        results = self.analysis_results
        ml_readiness = results['ml_readiness']
        
        print("\n" + "="*80)
        print("🎯 VERİ KALİTESİ ANALİZ ÖZETİ")
        print("="*80)
        
        print(f"📊 Toplam veri: {results['basic_statistics']['total_records']} kayıt")
        print(f"⭐ ML Hazırlık Skoru: {ml_readiness['total_score']}/100 ({ml_readiness['percentage']:.1f}%)")
        print(f"🏆 Değerlendirme: {ml_readiness['readiness_level']}")
        
        if 'quality_score' in results['basic_statistics']:
            print(f"📈 Ortalama kalite: {results['basic_statistics']['quality_score']['mean']:.1f}")
            
        print(f"\n📁 Detaylı rapor: output/data_quality_report.txt")
        print("="*80)

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ML eğitimi için veri kalitesi analizi")
    parser.add_argument('--data-file', default='output_json/toplam_egitim_veriseti.jsonl', 
                       help='Analiz edilecek JSONL dosyası')
    
    args = parser.parse_args()
    
    try:
        analyzer = MLDataQualityAnalyzer(args.data_file)
        results = analyzer.run_full_analysis()
        analyzer.print_summary()
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        
if __name__ == "__main__":
    main() 