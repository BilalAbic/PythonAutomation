#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Veri Temizleme Modülü
JSON dosyasındaki soru-cevap çiftlerini analiz eder ve kalitesiz verileri temizler.
"""

import json
import re
import os
from typing import List, Dict, Tuple
from collections import Counter

class DataCleaner:
    def __init__(self):
        """Veri temizleyici sınıfını başlatır"""
        self.quality_rules = {
            'min_question_length': 10,
            'min_answer_length': 20,
            'max_question_length': 500,
            'max_answer_length': 2000,
            'min_word_count_question': 3,
            'min_word_count_answer': 5,
            'answer_question_ratio': 1.5  # Cevap en az soru uzunluğunun 1.5 katı olmalı
        }
        
        # Kalitesiz içerik belirteçleri
        self.bad_patterns = [
            r'^\s*$',  # Boş içerik
            r'^\.+$',  # Sadece nokta
            r'^-+$',   # Sadece tire
            r'^\d+$',  # Sadece sayı
            r'^[^\w\s]+$',  # Sadece özel karakter
            r'sayfa \d+',  # Sayfa numarası
            r'bölüm \d+',  # Bölüm numarası
            r'şekil \d+',  # Şekil numarası
            r'tablo \d+',  # Tablo numarası
            r'grafik \d+', # Grafik numarası
            r'resim \d+',  # Resim numarası
        ]
        
        # Geçersiz soru başlangıçları
        self.invalid_question_starts = [
            'bu', 'şu', 'o', 'bunlar', 'şunlar', 'onlar',
            'burada', 'şurada', 'orada', 'yukarıda', 'aşağıda'
        ]
        
        # Sık tekrar eden gereksiz kelimeler
        self.stop_words = [
            'çok', 'daha', 'en', 'bir', 'bu', 'şu', 'o', 've', 'ile', 'için',
            'gibi', 'kadar', 'sonra', 'önce', 'üzere', 'dolayı', 'rağmen'
        ]

    def load_data(self, file_path: str) -> List[Dict]:
        """JSON dosyasından verileri yükler"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {len(data)} soru-cevap çifti yüklendi")
            return data
        except FileNotFoundError:
            print(f"❌ {file_path} dosyası bulunamadı!")
            return []
        except json.JSONDecodeError:
            print(f"❌ {file_path} geçerli bir JSON dosyası değil!")
            return []
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return []

    def check_basic_quality(self, qa_pair: Dict) -> Tuple[bool, List[str]]:
        """Temel kalite kontrolü yapar"""
        issues = []
        
        # Gerekli alanların varlığı
        if 'soru' not in qa_pair or 'cevap' not in qa_pair:
            issues.append("Eksik alan (soru/cevap)")
            return False, issues
        
        question = qa_pair['soru'].strip()
        answer = qa_pair['cevap'].strip()
        
        # Boş içerik kontrolü
        if not question or not answer:
            issues.append("Boş soru veya cevap")
            return False, issues
        
        # Uzunluk kontrolü
        if len(question) < self.quality_rules['min_question_length']:
            issues.append(f"Soru çok kısa ({len(question)} karakter)")
        
        if len(answer) < self.quality_rules['min_answer_length']:
            issues.append(f"Cevap çok kısa ({len(answer)} karakter)")
        
        if len(question) > self.quality_rules['max_question_length']:
            issues.append(f"Soru çok uzun ({len(question)} karakter)")
        
        if len(answer) > self.quality_rules['max_answer_length']:
            issues.append(f"Cevap çok uzun ({len(answer)} karakter)")
        
        # Kelime sayısı kontrolü
        question_words = len(question.split())
        answer_words = len(answer.split())
        
        if question_words < self.quality_rules['min_word_count_question']:
            issues.append(f"Soru çok az kelime ({question_words} kelime)")
        
        if answer_words < self.quality_rules['min_word_count_answer']:
            issues.append(f"Cevap çok az kelime ({answer_words} kelime)")
        
        # Cevap/soru oranı kontrolü
        if len(answer) < len(question) * self.quality_rules['answer_question_ratio']:
            issues.append("Cevap soruya göre çok kısa")
        
        return len(issues) == 0, issues

    def check_content_quality(self, qa_pair: Dict) -> Tuple[bool, List[str]]:
        """İçerik kalitesi kontrolü yapar"""
        issues = []
        question = qa_pair['soru'].strip().lower()
        answer = qa_pair['cevap'].strip().lower()
        
        # Kötü pattern kontrolü
        for pattern in self.bad_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                issues.append(f"Soruda geçersiz pattern: {pattern}")
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(f"Cevapta geçersiz pattern: {pattern}")
        
        # Soru işareti kontrolü
        if '?' not in qa_pair['soru']:
            issues.append("Soruda soru işareti yok")
        
        # Geçersiz soru başlangıcı kontrolü
        first_word = question.split()[0] if question.split() else ""
        if first_word in self.invalid_question_starts:
            issues.append(f"Geçersiz soru başlangıcı: {first_word}")
        
        # Tekrar eden kelime kontrolü
        question_words = question.split()
        answer_words = answer.split()
        
        # Soruda aynı kelimenin çok tekrarı
        question_word_counts = Counter(question_words)
        for word, count in question_word_counts.items():
            if count > 3 and len(word) > 3:
                issues.append(f"Soruda '{word}' kelimesi çok tekrar ediyor ({count} kez)")
        
        # Cevapta aynı kelimenin çok tekrarı
        answer_word_counts = Counter(answer_words)
        for word, count in answer_word_counts.items():
            if count > 5 and len(word) > 3:
                issues.append(f"Cevapta '{word}' kelimesi çok tekrar ediyor ({count} kez)")
        
        return len(issues) == 0, issues

    def check_semantic_quality(self, qa_pair: Dict) -> Tuple[bool, List[str]]:
        """Anlamsal kalite kontrolü yapar"""
        issues = []
        question = qa_pair['soru'].strip().lower()
        answer = qa_pair['cevap'].strip().lower()
        
        # Soru ve cevap arasında anlamsal bağlantı kontrolü
        question_words = set(question.split())
        answer_words = set(answer.split())
        
        # Ortak kelime oranı
        common_words = question_words.intersection(answer_words)
        common_ratio = len(common_words) / len(question_words) if question_words else 0
        
        if common_ratio < 0.1:  # %10'dan az ortak kelime
            issues.append("Soru ve cevap arasında yeterli anlamsal bağlantı yok")
        
        # Cevabın soruyu tekrar etmesi
        if question.replace('?', '').strip() in answer:
            issues.append("Cevap soruyu aynen tekrar ediyor")
        
        # Çok genel cevaplar
        generic_answers = [
            'evet', 'hayır', 'bilmiyorum', 'belki', 'muhtemelen',
            'önemlidir', 'gereklidir', 'faydalıdır', 'zararlıdır'
        ]
        
        if any(generic in answer for generic in generic_answers) and len(answer.split()) < 10:
            issues.append("Çok genel/kısa cevap")
        
        return len(issues) == 0, issues

    def detect_duplicates(self, data: List[Dict]) -> List[int]:
        """Tekrar eden soru-cevap çiftlerini tespit eder"""
        seen_questions = {}
        duplicates = []
        
        for i, qa_pair in enumerate(data):
            question = qa_pair.get('soru', '').strip().lower()
            
            # Benzer soruları tespit et (Levenshtein benzeri basit kontrol)
            for seen_q, seen_idx in seen_questions.items():
                similarity = self.calculate_similarity(question, seen_q)
                if similarity > 0.8:  # %80'den fazla benzerlik
                    duplicates.append(i)
                    break
            else:
                seen_questions[question] = i
        
        return duplicates

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerlik oranını hesaplar"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def clean_data(self, data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Verileri temizler ve istatistikleri döndürür"""
        print("\n🧹 Veri temizleme başlatılıyor...")
        
        original_count = len(data)
        cleaned_data = []
        stats = {
            'original_count': original_count,
            'basic_quality_failed': 0,
            'content_quality_failed': 0,
            'semantic_quality_failed': 0,
            'duplicates_removed': 0,
            'final_count': 0,
            'issues_summary': Counter()
        }
        
        # Temel kalite kontrolü
        print("1️⃣ Temel kalite kontrolü yapılıyor...")
        temp_data = []
        for i, qa_pair in enumerate(data):
            is_valid, issues = self.check_basic_quality(qa_pair)
            if is_valid:
                temp_data.append(qa_pair)
            else:
                stats['basic_quality_failed'] += 1
                for issue in issues:
                    stats['issues_summary'][issue] += 1
        
        print(f"   ✅ {len(temp_data)}/{original_count} çift temel kalite kontrolünü geçti")
        
        # İçerik kalite kontrolü
        print("2️⃣ İçerik kalite kontrolü yapılıyor...")
        temp_data2 = []
        for qa_pair in temp_data:
            is_valid, issues = self.check_content_quality(qa_pair)
            if is_valid:
                temp_data2.append(qa_pair)
            else:
                stats['content_quality_failed'] += 1
                for issue in issues:
                    stats['issues_summary'][issue] += 1
        
        print(f"   ✅ {len(temp_data2)}/{len(temp_data)} çift içerik kalite kontrolünü geçti")
        
        # Anlamsal kalite kontrolü
        print("3️⃣ Anlamsal kalite kontrolü yapılıyor...")
        temp_data3 = []
        for qa_pair in temp_data2:
            is_valid, issues = self.check_semantic_quality(qa_pair)
            if is_valid:
                temp_data3.append(qa_pair)
            else:
                stats['semantic_quality_failed'] += 1
                for issue in issues:
                    stats['issues_summary'][issue] += 1
        
        print(f"   ✅ {len(temp_data3)}/{len(temp_data2)} çift anlamsal kalite kontrolünü geçti")
        
        # Tekrar kontrolü
        print("4️⃣ Tekrar eden veriler tespit ediliyor...")
        duplicates = self.detect_duplicates(temp_data3)
        
        for i, qa_pair in enumerate(temp_data3):
            if i not in duplicates:
                cleaned_data.append(qa_pair)
            else:
                stats['duplicates_removed'] += 1
        
        print(f"   ✅ {len(duplicates)} tekrar eden veri kaldırıldı")
        
        stats['final_count'] = len(cleaned_data)
        
        return cleaned_data, stats

    def save_cleaned_data(self, data: List[Dict], output_file: str):
        """Temizlenmiş verileri kaydeder"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Temizlenmiş veriler '{output_file}' dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Veri kaydetme hatası: {e}")

    def print_statistics(self, stats: Dict):
        """Temizleme istatistiklerini yazdırır"""
        print("\n📊 TEMİZLEME İSTATİSTİKLERİ")
        print("=" * 40)
        print(f"Orijinal veri sayısı: {stats['original_count']}")
        print(f"Temel kalite hatası: {stats['basic_quality_failed']}")
        print(f"İçerik kalite hatası: {stats['content_quality_failed']}")
        print(f"Anlamsal kalite hatası: {stats['semantic_quality_failed']}")
        print(f"Tekrar eden veriler: {stats['duplicates_removed']}")
        print(f"Final veri sayısı: {stats['final_count']}")
        
        success_rate = (stats['final_count'] / stats['original_count']) * 100 if stats['original_count'] > 0 else 0
        print(f"Başarı oranı: {success_rate:.1f}%")
        
        if stats['issues_summary']:
            print("\n🔍 EN SIK KARŞILAŞILAN SORUNLAR:")
            for issue, count in stats['issues_summary'].most_common(10):
                print(f"  • {issue}: {count} kez")

def main():
    """Ana fonksiyon"""
    print("🧹 Veri Temizleme Aracı")
    print("=" * 30)
    
    # Dosya kontrolü
    input_file = "iki_kaynak_birlesimi.json"
    if not os.path.exists(input_file):
        print(f"❌ {input_file} dosyası bulunamadı!")
        print("Önce soru-cevap üretimi yapmalısınız.")
        return
    
    # Temizleyiciyi başlat
    cleaner = DataCleaner()
    
    # Verileri yükle
    data = cleaner.load_data(input_file)
    if not data:
        return
    
    # Verileri temizle
    cleaned_data, stats = cleaner.clean_data(data)
    
    # İstatistikleri göster
    cleaner.print_statistics(stats)
    
    # Temizlenmiş verileri kaydet
    if cleaned_data:
        output_file = "cleaned_qa_pairs.json"
        cleaner.save_cleaned_data(cleaned_data, output_file)
        
        # Yedek dosya oluştur
        backup_file = "backup_" + input_file
        if not os.path.exists(backup_file):
            import shutil
            shutil.copy2(input_file, backup_file)
            print(f"📋 Orijinal veriler '{backup_file}' olarak yedeklendi")
        
        print(f"\n🎉 Veri temizleme tamamlandı!")
        print(f"📄 Temizlenmiş veriler: {output_file}")
        print(f"📋 Yedek dosya: {backup_file}")
    else:
        print("\n❌ Temizleme sonrası hiç veri kalmadı!")

if __name__ == "__main__":
    main() 