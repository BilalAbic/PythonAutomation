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
        if APIKeyManager:
            self.api_manager = APIKeyManager(self.config['api_keys'], self.logger)
            active_count = self.api_manager.test_all_keys()
            if active_count == 0:
                raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            self.logger.info(f"✅ {active_count}/{len(self.config['api_keys'])} API key aktif")
        else:
            # Fallback to original implementation
            self._current_api_key_index = 0
            self._api_key_lock = threading.Lock()
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
        """Create the prompt for Gemini API."""
        max_questions = self._get_config_value('pdf_processing.max_questions_per_pdf', 15)
        
        prompt = f"""
Sen, büyük dil modellerini eğitmek için ULTRA KALİTELİ veri seti hazırlayan uzman bir tıbbi beslenme ve sağlık veri analisti uzmanısın.
Görevin, sana sunulan PDF dokümanının içeriğini (metin, tablolar ve görseller dahil) derinlemesine analiz ederek, LLM eğitimi için PROFESYONEL SEVİYEDE, yüksek kaliteli ve çeşitli Soru-Cevap çiftleri oluşturmaktır.

**ULTRA KALİTE STANDARTLARI:**
Bu veri seti Harvard, WHO, ADA gibi prestijli kurumların standartlarında olmalı. Her soru-cevap çifti eğitim değeri taşımalı ve gerçek sağlık profesyonelleri tarafından kullanılabilir olmalı.

**SORU ÇEŞİTLERİ VE KALİTE SEVİYELERİ:**

1. **SPESİFİK BİLGİ SORULARI** (En yüksek öncelik):
   - "WHO'nun günlük tuz tüketimi için önerdiği limit nedir?"
   - "Harvard Sağlıklı Yemek Tabağı modeli nasıl bir öğün dağılımı önerir?"
   - "Diyabet hastalarında HbA1c hedef değerleri nelerdir?"

2. **KLİNİK SENARYO SORULARI** (Ultra kaliteli):
   - "45 yaşında tip 2 diyabetli, BMI 32 olan bir hastaya nasıl beslenme önerileri verirsiniz?"
   - "Gebelikte gestasyonel diyabet gelişen 28 yaşındaki hastaya hangi diyet yaklaşımı uygulanır?"
   - "Kronik böbrek yetmezliği olan hastada protein kısıtlaması nasıl yapılır?"

3. **KOMPARATİF ANALİZ SORULARI**:
   - "Akdeniz diyeti ile DASH diyeti arasındaki temel farklar nelerdir?"
   - "Ketojenik diyet ile düşük karbonhidratlı diyet arasındaki farklar nelerdir?"

4. **FİZYOPATOLOJİK MEKANIZMA SORULARI**:
   - "İnsülin direncinin gelişim mekanizması nedir?"
   - "Omega-3 yağ asitlerinin kardiyovasküler sistem üzerindeki etki mekanizmaları nelerdir?"

**CEVAP KALİTE KURALLARI (ULTRA STANDART):**
1. **DETAYLILIK**: Cevaplar minimum 4-6 cümle, ideal olarak 150-300 kelime arası
2. **BİLİMSEL DOĞRULUK**: Sadece kanıtlanmış, bilimsel bilgiler
3. **PRATİK UYGULANABILIRLIK**: Her cevap gerçek hayatta uygulanabilir olmalı
4. **PROFESYONEL DİL**: Tıbbi terminoloji doğru kullanılmalı ama anlaşılır olmalı
5. **KAPSAMLILIK**: Sebep-sonuç ilişkileri, mekanizmalar, öneriler dahil edilmeli
6. **GÜNCEL BILGI**: En son kılavuzlar ve öneriler referans alınmalı

**YASAK KURALLAR (KESİN):**
- Tablo, şekil, grafik numaralarına referans verme
- "Yukarıdaki tabloda", "Aşağıdaki şekilde" ifadeleri yasak
- Kısa, eksik cevaplar (100 kelimeden az) yasak
- Belirsiz ifadeler ("genellikle", "çoğunlukla" gibi) minimal kullan
- Genel geçer cevaplar yasak - spesifik ve detaylı ol

**ÖRNEK ULTRA KALİTE SORU-CEVAP:**
Soru: "Tip 2 diyabetli hastalarda karbonhidrat sayımı yönteminin avantajları nelerdir?"
Cevap: "Karbonhidrat sayımı yöntemi, tip 2 diyabetli hastalara kan glukoz seviyelerini daha iyi kontrol etme imkanı sağlar. Bu yöntemde hastalar tükettikleri karbonhidrat miktarına göre insülin dozunu ayarlayabilirler. Sistemin temel avantajları arasında; esnek yemek planlaması, daha iyi glisemik kontrol (HbA1c değerlerinde %0.5-1 azalma), yaşam kalitesinde artış ve hipoglisemi riskinde azalma yer alır. Yöntem özellikle çoklu insülin enjeksiyonu kullanan hastalarda etkilidir ve karbonhidrat/insülin oranı belirlenerek kişiselleştirilerek uygulanır."

**ÇIKTI KURALLARI:**
1. Sadece JSON array formatı: `[{{"soru": "...", "cevap": "..."}}, ...]`
2. Her cevap yukarıdaki kalite standardında olmalı
3. En fazla {max_questions} soru-cevap çifti üret
4. Kalite her şeyden önemli - az ama mükemmel üret

Bu standartlarda veri üret. Hedef: Tıp fakültesi öğrencilerinin ve sağlık profesyonellerinin kullanabileceği seviyede kalite.
"""
        return prompt.strip()
    
    def _call_gemini_api(self, text_content: str, images: List[bytes], max_retries: int = None) -> Optional[List[Dict]]:
        """Call Gemini API with text and images, with enhanced retry logic and API key rotation."""
        if max_retries is None:
            max_retries = self._get_config_value('safety_settings.max_retries_per_key', 2) * len(self.config['api_keys'])
        
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
                
                # Parse JSON response
                try:
                    # Clean the response text (remove markdown code blocks if present)
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    
                    qa_pairs = json.loads(response_text)
                    
                    if not isinstance(qa_pairs, list):
                        self.logger.warning("Response is not a JSON array")
                        continue
                    
                    # Validate each Q&A pair with quality checks
                    valid_pairs = []
                    for qa in qa_pairs:
                        if isinstance(qa, dict) and all(key in qa for key in ['soru', 'cevap']):
                            # Ultra quality checks
                            question = qa['soru'].strip()
                            answer = qa['cevap'].strip()
                            
                            # Check for ultra quality minimum length standards
                            if len(question) < 15 or len(answer) < 100:
                                self.logger.warning(f"Skipping low quality Q&A: Question too short ({len(question)} chars) or answer too brief ({len(answer)} chars)")
                                continue
                                
                            # Check for forbidden table/figure references
                            forbidden_patterns = [
                                'tablo', 'şekil', 'grafik', 'çizelge', 'resim',
                                'yukarıdaki', 'aşağıdaki', 'tabloda', 'şekilde', 
                                'grafikte', 'görselde', 'fotoğrafta'
                            ]
                            
                            answer_lower = answer.lower()
                            question_lower = question.lower()
                            
                            # Check for table/figure references in Turkish
                            has_forbidden = False
                            for pattern in forbidden_patterns:
                                if pattern in answer_lower or pattern in question_lower:
                                    # Allow some exceptions like "şekillenmesi", "tablolama" etc.
                                    if not any(exception in answer_lower for exception in ['şekillenmesi', 'şekillenir', 'tablolama']):
                                        has_forbidden = True
                                        break
                            
                            # Check for numbered references like "Tablo 3.1", "Şekil 2"
                            import re
                            if re.search(r'(tablo|şekil|grafik|çizelge)\s*\d+', answer_lower) or \
                               re.search(r'(tablo|şekil|grafik|çizelge)\s*\d+', question_lower):
                                has_forbidden = True
                            
                            if has_forbidden:
                                self.logger.warning(f"Skipping Q&A with table/figure reference")
                                continue
                            
                            # Check for ultra quality word count (professional level)
                            word_count = len(answer.split())
                            if word_count < 25:
                                self.logger.warning(f"Skipping Q&A with too brief answer ({word_count} words) - need minimum 25 words for ultra quality")
                                continue
                            
                            # Check for too generic or vague language
                            vague_patterns = ['genellikle', 'çoğunlukla', 'bazen', 'muhtemelen', 'sanırım']
                            vague_count = sum(1 for pattern in vague_patterns if pattern in answer.lower())
                            if vague_count > 2:
                                self.logger.warning(f"Skipping Q&A with too much vague language ({vague_count} vague words)")
                                continue
                            
                            valid_pairs.append(qa)
                        else:
                            self.logger.warning(f"Invalid Q&A pair format: {qa}")
                    
                    if valid_pairs:
                        self.logger.info(f"Generated {len(valid_pairs)} valid Q&A pairs (filtered for quality)")
                        return valid_pairs
                    else:
                        self.logger.warning("No valid Q&A pairs found in response after quality filtering")
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
                        self.logger.info(f"Rate limit detected, waiting {delay}s before retry...")
                        time.sleep(delay)
                    
                    # Try to rotate API key if we haven't exhausted retries for current key
                    if attempt % self.config.get('max_retries_per_key', 2) == (self.config.get('max_retries_per_key', 2) - 1):
                        if self._rotate_api_key():
                            self.logger.info("Rotated API key due to limits, retrying...")
                            continue
                        else:
                            self.logger.error("All API keys exhausted, cannot continue")
                            return None
                    else:
                        # Wait before retry with same key
                        time.sleep(self.config.get('api_rate_limit_delay', 2))
                        continue
                        
                elif 'timeout' in error_msg or 'deadline' in error_msg:
                    self.logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
                    # Increase delay for timeout errors
                    timeout_delay = min(5 * (attempt + 1), 30)
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
            
            # Save to output file without source information
            output_path = Path(self._get_config_value('pdf_processing.output_folder', 'output_json')) / self._get_config_value('pdf_processing.output_filename', 'toplam_egitim_veriseti.jsonl')
            
            with open(output_path, 'a', encoding='utf-8') as f:
                for qa in all_qa_pairs:
                    # Remove source information from output - only keep soru and cevap
                    clean_qa = {'soru': qa['soru'], 'cevap': qa['cevap']}
                    f.write(json.dumps(clean_qa, ensure_ascii=False) + '\n')
            
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
