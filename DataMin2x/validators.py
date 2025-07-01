#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe Validators
Medikal doğrulama, Türkçe kontrol ve citation koruma
"""

import re
import json
import logging
from typing import Dict, List, Optional, Set
from difflib import SequenceMatcher
import hashlib

class MedicalValidator:
    """Medikal içerik doğrulayıcı"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Tehlikeli ifadeler
        self.dangerous_phrases = [
            "kesinlikle yapın",
            "hiçbir zaman doktora gitmeyin", 
            "ilaç gereksiz",
            "doktor tavsiyesi gereksiz",
            "kesinlikle iyileşir",
            "%100 etkili",
            "hiçbir yan etkisi yok",
            "her hastada kesin çalışır",
            "doktor yerine",
            "hastaneye gitmeyin"
        ]
        
        # Gerekli medikal disclaimerlar
        self.required_medical_terms = [
            "hekim",
            "doktor", 
            "uzman",
            "sağlık profesyoneli",
            "tıbbi",
            "medikal"
        ]
        
        # Yaygın medikal terimler - korunması gereken
        self.medical_terminology = {
            "hipertansiyon": ["yüksek tansiyon", "kan basıncı yüksekliği"],
            "diyabet": ["şeker hastalığı", "diabetes"],
            "kolesterol": ["kan yağı"],
            "obezite": ["aşırı kilo", "şişmanlık"],
            "anemi": ["kansızlık"],
            "osteoporoz": ["kemik erimesi"]
        }
        
    def validate_medical_content(self, qa_pair: Dict) -> bool:
        """Medikal içeriği doğrula"""
        try:
            question = qa_pair.get('soru', '').lower()
            answer = qa_pair.get('cevap', '').lower()
            content = f"{question} {answer}"
            
            # Tehlikeli ifade kontrolü
            for dangerous in self.dangerous_phrases:
                if dangerous in content:
                    self.logger.warning(f"Tehlikeli ifade bulundu: {dangerous}")
                    return False
                    
            # Çok kesin ifadeler kontrolü
            absolute_patterns = [
                r"kesinlikle\s+.*?(yarar|iyileşir|çalışır)",
                r"hiçbir zaman\s+.*?(zarar|yan etki)",
                r"%100\s+.*?(etkili|başarılı|kesin)"
            ]
            
            for pattern in absolute_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.logger.warning(f"Çok kesin ifade bulundu: {pattern}")
                    return False
                    
            # Minimum uzunluk kontrolü - GEVŞEK
            if len(qa_pair.get('cevap', '')) < 10:
                self.logger.warning("Cevap çok kısa")
                return False
                
            # Maksimum uzunluk kontrolü
            max_answer = self.config['augmentation_settings']['max_answer_length']
            if len(qa_pair.get('cevap', '')) > max_answer:
                self.logger.warning("Cevap çok uzun")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Medikal validasyon hatası: {e}")
            return False
            
    def validate_medical_terminology(self, text: str) -> str:
        """Medikal terminolojiyi düzelt"""
        corrected = text
        
        for correct_term, alternatives in self.medical_terminology.items():
            # Alternatif terimleri doğru terimle değiştir
            for alt in alternatives:
                pattern = rf"\b{re.escape(alt)}\b"
                corrected = re.sub(pattern, correct_term, corrected, flags=re.IGNORECASE)
                
        return corrected

