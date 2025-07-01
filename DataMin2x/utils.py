#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe Utilities
JSON parsing, memory management ve yardımcı fonksiyonlar
"""

import json
import re
import gc
import os
import logging
import psutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

class JsonSafeParser:
    """Güvenli JSON parser"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def safe_parse(self, response_text: str) -> Optional[Dict]:
        """Güvenli JSON parse"""
        try:
            # Önce boş veya None kontrolü
            if not response_text or response_text.strip() == "":
                self.logger.warning("Boş response alındı")
                return None
                
            # Standart parse denemesi
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON parse hatası, düzeltmeye çalışılıyor: {e}")
            return self._repair_and_parse(response_text)
            
    def _repair_and_parse(self, text: str) -> Optional[Dict]:
        """JSON'ı tamir et ve parse et"""
        try:
            # Boş kontrolü
            if not text or text.strip() == "":
                return None
                
            # Markdown code blocks temizle
            cleaned = re.sub(r'```json\s*', '', text)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            
            # Baş ve son boşlukları temizle
            cleaned = cleaned.strip()
            
            # Eğer hala boşsa çık
            if not cleaned:
                return None
            
            # JSON dışındaki başlangıç metinlerini temizle
            if not cleaned.startswith('{') and not cleaned.startswith('['):
                # İlk { veya [ karakterini bul
                json_start = max(cleaned.find('{'), cleaned.find('['))
                if json_start > 0:
                    cleaned = cleaned[json_start:]
            
            # JSON dışındaki bitiş metinlerini temizle
            if not cleaned.endswith('}') and not cleaned.endswith(']'):
                # Son } veya ] karakterini bul
                json_end_curly = cleaned.rfind('}')
                json_end_square = cleaned.rfind(']')
                json_end = max(json_end_curly, json_end_square)
                if json_end > 0:
                    cleaned = cleaned[:json_end + 1]
            
            # Tekrar dene
            try:
                return json.loads(cleaned)
            except:
                pass
                
            # Daha agresif temizlik
            cleaned = self._aggressive_json_cleanup(cleaned)
            
            try:
                return json.loads(cleaned)
            except:
                pass
                
            # Son çare: regex ile extraction
            return self._extract_json_with_regex(text)
            
        except Exception as e:
            self.logger.error(f"JSON repair hatası: {e}")
            return None
            
    def _aggressive_json_cleanup(self, text: str) -> str:
        """Agresif JSON temizliği"""
        # Trailing commaları temizle
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        # Çift quotes düzelt
        text = re.sub(r'([^\\])"([^"]*)"([^:])', r'\1"\2"\3', text)
        
        # Control characters temizle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text
        
    def _extract_json_with_regex(self, text: str) -> Optional[Dict]:
        """Regex ile JSON çıkarımı"""
        try:
            # augmented_data array'ini bul
            pattern = r'"augmented_data"\s*:\s*\[(.*?)\]'
            match = re.search(pattern, text, re.DOTALL)
            
            if match:
                # Basit bir array yapısı oluştur
                return {
                    "augmented_data": []  # Boş dön, ana script handle etsin
                }
                
        except Exception as e:
            self.logger.error(f"Regex extraction hatası: {e}")
            
        return None

class MemoryManager:
    """Memory yönetim sistemi"""
    
    def __init__(self, max_memory_percent: float = 85.0):
        self.max_memory_percent = max_memory_percent
        self.logger = logging.getLogger(__name__)
        
    def check_memory_usage(self):
        """Memory kullanımını kontrol et"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > self.max_memory_percent:
                self.logger.warning(f"Memory kullanımı yüksek: %{memory.percent:.1f}")
                self.cleanup_memory()
                
                # Tekrar kontrol
                memory_after = psutil.virtual_memory()
                if memory_after.percent > self.max_memory_percent:
                    raise MemoryError(f"Memory kullanımı hala yüksek: %{memory_after.percent:.1f}")
                    
        except Exception as e:
            self.logger.error(f"Memory check hatası: {e}")
            
    def cleanup_memory(self):
        """Memory temizliği"""
        try:
            # Garbage collection
            collected = gc.collect()
            self.logger.info(f"Garbage collection: {collected} objets cleaned")
            
            # Force GC
            for i in range(3):
                gc.collect()
                
        except Exception as e:
            self.logger.error(f"Memory cleanup hatası: {e}")
            
    def get_memory_info(self) -> Dict:
        """Memory bilgilerini getir"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            }
        except Exception as e:
            self.logger.error(f"Memory info hatası: {e}")
            return {}

