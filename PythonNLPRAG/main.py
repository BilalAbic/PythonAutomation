#!/usr/bin/env python3
"""
Production-ready PDF to Q&A Dataset Generator
Automates the creation of Question-Answer datasets from PDF files using Gemini API
Enhanced with multi-machine support, adaptive rate limiting, and robust API key management
"""

import argparse
import io
import json
import logging
import os
import random
import sys
import threading
import time
import gc
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import traceback

import fitz  # PyMuPDF
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from PIL import Image

# Enhanced imports (DataMin2x style)
try:
    from pdf_api_manager import APIKeyManager
except ImportError:
    APIKeyManager = None  # Fallback to original implementation


class PDFToQAGenerator:
    """Main class for generating Q&A datasets from PDF files."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the enhanced PDF generator with ultra-safe features."""
        print("🛡️ Ultra Safe PDF Processor başlatılıyor...")
        
        # Setup basic logging first
        self._setup_basic_logging()
        
        # Config yükle ve doğrula
        self.config = self._load_config(config_path)
        
        # Setup enhanced logging with config
        self._setup_logging()
        self._setup_output_directory()
        
        # Enhanced safety settings
        self.setup_safety_systems()
        
        # API key management - Enhanced version
        # Always initialize these attributes for compatibility
        self._current_api_key_index = 0
        self._api_key_lock = threading.Lock()
        
        if APIKeyManager:
            self.api_manager = APIKeyManager(self.config['api_keys'], self.logger)
            active_count = self.api_manager.test_all_keys()
            if active_count == 0:
                raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            self.logger.info(f"✅ {active_count}/{len(self.config['api_keys'])} API key aktif")
        else:
            # Fallback to original implementation
            self._configure_gemini()
        
        # Enhanced timing and rate limiting
        self._api_call_times = []
        self._last_api_call_time = 0
        self._current_delay = self._get_config_value('safety_settings.min_delay_between_calls', 3)
        
        # Multi-machine support
        multi_config = self.config.get('multi_machine', {})
        self.machine_id = multi_config.get('machine_id', 0)
        self.total_machines = multi_config.get('total_machines', 1)
        
        # Track processed files for resume functionality
        self.processed_files = self._get_already_processed_files()
        
        # Enhanced stats
        self.stats = {
            'total_pdfs_processed': 0,
            'total_questions_generated': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'api_failures': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Config hot reload support
        self.config_file_path = config_path
        self.config_last_modified = os.path.getmtime(config_path)
        
        self.logger.info(f"🛡️ Ultra Safe PDF Processor hazır!")
        self.logger.info(f"📁 Configuration: {config_path}")
        self.logger.info(f"🤖 Machine ID: {self.machine_id}/{self.total_machines}")
        self.logger.info(f"📄 Processed files: {len(self.processed_files)}")
        
        if APIKeyManager:
            self.logger.info(f"🔑 Enhanced API management: ACTIVE")
        else:
            self.logger.info(f"🔑 Legacy API management: {len(self.config['api_keys'])} keys")
    
    def setup_safety_systems(self):
        """DataMin2x tarzı güvenlik sistemleri kurulumu"""
        # Emergency stop file
        self.emergency_stop_file = 'EMERGENCY_STOP_PDF'
        if os.path.exists(self.emergency_stop_file):
            os.remove(self.emergency_stop_file)
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Directories
        os.makedirs('checkpoints', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        self.logger.info("🛡️ Güvenlik sistemleri kuruldu")
        
    def _signal_handler(self, signum, frame):
        """Signal handler - graceful shutdown"""
        self.logger.warning(f"Signal {signum} alındı. Güvenli shutdown...")
        self.emergency_shutdown()
        sys.exit(0)
        
    def emergency_shutdown(self):
        """Emergency shutdown"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN!")
        
        # Save emergency data
        emergency_data = {
            "shutdown_time": datetime.now().isoformat(),
            "stats": getattr(self, 'stats', {}),
            "processed_files": list(getattr(self, 'processed_files', set())),
            "reason": "Emergency shutdown"
        }
        
        try:
            with open('emergency_shutdown_pdf.json', 'w', encoding='utf-8') as f:
                json.dump(emergency_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _load_config(self, config_path: str) -> Dict:
        """Enhanced configuration loading with validation."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Enhanced config structure support
            if 'pdf_processing' in config:
                # New enhanced config format
                self._validate_enhanced_config(config)
            else:
                # Legacy config format - convert to new format
                config = self._convert_legacy_config(config)
            
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
            
    def _validate_enhanced_config(self, config: Dict):
        """Enhanced config validation"""
        required_sections = ['api_keys', 'pdf_processing', 'safety_settings']
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
        
        # API keys validation
        if not config['api_keys'] or len(config['api_keys']) == 0:
            raise ValueError("En az 1 API key gerekli")
            
        # PDF processing validation
        pdf_config = config['pdf_processing']
        required_pdf_keys = ['pdf_folder', 'output_folder', 'output_filename']
        for key in required_pdf_keys:
            if key not in pdf_config:
                raise ValueError(f"Missing required PDF config: {key}")
                
    def _convert_legacy_config(self, config: Dict) -> Dict:
        """Legacy config'i yeni formata çevir"""
        # Validate legacy required keys
        required_keys = ['api_keys', 'pdf_folder', 'output_folder', 'output_filename']
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Convert to new format
        enhanced_config = {
            'api_keys': config['api_keys'],
            'safety_settings': {
                'max_retries': config.get('max_retries_per_key', 3),
                'min_delay_between_calls': config.get('min_delay_between_calls', 3),
                'max_delay_between_calls': config.get('max_delay_between_calls', 15),
                'adaptive_delay': config.get('adaptive_delay', True),
                'max_fails_per_hour': 20,
                'emergency_shutdown_threshold': 50,
                'memory_usage_threshold': 85,
                'auto_checkpoint_frequency': 10
            },
            'pdf_processing': {
                'model_name': config.get('model_name', 'gemini-1.5-flash-latest'),
                'pdf_folder': config['pdf_folder'],
                'output_folder': config['output_folder'],
                'output_filename': config['output_filename'],
                'max_questions_per_pdf': config.get('max_questions_per_pdf', 15),
                'extract_images': False,
                'min_content_length': 100,
                'timeout_seconds': config.get('api_timeout_seconds', 600)
            },
            'quality_controls': {
                'validate_turkish': True,
                'min_question_length': 10,
                'min_answer_length': 20,
                'content_filtering': True,
                'duplicate_detection': False,
                'confidence_threshold': 0.8
            },
            'monitoring': {
                'log_filename': config.get('log_filename', 'data_generator.log'),
                'enable_progress_reports': True,
                'enable_performance_monitoring': True,
                'enable_cost_tracking': True,
                'detailed_logging': True
            },
            'multi_machine': {
                'machine_id': config.get('machine_id', 0),
                'total_machines': config.get('total_machines', 1),
                'enable_distributed_processing': False
            },
            'file_settings': {
                'output_directory': 'output',
                'checkpoint_directory': 'checkpoints', 
                'log_directory': 'logs',
                'backup_directory': 'backups'
            }
        }
        
        self.logger.info("📄 Legacy config converted to enhanced format")
        return enhanced_config
    
    def _get_config_value(self, key_path: str, default=None):
        """Helper method to safely get config values from enhanced format."""
        # Handle nested keys like 'pdf_processing.output_folder'
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def _setup_basic_logging(self):
        """Setup basic logging for initialization phase."""
        self.logger = logging.getLogger('UltraSafePDFProcessor')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Basic console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_logging(self):
        """Enhanced logging setup with better organization."""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Clear existing handlers (basic logging)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Logger already exists from basic setup
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler - enhanced path
        log_filename = self._get_config_value('monitoring.log_filename', 'data_generator.log')
        if not log_filename.startswith('logs/'):
            log_filename = f"logs/{log_filename}"
            
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Also create a timestamped log file for this session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        timestamped_handler = logging.FileHandler(
            f"logs/pdf_processor_{timestamp}.log", 
            encoding='utf-8'
        )
        timestamped_handler.setLevel(logging.DEBUG)
        timestamped_handler.setFormatter(formatter)
        self.logger.addHandler(timestamped_handler)
    
    def _setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        output_dir = Path(self._get_config_value('pdf_processing.output_folder', 'output_json'))
        output_dir.mkdir(exist_ok=True)
        self.logger.info(f"Output directory ready: {output_dir}")
    
    def _configure_gemini(self):
        """Configure Gemini API with the first available key."""
        if not self.config['api_keys']:
            raise ValueError("No API keys provided in configuration")
        
        genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
        self.logger.info(f"Configured Gemini API with key index: {self._current_api_key_index}")
    
    def _get_already_processed_files(self) -> Set[str]:
        """Since we removed source information from output, we'll process all files each time."""
        # Note: Without source information in the output, we cannot track which files were processed
        # This means all files will be reprocessed each time the script runs
        # Consider using a separate tracking file if you need to resume processing
        processed_files = set()
        self.logger.info(f"Resume functionality disabled - no source tracking in output format")
        return processed_files
    
    def _rotate_api_key(self) -> bool:
        """Rotate to the next API key with thread safety. Returns True if successful, False if no more keys."""
        with self._api_key_lock:
            self._current_api_key_index += 1
            
            if self._current_api_key_index >= len(self.config['api_keys']):
                self.logger.error("All API keys exhausted")
                return False
            
            try:
                genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
                self.logger.info(f"Rotated to API key index: {self._current_api_key_index}")
                
                # Add delay after key rotation to avoid immediate rate limiting
                delay = self._get_config_value('safety_settings.api_key_rotation_delay', 5)
                self.logger.info(f"Waiting {delay}s after API key rotation...")
                time.sleep(delay)
                
                return True
            except Exception as e:
                self.logger.error(f"Failed to configure new API key: {e}")
                return False
    
    def _adaptive_rate_limit(self):
        """Implement adaptive rate limiting to avoid API limits."""
        current_time = time.time()
        
        # Clean old call times (keep only last minute)
        self._api_call_times = [t for t in self._api_call_times if current_time - t < 60]
        
        # Check if we're making too many calls
        calls_per_minute = len(self._api_call_times)
        
        if self._get_config_value('safety_settings.adaptive_delay', True):
            # Adaptive delay based on recent call frequency
            if calls_per_minute > 50:  # High frequency
                self._current_delay = min(self._current_delay * 1.5, self._get_config_value('safety_settings.max_delay_between_calls', 15))
            elif calls_per_minute < 20:  # Low frequency
                self._current_delay = max(self._current_delay * 0.8, self._get_config_value('safety_settings.min_delay_between_calls', 3))
        else:
            # Fixed delay
            self._current_delay = self._get_config_value('safety_settings.api_rate_limit_delay', 2)
        
        # Ensure minimum time between calls
        time_since_last_call = current_time - self._last_api_call_time
        if time_since_last_call < self._current_delay:
            sleep_time = self._current_delay - time_since_last_call
            if sleep_time > 0.1:  # Only log significant delays
                self.logger.debug(f"Rate limiting: waiting {sleep_time:.1f}s (current delay: {self._current_delay:.1f}s)")
            time.sleep(sleep_time)
        
        # Record this call
        self._api_call_times.append(time.time())
        self._last_api_call_time = time.time()
    
    def _extract_pdf_content(self, pdf_path: Path) -> Tuple[str, List[bytes]]:
        """Extract text and images from PDF using PyMuPDF."""
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            all_images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                all_text += f"\n--- Sayfa {page_num + 1} ---\n{text}"
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # Check if it's not CMYK
                            img_data = pix.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                        else:
                            # Convert CMYK to RGB first
                            pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix_rgb.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                            pix_rgb = None
                        
                        pix = None
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
                        continue
                
                # Extract tables as images (render page areas with tables)
                # Skip table extraction for pages without proper text layer to reduce noise
                try:
                    # Check if page has text layer (required for table detection)
                    if text.strip():  # Only try table extraction if page has text
                        tables = page.find_tables()
                        if tables:  # Only process if tables are found
                            for table_index, table in enumerate(tables):
                                try:
                                    # Get table bounding box and render as image
                                    bbox = table.bbox
                                    mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                                    pix = page.get_pixmap(matrix=mat, clip=bbox)
                                    img_data = pix.pil_tobytes(format="PNG")
                                    all_images.append(img_data)
                                    pix = None
                                except Exception as e:
                                    # Only log if it's not a common issue
                                    if "not a textpage" not in str(e).lower() and "weakly-referenced" not in str(e).lower():
                                        self.logger.warning(f"Failed to extract table {table_index} from page {page_num + 1}: {e}")
                                    continue
                except Exception as e:
                    # Only log non-common table extraction issues
                    if "not a textpage" not in str(e).lower() and "weakly-referenced" not in str(e).lower():
                        self.logger.warning(f"Failed to extract tables from page {page_num + 1}: {e}")
            
            doc.close()
            self.logger.info(f"Extracted content from {pdf_path.name}: {len(all_text)} chars, {len(all_images)} images")
            return all_text, all_images
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from {pdf_path}: {e}")
            raise
    
    def _create_prompt(self) -> str:
        """Create specialized prompt for dietitian and health chatbot training dataset."""
        prompt = f"""
Sana verilen metin içeriğinden, DİYETİSYEN VE SAĞLIK CHATBOT'U eğitimi için YÜKSEK KALİTELİ soru-cevap çiftleri üret.

🎯 HEDEF: Profesyonel diyetisyen chatbot'u için uzman seviye eğitim verisi

📋 ÇIKTI FORMATI (SADECE BU FORMAT):
[
  {{"soru": "Diyetisyenlik sorusu", "cevap": "Uzman diyetisyen cevabı"}},
  {{"soru": "Beslenme sorusu", "cevap": "Detaylı beslenme cevabı"}}
]

🚫 KESINLIKLE YASAK:
- "makalede", "metinde", "kaynaklarda", "yukarıda", "aşağıda" 
- "belirtildiği gibi", "anlatıldığı üzere", "bahsedildiği"
- "bu", "şu", "bunlar" ile soru başlatma
- Tablo/şekil/grafik referansları

✅ DİYETİSYEN CHATBOT İÇİN MÜKEMMEL SORULAR:

**BESLENME BİLİMİ:**
- "Protein gereksinimini karşılamak için hangi besinler tüketilmeli ve günlük dağılım nasıl olmalı?"
- "Omega-3 yağ asitlerinin vücut üzerindeki etkileri nelerdir ve hangi besinlerde bulunur?"
- "Lif tüketiminin sindirim sistemi üzerindeki faydaları nelerdir ve günlük önerilen miktar nedir?"

**DİYET PLANLAMA:**
- "Kilo vermek isteyen 30 yaşındaki kadın için hangi makro besin dağılımı önerilir?"
- "Diyabetik hastalarda kan şekerini kontrol altında tutmak için hangi beslenme stratejileri uygulanır?"
- "Spor yapan bireyler için antrenman öncesi ve sonrası beslenme nasıl planlanmalı?"

**SAĞLIK KOŞULLARI:**
- "Hipertansiyon hastalarında sodyum kısıtlaması nasıl uygulanır ve alternatif lezzet kaynakları nelerdir?"
- "Çölyak hastalarında glutensiz diyet planlaması yaparken dikkat edilmesi gereken noktalar nelerdir?"
- "Anemi tedavisinde demir emilimini artıran ve azaltan faktörler nelerdir?"

**BESİN DEĞERLERI:**
- "100 gram tavuk göğsünün besin değerleri nelerdir ve hangi vitaminleri içerir?"
- "Karbonhidrat sayımı nasıl yapılır ve diyabetik hastalar için önemi nedir?"
- "Kalsiyum emilimini etkileyen faktörler nelerdir ve günlük ihtiyaç nasıl karşılanır?"

❌ KÖTÜ ÖRNEKLER (YAPMA):
- "Metinde bahsedilen vitaminler nelerdir?"
- "Bu araştırmanın sonuçları nelerdir?"
- "Yukarıdaki tabloda gösterilen besinler nelerdir?"

🎯 SORU KATEGORİLERİ (Diyetisyen odaklı):

1. **BESLENME BİLİMİ** (30%):
   - Makro/mikro besinler, metabolizma
   - "Hangi besinler", "Nasıl çalışır", "Etkisi nedir"
   - Biyokimyasal süreçler ve besin emilimi

2. **DİYET PLANLAMA** (25%):
   - Kişiselleştirilmiş beslenme önerileri
   - "Nasıl planlanır", "Önerilen miktar", "Dağılım"
   - Yaş/cinsiyet/aktivite seviyesine göre planlama

3. **SAĞLIK KOŞULLARI** (25%):
   - Hastalık durumlarında beslenme
   - "Hangi hastalıklarda", "Nasıl etkilenir", "Öneriler"
   - Terapötik beslenme uygulamaları

4. **PRATİK UYGULAMA** (20%):
   - Günlük yaşamda beslenme ipuçları
   - "Nasıl uygulanır", "Alternatifler", "Püf noktalar"
   - Yemek hazırlama ve saklama

📝 DİYETİSYEN CEVAP KALİTESİ:

**MÜKEMMEL CEVAP YAPISI:**
1. **Uzman Tanım** (40-60 kelime)
   "Protein vücudun yapı taşıdır ve günlük gereksinim..."

2. **Bilimsel Açıklama** (80-120 kelime)
   "Amino asitlerden oluşan proteinler, kas yapımı, enzim üretimi..."

3. **Pratik Öneriler** (40-60 kelime)
   "Günde 1.2-1.6 g/kg vücut ağırlığı kadar protein alınmalı..."

4. **Diyetisyen Tavsiyesi** (30-40 kelime)
   "Diyetisyen kontrolünde kişiselleştirilmiş plan önerilir..."

**CEVAP KALİTE STANDARTLARI:**
✅ 180-280 kelime arası (diyetisyen danışmanlığı için optimal)
✅ Bilimsel doğruluk ve güncel beslenme bilimi
✅ Pratik uygulanabilir tavsiyeler
✅ Miktarlar ve önerilerle desteklenmiş
✅ Profesyonel diyetisyen dili
✅ Güvenli ve etik tavsiyeler

❌ Medikal tanı/tedavi önerileri
❌ Spesifik ilaç tavsiyeleri
❌ Kesin sayısal değerler (kişiye özel)
❌ Abartılı iddialar

🔬 DİYETİSYEN BİLİMSEL KALİTE:
- Beslenme terminolojisi doğru kullanımı
- Güncel beslenme kılavuzlarına uygunluk
- Kanıta dayalı beslenme önerileri
- Güvenli beslenme prensipleri

🎯 ADET HEDEF: {self.config.get('pdf_processing', {}).get('questions_per_chunk', 15)} DİYETİSYEN KALİTESİNDE soru-cevap çifti

🚀 DİYETİSYEN CHATBOT KONTROL:
- Her soru diyetisyen pratiğine uygun
- Her cevap profesyonel danışmanlık seviyesi
- Hiçbir referans/belirsizlik yok
- Güvenli ve etik tavsiyeler
- JSON formatına kesinlikle uy

SADECE VE SADECE geçerli JSON array formatında yanıt ver!
"""

        return prompt.strip()
    
    def _clean_and_fix_json(self, json_text: str) -> str:
        """Advanced JSON cleaning and fixing for Gemini API responses"""
        try:
            # Remove any text before first [ and after last ]
            start_idx = json_text.find('[')
            end_idx = json_text.rfind(']')
            
            if start_idx == -1 or end_idx == -1:
                self.logger.warning("No JSON array found in response")
                return "[]"
                
            json_text = json_text[start_idx:end_idx + 1]
            
            # Fix common JSON issues
            fixes_applied = []
            
            # 1. Fix trailing commas
            import re
            original_text = json_text
            json_text = re.sub(r',(\s*[\]}])', r'\1', json_text)
            if json_text != original_text:
                fixes_applied.append("trailing_commas")
            
            # 2. Fix missing commas between objects
            original_text = json_text
            json_text = re.sub(r'}\s*{', '}, {', json_text)
            if json_text != original_text:
                fixes_applied.append("missing_commas")
            
            # 3. Fix unescaped quotes in strings
            def fix_quotes_in_strings(match):
                content = match.group(1)
                # Replace unescaped quotes inside the string
                content = content.replace('"', '\\"')
                return f'"{content}"'
            
            # Find and fix quotes in string values
            original_text = json_text
            json_text = re.sub(r'"([^"]*)"(\s*:\s*)"([^"]*(?:[^"\\]|\\.)*)"', 
                             lambda m: f'"{m.group(1)}": "{m.group(3).replace(chr(34), chr(92)+chr(34))}"', 
                             json_text)
            
            # 4. Fix single quotes to double quotes
            original_text = json_text
            json_text = json_text.replace("'", '"')
            if json_text != original_text:
                fixes_applied.append("single_quotes")
            
            # 5. Remove any non-JSON text at beginning or end
            json_text = json_text.strip()
            
            # 6. Try to fix malformed arrays
            if not json_text.startswith('['):
                json_text = '[' + json_text
                fixes_applied.append("missing_start_bracket")
            if not json_text.endswith(']'):
                json_text = json_text + ']'
                fixes_applied.append("missing_end_bracket")
            
            # 7. Fix incomplete objects at the end
            bracket_count = 0
            brace_count = 0
            fixed_text = ""
            
            for char in json_text:
                fixed_text += char
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            
            # Close any unclosed braces
            while brace_count > 0:
                fixed_text += '}'
                brace_count -= 1
                fixes_applied.append("unclosed_braces")
            
            # Close any unclosed brackets
            while bracket_count > 0:
                fixed_text += ']'
                bracket_count -= 1
                fixes_applied.append("unclosed_brackets")
            
            json_text = fixed_text
            
            # Log applied fixes
            if fixes_applied:
                self.logger.info(f"Applied JSON fixes: {', '.join(fixes_applied)}")
            
            # Final validation attempt
            try:
                json.loads(json_text)
                return json_text
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON still invalid after fixes: {e}")
                
                # Last resort: try to extract valid JSON objects manually
                return self._extract_valid_qa_objects(json_text)
                
        except Exception as e:
            self.logger.error(f"Error in JSON cleaning: {e}")
            return "[]"
    
    def _extract_valid_qa_objects(self, text: str) -> str:
        """Extract valid Q&A objects from malformed JSON as last resort"""
        import re
        
        try:
            # Find all potential Q&A objects using regex
            pattern = r'\{[^{}]*"soru"[^{}]*"cevap"[^{}]*\}'
            matches = re.findall(pattern, text, re.DOTALL)
            
            valid_objects = []
            for match in matches:
                try:
                    # Try to parse each object individually
                    obj = json.loads(match)
                    if 'soru' in obj and 'cevap' in obj:
                        valid_objects.append(obj)
                except:
                    continue
            
            if valid_objects:
                result = json.dumps(valid_objects, ensure_ascii=False)
                self.logger.info(f"Extracted {len(valid_objects)} valid Q&A objects from malformed JSON")
                return result
            else:
                self.logger.warning("Could not extract any valid Q&A objects")
                return "[]"
                
        except Exception as e:
            self.logger.error(f"Error in Q&A extraction: {e}")
            return "[]"
    
    def _validate_qa_pair(self, qa: Dict) -> bool:
        """Specialized validation for dietitian and health chatbot Q&A pairs."""
        if not isinstance(qa, dict):
            return False
        
        if "soru" not in qa or "cevap" not in qa:
            return False
        
        soru = qa["soru"].strip()
        cevap = qa["cevap"].strip()
        
        # Length checks for dietitian consultation quality (RELAXED FOR PROFESSIONAL CONTENT)
        if len(soru) < 20 or len(cevap) < 150:
            self.logger.warning(f"Q&A too short for dietitian quality: Q={len(soru)} chars, A={len(cevap)} chars")
            return False
        
        # INCREASED LIMITS FOR PROFESSIONAL DIETITIAN RESPONSES
        if len(soru) > 400 or len(cevap) > 1500:
            self.logger.warning(f"Q&A too long: Q={len(soru)} chars, A={len(cevap)} chars")
            return False
        
        # Word count validation for dietitian responses (RELAXED)
        soru_words = len(soru.split())
        cevap_words = len(cevap.split())
        
        if soru_words < 8 or soru_words > 50:
            self.logger.warning(f"Question word count out of range: {soru_words} words")
            return False
            
        # INCREASED WORD LIMITS FOR DETAILED DIETITIAN RESPONSES
        if cevap_words < 70 or cevap_words > 400:
            self.logger.warning(f"Answer word count out of range: {cevap_words} words")
            return False
        
        # Forbidden reference words that confuse health chatbots (REDUCED LIST)
        forbidden_words = [
            'makalede', 'metinde', 'kaynaklarda', 'yukarıda', 'aşağıda',
            'belirtildiği gibi', 'anlatıldığı üzere', 'bahsedildiği', 
            'şekilde gösterildiği', 'grafikte', 'resimde',
            'bu makalede', 'bu metinde', 'bu araştırmada', 'yukarıdaki',
            'aşağıdaki', 'gösterilen', 'verilen tabloda'
            # REMOVED: 'şekil', 'tablo', 'tabloda' - these can be legitimate nutrition references
        ]
        
        soru_lower = soru.lower()
        cevap_lower = cevap.lower()
        
        for forbidden in forbidden_words:
            if forbidden in soru_lower or forbidden in cevap_lower:
                self.logger.warning(f"Forbidden reference detected: '{forbidden}' in Q&A pair")
                return False
        
        # Check for vague references at start
        vague_patterns = ['bu', 'şu', 'bunlar', 'şunlar', 'onlar', 'öteki', 'diğer']
        soru_words_list = soru_lower.split()
        
        for i, word in enumerate(soru_words_list[:3]):
            if word in vague_patterns:
                self.logger.warning(f"Vague reference detected: '{word}' at position {i+1}")
                return False
        
        # Dietitian-specific terminology validation
        nutrition_terms = [
            # Macronutrients
            'protein', 'karbonhidrat', 'yağ', 'kalori', 'enerji', 'amino asit',
            'glukoz', 'fruktoz', 'omega', 'doymuş', 'doymamış', 'trans',
            
            # Micronutrients
            'vitamin', 'mineral', 'demir', 'kalsiyum', 'çinko', 'magnezyum',
            'folat', 'b12', 'vitamin d', 'vitamin c', 'beta karoten',
            
            # Health conditions
            'diyabet', 'hipertansiyon', 'kolesterol', 'trigliserit', 'anemi',
            'osteoporoz', 'çölyak', 'gluten', 'laktoz', 'allerji',
            
            # Nutrition concepts
            'metabolizma', 'emilim', 'sindirim', 'diyet', 'beslenme',
            'besin', 'gıda', 'öğün', 'porsiyon', 'indeks', 'lif',
            
            # Body functions
            'kas', 'kemik', 'bağışıklık', 'hormon', 'enzim', 'antioxidant'
        ]
        
        # Check for dietitian terminology in answer (professional quality indicator)
        has_nutrition_terms = any(term in cevap_lower for term in nutrition_terms)
        
        if not has_nutrition_terms:
            self.logger.warning("Answer lacks nutrition/health terminology")
            return False
        
        # Dietitian question quality indicators
        dietitian_question_indicators = [
            # Question starters
            'hangi', 'nasıl', 'neden', 'kaç', 'ne kadar', 'kimler',
            'nelerdir', 'nedir', 'nerelerde', 'ne zaman',
            
            # Nutrition topics
            'beslenme', 'diyet', 'vitamin', 'mineral', 'protein', 'besin',
            'sağlık', 'hastalık', 'kilo', 'enerji', 'metabolizma',
            
            # Professional terms
            'önerilir', 'tavsiye', 'gereksinim', 'ihtiyaç', 'etki',
            'fayda', 'risk', 'kontrol', 'dengeli', 'sağlıklı'
        ]
        
        has_dietitian_question = any(indicator in soru_lower for indicator in dietitian_question_indicators)
        
        if not has_dietitian_question:
            self.logger.warning("Question lacks dietitian consultation indicators")
            return False
        
        # Check for unsafe medical claims (REFINED FOR DIETITIAN SCOPE)
        unsafe_medical_terms = [
            'tanı koy', 'teşhis et', 'tedavi et', 'iyileştir', 'tedavi ol',
            'ilaç ver', 'reçete', 'doz al', 'tablet al'
            # REMOVED: 'tanı', 'mg', 'ml' - these are legitimate nutrition terminology
        ]
        
        for unsafe in unsafe_medical_terms:
            if unsafe in cevap_lower:
                self.logger.warning(f"Unsafe medical claim detected: '{unsafe}'")
                return False
        
        # Check answer structure for dietitian consultation quality (RELAXED)
        sentences = [s.strip() for s in cevap.split('.') if s.strip()]
        if len(sentences) < 3:
            self.logger.warning(f"Answer lacks dietitian consultation depth: only {len(sentences)} sentences")
            return False
        
        # Professional language check (OPTIONAL FOR FLEXIBILITY)
        professional_indicators = [
            'önerilir', 'tavsiye edilir', 'dikkat edilmeli', 'önemlidir',
            'gereklidir', 'faydalıdır', 'etkilidir', 'uygun', 'ideal',
            'kontrol', 'dengelenme', 'planlanma', 'kişiselleştir',
            'mg', 'gram', 'porsiyon', 'günlük', 'haftalık'  # Added nutrition units
        ]
        
        has_professional_language = any(indicator in cevap_lower for indicator in professional_indicators)
        
        if not has_professional_language:
            self.logger.info("Answer could benefit from more professional dietitian language")
            # Changed to INFO instead of WARNING and don't return False
        
        return True
    
    def _call_gemini_api(self, text_content: str, images: List[bytes], max_retries: int = None) -> Optional[List[Dict]]:
        """Call Gemini API with text and images, with enhanced retry logic and API key rotation."""
        if max_retries is None:
            max_retries = self._get_config_value('safety_settings.max_retries', 3) * len(self.config['api_keys'])
        
        prompt = self._create_prompt()
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before each API call
                self._adaptive_rate_limit()
                
                # Initialize model
                model = genai.GenerativeModel(self._get_config_value('pdf_processing.model_name', 'gemini-1.5-flash-latest'))
                
                # Prepare content
                content_parts = [prompt, text_content]
                
                # Add images if available (limit to first 10 for performance)
                image_count = 0
                for img_data in images:
                    if image_count >= 10:  # Limit images to avoid timeout
                        break
                    try:
                        # Convert bytes to PIL Image and then to the format Gemini expects
                        pil_img = Image.open(io.BytesIO(img_data))
                        content_parts.append(pil_img)
                        image_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to process image: {e}")
                        continue
                
                # Generate content with timeout handling
                response = model.generate_content(
                    content_parts,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=8192,
                        temperature=0.1,
                    ),
                    request_options={'timeout': self._get_config_value('pdf_processing.api_timeout_seconds', 600)}
                )
                
                if not response.text:
                    self.logger.warning("Empty response from Gemini API")
                    time.sleep(1)  # Brief pause before retry
                    continue
                
                # Parse JSON response with enhanced error handling
                try:
                    # Clean the response text with advanced JSON fixing
                    response_text = response.text.strip()
                    
                    # Remove markdown code blocks if present
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.startswith('```'):
                        response_text = response_text[3:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    
                    # Advanced JSON cleaning for common Gemini API issues
                    response_text = self._clean_and_fix_json(response_text)
                    
                    qa_pairs = json.loads(response_text)
                    
                    if not isinstance(qa_pairs, list):
                        self.logger.warning("Response is not a JSON array")
                        continue
                    
                    # Validate and clean each Q&A pair
                    valid_qa_pairs = []
                    for qa in qa_pairs:
                        if self._validate_qa_pair(qa):
                            # Simplified output format - only question and answer
                            clean_qa = {
                                "soru": qa.get("soru", "").strip(),
                                "cevap": qa.get("cevap", "").strip()
                            }
                            valid_qa_pairs.append(clean_qa)
                    
                    # Enhanced statistics for ML training
                    if valid_qa_pairs:
                        # Simplified stats calculation
                        total_questions = len(valid_qa_pairs)
                        avg_question_length = sum(len(qa['soru'].split()) for qa in valid_qa_pairs) / total_questions
                        avg_answer_length = sum(len(qa['cevap'].split()) for qa in valid_qa_pairs) / total_questions
                        avg_total_length = avg_question_length + avg_answer_length
                        
                        self.logger.info(f"ML Training Quality Metrics - Questions: {total_questions}, Avg Q Length: {avg_question_length:.1f}, Avg A Length: {avg_answer_length:.1f} words")
                        
                        return valid_qa_pairs
                    else:
                        self.logger.warning("No valid Q&A pairs found after enhanced ML training quality filtering")
                        continue
                
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON response (attempt {attempt + 1}): {e}")
                    self.logger.debug(f"Response text: {response.text[:500]}...")
                    continue
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Enhanced error detection and handling
                if any(keyword in error_msg for keyword in [
                    'permission', 'quota', 'exhausted', 'denied', 'invalid api key', 
                    'rate limit', 'too many requests', '429', 'resource_exhausted'
                ]):
                    self.logger.warning(f"API limit/permission issue detected (attempt {attempt + 1}): {e}")
                    
                    # Add extra delay for rate limiting
                    if 'rate limit' in error_msg or '429' in error_msg or 'too many requests' in error_msg:
                        delay = min(self._current_delay * 2, 30)  # Max 30 seconds
                        self.logger.info(f"🚦 Rate limit detected, waiting {delay}s before retry...")
                        time.sleep(delay)
                    
                    # Try to rotate API key immediately on quota/permission errors
                    if self._rotate_api_key():
                        self.logger.info("🔄 Rotated API key due to quota/permission limits, retrying...")
                        continue
                    else:
                        self.logger.error("❌ All API keys exhausted, cannot continue")
                        return None
                        
                elif 'timeout' in error_msg or 'deadline' in error_msg:
                    self.logger.warning(f"⏱️ Timeout error (attempt {attempt + 1}): {e}")
                    # Increase delay for timeout errors
                    timeout_delay = min(5 * (attempt + 1), 30)
                    self.logger.info(f"⏱️ Waiting {timeout_delay}s for timeout recovery...")
                    time.sleep(timeout_delay)
                    continue
                    
                else:
                    self.logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = min(2 ** attempt + random.uniform(0, 1), 15)
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"All retry attempts failed for API call")
                        return None
        
        return None
    
    def _process_single_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF file and generate Q&A pairs with chunking and proactive key rotation."""
        try:
            self.logger.info(f"Processing: {pdf_path.name}")
            
            # Extract content from PDF
            text_content, images = self._extract_pdf_content(pdf_path)
            
            if not text_content.strip():
                self.logger.warning(f"No text content extracted from {pdf_path.name}")
                return False
            
            # Split text into chunks to avoid overwhelming single API key
            chunk_size = 50000  # characters per chunk
            text_chunks = []
            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                text_chunks.append(chunk)
            
            # Split images proportionally across chunks
            images_per_chunk = max(1, len(images) // len(text_chunks)) if images else 0
            
            self.logger.info(f"Split {pdf_path.name} into {len(text_chunks)} chunks")
            
            all_qa_pairs = []
            
            # Process each chunk with proactive API key rotation
            for chunk_idx, text_chunk in enumerate(text_chunks):
                self.logger.info(f"Processing chunk {chunk_idx + 1}/{len(text_chunks)} of {pdf_path.name}")
                
                # Rotate API key proactively every 2 chunks to distribute load
                if chunk_idx > 0 and chunk_idx % 2 == 0 and len(self.config['api_keys']) > 1:
                    if self._rotate_api_key():
                        self.logger.info(f"Proactively rotated API key for chunk {chunk_idx + 1}")
                
                # Get images for this chunk
                start_img = chunk_idx * images_per_chunk
                end_img = min((chunk_idx + 1) * images_per_chunk, len(images))
                chunk_images = images[start_img:end_img] if images else []
                
                # Generate Q&A pairs for this chunk
                qa_pairs = self._call_gemini_api(text_chunk, chunk_images)
                
                if qa_pairs:
                    all_qa_pairs.extend(qa_pairs)
                    self.logger.info(f"Chunk {chunk_idx + 1}: Generated {len(qa_pairs)} Q&A pairs")
                else:
                    self.logger.warning(f"Failed to generate Q&A pairs for chunk {chunk_idx + 1}")
                
                # Add delay between chunks to respect rate limits
                if chunk_idx < len(text_chunks) - 1:  # Don't delay after last chunk
                    chunk_delay = max(3, self._get_config_value('safety_settings.min_delay_between_calls', 5))
                    self.logger.info(f"Waiting {chunk_delay}s before next chunk...")
                    time.sleep(chunk_delay)
            
            if not all_qa_pairs:
                self.logger.error(f"Failed to generate any Q&A pairs for {pdf_path.name}")
                return False
            
            # Save to output file with enhanced metadata for ML training
            output_file = Path(self.config['pdf_processing']['output_folder']) / self.config['pdf_processing']['output_filename']
            
            with open(output_file, 'a', encoding='utf-8') as f:
                for qa_pair in all_qa_pairs:
                    # Simplified JSONL format - only question and answer
                    output_data = {
                        "soru": qa_pair["soru"],
                        "cevap": qa_pair["cevap"]
                    }
                    f.write(json.dumps(output_data, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Successfully processed {pdf_path.name}: {len(all_qa_pairs)} total Q&A pairs generated from {len(text_chunks)} chunks")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path.name}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _get_pdf_files(self) -> List[Path]:
        """Get list of PDF files to process with multi-machine support."""
        pdf_folder = Path(self._get_config_value('pdf_processing.pdf_folder', 'pdfs'))
        
        if not pdf_folder.exists():
            raise FileNotFoundError(f"PDF folder not found: {pdf_folder}")
        
        pdf_files = list(pdf_folder.glob('*.pdf'))
        
        # Filter out already processed files
        unprocessed_files = [
            pdf for pdf in pdf_files 
            if pdf.name not in self.processed_files
        ]
        
        # Multi-machine support: distribute files across machines
        if self.total_machines > 1:
            # Sort files for consistent distribution
            unprocessed_files.sort(key=lambda x: x.name)
            
            # Calculate files for this machine
            machine_files = []
            for i, pdf_file in enumerate(unprocessed_files):
                if i % self.total_machines == self.machine_id:
                    machine_files.append(pdf_file)
            
            unprocessed_files = machine_files
            self.logger.info(f"Multi-machine mode: Machine {self.machine_id}/{self.total_machines}")
            self.logger.info(f"This machine will process {len(unprocessed_files)} files")
        
        self.logger.info(f"Found {len(pdf_files)} total PDF files")
        self.logger.info(f"Found {len(unprocessed_files)} unprocessed PDF files for this machine")
        
        return unprocessed_files
    
    def run(self):
        """Main execution method."""
        try:
            self.logger.info("Starting PDF to Q&A dataset generation")
            
            # Get PDF files to process
            pdf_files = self._get_pdf_files()
            
            if not pdf_files:
                self.logger.info("No unprocessed PDF files found. Nothing to do.")
                return
            
            # Process files in parallel
            successful_count = 0
            failed_count = 0
            
            with ThreadPoolExecutor(max_workers=self._get_config_value('pdf_processing.num_workers', 1)) as executor:
                # Submit all tasks
                future_to_pdf = {
                    executor.submit(self._process_single_pdf, pdf_path): pdf_path 
                    for pdf_path in pdf_files
                }
                
                # Process completed tasks
                for future in as_completed(future_to_pdf):
                    pdf_path = future_to_pdf[future]
                    try:
                        success = future.result()
                        if success:
                            successful_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        self.logger.error(f"Unexpected error processing {pdf_path.name}: {e}")
                        failed_count += 1
            
            # Final summary
            total_processed = successful_count + failed_count
            self.logger.info(f"Processing completed!")
            self.logger.info(f"Total files processed: {total_processed}")
            self.logger.info(f"Successful: {successful_count}")
            self.logger.info(f"Failed: {failed_count}")
            
            if successful_count > 0:
                output_path = Path(self._get_config_value('pdf_processing.output_folder', 'output_json')) / self._get_config_value('pdf_processing.output_filename', 'toplam_egitim_veriseti.jsonl')
                self.logger.info(f"Output saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Fatal error in main execution: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate Q&A datasets from PDF files using Gemini API"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = PDFToQAGenerator(config_path=args.config)
        generator.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