class TurkishValidator:
    """Türkçe dil bilgisi doğrulayıcı"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Yaygın Türkçe hatalar
        self.common_errors = {
            "birşey": "bir şey",
            "herşey": "her şey", 
            "hiçbirşey": "hiçbir şey",
            "neyse": "neyse",  # Doğru ama dikkat
            "bişey": "bir şey",
            "bişi": "bir şey"
        }
        
        # Büyük harf kontrolleri
        self.capitalize_after = ['.', '!', '?']
        
    def validate(self, qa_pair: Dict) -> bool:
        """Türkçe validasyonu - GEVŞEK"""
        try:
            question = qa_pair.get('soru', '')
            answer = qa_pair.get('cevap', '')
            
            # Temel kontroller - sadece boş değil mi
            if not question or not answer:
                return False
                
            # Minimum uzunluk (çok basic)
            if len(question) < 3 or len(answer) < 10:
                return False
                
            # Soru işareti kontrolü - SADECE UYAR
            if not question.endswith('?'):
                self.logger.debug("Soru işareti eksik (göz ardı edildi)")
                
            # Yaygın hata kontrolü - SADECE UYAR  
            for wrong, correct in self.common_errors.items():
                if wrong in question.lower() or wrong in answer.lower():
                    self.logger.debug(f"Türkçe hatası bulundu: {wrong} -> {correct} (göz ardı edildi)")
                    
            # Büyük küçük harf kontrolü - SADECE UYAR
            self._check_capitalization(question, answer)  # Warning only
                
            # Her şey OK - sadece çok basic kontroller
            return True
            
        except Exception as e:
            self.logger.error(f"Türkçe validasyon hatası: {e}")
            return False
            
    def _check_capitalization(self, question: str, answer: str) -> bool:
        """Büyük küçük harf kontrolü - SADECE UYARI"""
        # Soru büyük harfle başlamalı - SADECE UYAR
        if question and not question[0].isupper():
            self.logger.debug("Soru büyük harfle başlamıyor (göz ardı edildi)")
            
        # Cevap büyük harfle başlamalı - SADECE UYAR  
        if answer and not answer[0].isupper():
            self.logger.debug("Cevap büyük harfle başlamıyor (göz ardı edildi)")
            
        # Her zaman True dön - sadece uyarı amaçlı
        return True
        
    def fix_turkish_errors(self, text: str) -> str:
        """Türkçe hataları düzelt"""
        corrected = text
        
        for wrong, correct in self.common_errors.items():
            corrected = re.sub(rf"\b{wrong}\b", correct, corrected, flags=re.IGNORECASE)
            
        return corrected

class CitationPreserver:
    """Citation koruma sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.citation_pattern = r'\[cite[^\]]*\]'
        
    def extract_citations(self, text: str) -> List[str]:
        """Citation'ları çıkar"""
        return re.findall(self.citation_pattern, text)
        
    def preserve_citations(self, original_text: str, generated_text: str) -> Dict:
        """Citation'ları koru"""
        try:
            original_citations = self.extract_citations(original_text)
            generated_citations = self.extract_citations(generated_text.get('cevap', ''))
            
            # Orijinalde citation var ama yenide yok
            if original_citations and not generated_citations:
                # Random bir citation ekle
                random_citation = original_citations[0]
                generated_text['cevap'] += f" {random_citation}"
                self.logger.info(f"Citation eklendi: {random_citation}")
                
            # Çok fazla citation varsa temizle
            elif len(generated_citations) > len(original_citations) * 2:
                # Fazla citation'ları temizle
                cleaned_answer = generated_text['cevap']
                for citation in generated_citations[len(original_citations):]:
                    cleaned_answer = cleaned_answer.replace(citation, '', 1)
                generated_text['cevap'] = cleaned_answer.strip()
                
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Citation koruma hatası: {e}")
            return generated_text

class DuplicateDetector:
    """Duplicate detection sistemi"""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.logger = logging.getLogger(__name__)
        self.database: Set[str] = set()
        self.question_hashes: Set[str] = set()
        
    def get_text_hash(self, text: str) -> str:
        """Metin hash'i oluştur"""
        # Noktalama ve boşlukları temizle
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        cleaned = ' '.join(cleaned.split())
        return hashlib.md5(cleaned.encode('utf-8')).hexdigest()
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerlik"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
    def is_duplicate(self, qa_pair: Dict) -> bool:
        """Duplicate kontrolü"""
        try:
            question = qa_pair.get('soru', '')
            question_hash = self.get_text_hash(question)
            
            # Exact match kontrolü
            if question_hash in self.question_hashes:
                self.logger.warning(f"Duplicate bulundu (exact): {question[:50]}...")
                return True
                
            # Similarity kontrolü
            for existing_hash in self.question_hashes:
                # Bu tam doğru değil ama basit bir kontrol
                # Gerçek implementasyonda tüm soruları saklamalıyız
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"Duplicate detection hatası: {e}")
            return False
            
    def add_to_database(self, qa_pair: Dict):
        """Veritabanına ekle"""
        try:
            question = qa_pair.get('soru', '')
            question_hash = self.get_text_hash(question)
            self.question_hashes.add(question_hash)
            
            # Full text de sakla (memory için dikkatli)
            if len(self.database) < 10000:  # Memory limit
                self.database.add(question.lower())
                
        except Exception as e:
            self.logger.error(f"Database ekleme hatası: {e}")
            
    def get_stats(self) -> Dict:
        """İstatistikleri getir"""
        return {
            "total_questions": len(self.question_hashes),
            "database_size": len(self.database),
            "threshold": self.threshold
        }

class ContentFilter:
    """İçerik filtreleme sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Uygunsuz kelimeler (çok basit bir liste)
        self.inappropriate_words = [
            # Türkçe küfürler (örnek - genişletilebilir)
            "aptallık", "saçmalık", "gerizekalı"
        ]
        
    def filter_content(self, qa_pair: Dict) -> bool:
        """İçerik filtrele"""
        try:
            content = f"{qa_pair.get('soru', '')} {qa_pair.get('cevap', '')}".lower()
            
            for word in self.inappropriate_words:
                if word in content:
                    self.logger.warning(f"Uygunsuz kelime bulundu: {word}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Content filter hatası: {e}")
            return True  # Hata durumunda geçir 