class FileManager:
    """Dosya yönetim sistemi"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Dizinleri oluştur
        self.ensure_directories()
        
    def ensure_directories(self):
        """Gerekli dizinleri oluştur"""
        directories = [
            self.config['file_settings']['output_directory'],
            self.config['file_settings']['backup_directory'],
            self.config['file_settings']['checkpoint_directory'],
            self.config['file_settings']['log_directory']
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"Dizin hazırlandı: {directory}")
            
    def safe_write_json(self, data: Any, filepath: str, backup: bool = True):
        """Güvenli JSON yazma"""
        try:
            # Backup oluştur
            if backup and os.path.exists(filepath):
                backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(filepath, backup_path)
                self.logger.debug(f"Backup oluşturuldu: {backup_path}")
                
            # Geçici dosyaya yaz
            temp_path = f"{filepath}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # Geçici dosyayı asıl dosyaya taşı
            os.rename(temp_path, filepath)
            self.logger.debug(f"Dosya güvenli yazıldı: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Safe write hatası: {e}")
            # Geçici dosyayı temizle
            if os.path.exists(f"{filepath}.tmp"):
                os.remove(f"{filepath}.tmp")
            raise
            
    def cleanup_old_files(self, directory: str, days: int = 7):
        """Eski dosyaları temizle"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        self.logger.debug(f"Eski dosya silindi: {filepath}")
                        
        except Exception as e:
            self.logger.error(f"Cleanup hatası: {e}")

class TextProcessor:
    """Metin işleme utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def estimate_tokens(self, text: str) -> int:
        """Token sayısını tahmin et"""
        # Basit tahmin: 4 karakter = 1 token
        return len(text) // 4
        
    def truncate_text(self, text: str, max_length: int) -> str:
        """Metni kırp"""
        if len(text) <= max_length:
            return text
            
        # Kelime sınırında kırp
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # %80'inden fazlaysa kelime sınırında kırp
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."
            
    def clean_text(self, text: str) -> str:
        """Metni temizle"""
        # Çoklu boşlukları tek boşluk yap
        text = re.sub(r'\s+', ' ', text)
        
        # Baş ve son boşlukları temizle
        text = text.strip()
        
        # Çoklu noktalama işaretlerini düzelt
        text = re.sub(r'[.]{2,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text
        
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Anahtar kelimeleri çıkar"""
        # Basit keyword extraction
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Yaygın kelimeleri filtrele
        stop_words = {'için', 'olan', 'olan', 'daha', 'çok', 'gibi', 'kadar', 'sonra'}
        keywords = [w for w in words if w not in stop_words]
        
        # Frequency count
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        # En çok kullanılanları döndür
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word[0] for word in sorted_words[:max_keywords]]

class ProgressTracker:
    """İlerleme takip sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now().isoformat()
        self.progress_data = {
            'total_items': 0,
            'processed_items': 0,
            'current_batch': 0,
            'estimated_completion': None
        }
        
    def update_progress(self, processed: int, total: int, current_batch: int = 0):
        """İlerlemeyi güncelle"""
        self.progress_data.update({
            'total_items': total,
            'processed_items': processed,
            'current_batch': current_batch
        })
        
        # Tahmini bitiş zamanı hesapla
        if processed > 0:
            start_time = datetime.fromisoformat(self.start_time)
            elapsed = datetime.now() - start_time
            rate = processed / elapsed.total_seconds()
            remaining_items = total - processed
            estimated_seconds = remaining_items / rate if rate > 0 else 0
            
            self.progress_data['estimated_completion'] = (
                datetime.now() + timedelta(seconds=estimated_seconds)
            ).isoformat()
            
    def get_progress_percentage(self) -> float:
        """İlerleme yüzdesi"""
        if self.progress_data['total_items'] == 0:
            return 0.0
        return (self.progress_data['processed_items'] / self.progress_data['total_items']) * 100
        
    def get_eta(self) -> str:
        """Tahmini bitiş zamanı"""
        if self.progress_data['estimated_completion']:
            eta = datetime.fromisoformat(self.progress_data['estimated_completion'])
            return eta.strftime('%Y-%m-%d %H:%M:%S')
        return "Hesaplanıyor..."
        
    def get_speed(self) -> str:
        """İşlem hızı"""
        start_time = datetime.fromisoformat(self.start_time)
        elapsed = datetime.now() - start_time
        if elapsed.total_seconds() > 0:
            rate = self.progress_data['processed_items'] / elapsed.total_seconds()
            return f"{rate:.2f} item/saniye"
        return "0 item/saniye"

class ConfigValidator:
    """Config doğrulama sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self, config: Dict) -> bool:
        """Config'i doğrula"""
        try:
            # Zorunlu anahtarlar
            required_keys = [
                'api_keys',
                'safety_settings',
                'quality_controls',
                'monitoring',
                'augmentation_settings',
                'file_settings'
            ]
            
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Config'de eksik anahtar: {key}")
                    
            # API keys kontrolü
            if not config['api_keys'] or len(config['api_keys']) == 0:
                raise ValueError("En az 1 API key gerekli")
                
            # Sayısal değer kontrolleri
            numeric_checks = [
                ('safety_settings.batch_size', 1, 20),
                ('safety_settings.delay_between_requests', 0, 60),
                ('safety_settings.max_retries', 1, 10),
                ('safety_settings.duplicate_threshold', 0.5, 1.0)
            ]
            
            for path, min_val, max_val in numeric_checks:
                value = self._get_nested_value(config, path)
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    raise ValueError(f"Geçersiz değer {path}: {value} (beklenen: {min_val}-{max_val})")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Config validation hatası: {e}")
            return False
            
    def _get_nested_value(self, data: Dict, path: str):
        """Nested dictionary'den değer al"""
        keys = path.split('.')
        value = data
        for key in keys:
            value = value[key]
        return value 