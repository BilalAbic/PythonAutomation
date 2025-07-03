#!/usr/bin/env python3
"""
ULTRA-TECHNICAL DIETITIAN Q&A Dataset Generator
Professional-grade technical content for advanced dietitian chatbot training
Generates highly technical nutrition science questions with expert-level answers
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

# Enhanced imports
try:
    from pdf_api_manager import APIKeyManager
except ImportError:
    APIKeyManager = None  # Fallback to original implementation


class UltraTechnicalDietitianProcessor:
    """Ultra-technical dietitian Q&A processor for expert-level training data."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the ultra-technical dietitian processor."""
        print("🧬 Ultra-Technical Dietitian Processor başlatılıyor...")
        
        # Setup basic logging first
        self._setup_basic_logging()
        
        # Config yükle ve doğrula
        self.config = self._load_config(config_path)
        
        # Setup enhanced logging with config
        self._setup_logging()
        self._setup_output_directory()
        
        # Enhanced safety settings
        self.setup_safety_systems()
        
        # API key management
        if APIKeyManager:
            self.api_manager = APIKeyManager(self.config['api_keys'], self.logger)
            active_count = self.api_manager.test_all_keys()
            if active_count == 0:
                raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            self.logger.info(f"✅ {active_count}/{len(self.config['api_keys'])} API key aktif")
        else:
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
        
        # Track processed files
        self.processed_files = self._get_already_processed_files()
        
        # Enhanced stats
        self.stats = {
            'total_pdfs_processed': 0,
            'total_technical_questions_generated': 0,
            'expert_level_pairs': 0,
            'biochemical_concepts': 0,
            'clinical_applications': 0,
            'start_time': datetime.now().isoformat()
        }
        
        self.config_file_path = config_path
        self.config_last_modified = os.path.getmtime(config_path)
        
        self.logger.info(f"🧬 Ultra-Technical Dietitian Processor hazır!")
        self.logger.info(f"📁 Configuration: {config_path}")
        self.logger.info(f"🤖 Machine ID: {self.machine_id}/{self.total_machines}")
        self.logger.info(f"📄 Processed files: {len(self.processed_files)}")
        
        if APIKeyManager:
            self.logger.info(f"🔑 Enhanced API management: ACTIVE")
    
    def _create_ultra_technical_prompt(self) -> str:
        """Create ultra-technical prompt for expert-level dietitian training."""
        prompt = f"""
Sana verilen metin içeriğinden, UZMAN DİYETİSYEN VE BESLENME BİLİMCİSİ için ULTRA-TEKNİK, PROFESYONELce soru-cevap çiftleri üret.

🎯 HEDEF: Yüksek lisans/doktora seviyesi diyetisyen eğitimi için uzman teknik veri

📋 ÇIKTI FORMATI (SADECE BU FORMAT):
[
  {{"soru": "Teknik diyetisyenlik sorusu", "cevap": "Uzman seviye teknik cevap"}},
  {{"soru": "Biyokimyasal beslenme sorusu", "cevap": "Moleküler düzey detaylı cevap"}}
]

🚫 KESINLIKLE YASAK:
- "makalede", "metinde", "kaynaklarda", "yukarıda", "aşağıda" 
- "belirtildiği gibi", "anlatıldığı üzere", "bahsedildiği"
- "bu", "şu", "bunlar" ile soru başlatma
- Basit, temel seviye sorular

✅ ULTRA-TEKNİK DİYETİSYEN SORULARI:

**BİYOKİMYASAL BESLENME BİLİMİ (35%):**
- "Laktoz intoleransında β-galaktosidaz enzim eksikliğinin intestinal mikrobiyota kompozisyonu üzerindeki moleküler etkileri nelerdir?"
- "Fruktoz metabolizmasında ALDOB enzim polimorfizmlerinin hepatik lipogenez ve NAFLD patogenezi ile ilişkisi nasıldır?"
- "Arginin-nitrik oksit-cGMP sinyal yolağında beslenmenin endotel fonksiyonları üzerindeki epigenetik düzenleyici mekanizmaları nelerdir?"

**KLİNİK BESLENME FARMAKOLOJİSİ (30%):**
- "Varfarin antikoagülan tedavisinde Vitamin K1 (fillokinon) ve K2 (menakinon-7) formlarının INR değerleri üzerindeki farklı etki mekanizmaları nelerdir?"
- "CYP450 enzim polimorfizmlerinin kafein metabolizması ve adenozin reseptör antagonizmi üzerindeki bireysel varyasyonları nasıl etkiler?"
- "Metformin kullanan Tip 2 diyabetlilerde B12 malabsorpsiyonunun intrinsik faktör-kobalt kompleksi üzerindeki moleküler etki mekanizması nedir?"

**MOLEKÜLER NUTRİGENOMİK (25%):**
- "APOE ε4 allel varyantında omega-3 yağ asitlerinin beyinde neuroinflasyon ve amiloid-β birikimi üzerindeki moleküler koruyucu mekanizmaları nelerdir?"
- "MTHFR C677T polimorfizminde folat metabolizmasının homoksistein remetilasyon döngüsü ve DNA metilasyon paternleri üzerindeki etkisi nasıldır?"
- "FADS1/FADS2 gen ekspresyon varyasyonlarının araşidonik asit/EPA oranı ve prostaglandin E2/E3 dengesine etkisi nedir?"

**İLERİ KLİNİK UYGULAMALAR (10%):**
- "Krohn hastalığında intestinal permeabilite artışının tight junction proteinleri (claudin-1, zonulin) üzerindeki etkisi ve glutamin takviyesinin moleküler onarım mekanizması nedir?"
- "Parkinson hastalığında dopamin prekürsörü L-DOPA tedavisinde amino asit kompetisyonunun blood-brain barrier taşıyıcı proteinleri üzerindeki etkisi nasıldır?"

🔬 TEKNİK REQUİREMENTLER:

**SORU KALİTESİ:**
- Mutlaka enzim isimleri, metabolik pathway'lar içersin
- Moleküler mekanizmalar, reseptör etkileşimleri
- Genetik polimorfizmler, epigenetik faktörler
- Farmakokinetik/farmakodinamik etkileşimler
- Biyomarkır değerlendirmeleri

**CEVAP KALİTESİ:**
- 200-400 kelime arası detaylı açıklama
- Moleküler düzeyde açıklamalar
- Enzim kinetik parametreleri (Km, Vmax)
- Serum/plazma konsantrasyon değerleri
- Doz-yanıt ilişkileri
- Klinik korelasyonlar

**PROFESYONEL DİL:**
- Enzim isimlerini doğru kullan (örn: α-amylase, lipase, pepsinogen)
- Metabolit isimlerini tam adı ile (örn: 25-hydroxyvitamin D3, methylcobalamin)
- Ölçüm birimleri (nmol/L, μg/dL, mEq/L, μmol/L)
- Farmakolojik terimler (bioavailability, clearance, half-life)
- Laboratuvar değerleri ve referans aralıkları

**YASAKLI İFADELER:**
- Genel tavsiyeler ("sağlıklı beslenin")
- Temel bilgiler ("protein kas yapımı için gerekli")
- Belirsiz ifadeler ("bazı vitaminler")
- Popüler beslenme mitleri

Ürettiğin her soru-cevap çifti UZMAN DİYETİSYEN seviyesinde olmalı ve ileri düzey biyokimya, farmakoloji, genetik bilgisi gerektirmelidir.

ÇOK ÖNEMLİ: Sadece JSON formatında döndür, başka açıklama yapma!
"""

        return prompt

    def _validate_ultra_technical_qa(self, qa: Dict) -> bool:
        """Ultra-technical validation for expert-level dietitian Q&A pairs."""
        if not isinstance(qa, dict):
            return False
        
        if "soru" not in qa or "cevap" not in qa:
            return False
        
        soru = qa["soru"].strip()
        cevap = qa["cevap"].strip()
        
        # Technical length requirements (longer for expert content)
        if len(soru) < 30 or len(cevap) < 200:
            self.logger.warning(f"Ultra-technical Q&A too short: Q={len(soru)} chars, A={len(cevap)} chars")
            return False
        
        if len(soru) > 500 or len(cevap) > 2000:
            self.logger.warning(f"Ultra-technical Q&A too long: Q={len(soru)} chars, A={len(cevap)} chars")
            return False
        
        # Word count for expert level content
        soru_words = len(soru.split())
        cevap_words = len(cevap.split())
        
        if soru_words < 12 or soru_words > 60:
            self.logger.warning(f"Ultra-technical question word count: {soru_words} words")
            return False
            
        if cevap_words < 80 or cevap_words > 500:
            self.logger.warning(f"Ultra-technical answer word count: {cevap_words} words")
            return False
        
        # Forbidden reference words
        forbidden_words = [
            'makalede', 'metinde', 'kaynaklarda', 'yukarıda', 'aşağıda',
            'belirtildiği gibi', 'anlatıldığı üzere', 'bahsedildiği', 
            'şekilde gösterildiği', 'grafikte', 'resimde',
            'bu makalede', 'bu metinde', 'bu araştırmada', 'yukarıdaki',
            'aşağıdaki', 'gösterilen', 'verilen tabloda'
        ]
        
        soru_lower = soru.lower()
        cevap_lower = cevap.lower()
        
        for forbidden in forbidden_words:
            if forbidden in soru_lower or forbidden in cevap_lower:
                self.logger.warning(f"Forbidden reference detected: '{forbidden}' in ultra-technical Q&A")
                return False
        
        # Ultra-technical terminology validation
        technical_terms = [
            # Enzymes & proteins
            'enzim', 'protein', 'reseptör', 'kinaz', 'fosfataz', 'hidrolaz',
            'lipaz', 'amilaz', 'pepsinogen', 'tripsinogen', 'katalaz',
            
            # Biochemical pathways
            'metabolizma', 'glikoliz', 'glukoneogenez', 'lipogenez', 'lipoliz',
            'fosforilasyon', 'defosforilasyon', 'oksidatif', 'ATP', 'NADH',
            
            # Molecular terms
            'polimorfizm', 'allel', 'gen ekspresyonu', 'transkripsiyon', 'translasyon',
            'epigenetik', 'metilasyon', 'asetilasyon', 'mikroRNA',
            
            # Clinical biochemistry
            'biomarkır', 'farmakokinet', 'farmakodinamik', 'absorpsiyon', 'dağılım',
            'metabolizma', 'eliminasyon', 'yarı ömür', 'biyoyararlanım', 'klirens',
            
            # Measurements & units
            'nmol/L', 'μg/dL', 'mg/L', 'mEq/L', 'μmol/L', 'ng/mL', 'IU/L',
            'reference range', 'cut-off', 'sensitivite', 'spesifisite',
            
            # Advanced nutrition
            'nutrigenetik', 'nutrigenomik', 'mikrobiyom', 'metabolomik',
            'proteomik', 'epigenome', 'intestinal permeabilite'
        ]
        
        # Check for technical terms in both question and answer
        has_technical_terms = any(term in soru_lower or term in cevap_lower for term in technical_terms)
        
        if not has_technical_terms:
            self.logger.warning("Ultra-technical Q&A lacks advanced technical terminology")
            return False
        
        # Advanced technical question indicators
        advanced_question_indicators = [
            # Technical question starters
            'moleküler mekanizma', 'biyokimyasal', 'enzimatik', 'metabolik pathway',
            'gen polimorfizm', 'protein etkileşim', 'reseptör aktivasyon',
            'farmakokinet', 'farmakodinamik', 'absorpsiyon mekanizma',
            
            # Expert terminology
            'patogenez', 'etiyopatogenez', 'patofizyoloji', 'moleküler hedef',
            'sinyal ileti', 'transdüksiyon', 'regülasyon', 'homeostaz'
        ]
        
        has_advanced_question = any(indicator in soru_lower for indicator in advanced_question_indicators)
        
        if not has_advanced_question:
            self.logger.warning("Question lacks ultra-technical indicators")
            return False
        
        # Check for measurement units and technical precision
        measurement_indicators = [
            'μg', 'mg', 'ng', 'pg', 'nmol', 'μmol', 'mmol', 'mEq',
            '/L', '/dL', '/mL', 'IU', 'kDa', 'rpm', '°C', 'pH',
            '%', 'ratio', 'index', 'score', 'grade'
        ]
        
        has_measurements = any(unit in cevap for unit in measurement_indicators)
        
        if not has_measurements:
            self.logger.info("Answer could benefit from technical measurements/units")
        
        # Professional expert language check
        expert_language_indicators = [
            'mekanizma', 'regülasyon', 'modulasyon', 'aktivasyon', 'inhibisyon',
            'indüksiyon', 'supresyon', 'ekspresyon', 'transkripsiyon',
            'post-translasyonel', 'allosterik', 'kompetitif', 'non-kompetitif',
            'Km değeri', 'Vmax', 'Ki', 'IC50', 'EC50', 'Kd',
            'afinite', 'spesifisite', 'katalitik aktivite'
        ]
        
        has_expert_language = any(indicator in cevap_lower for indicator in expert_language_indicators)
        
        if not has_expert_language:
            self.logger.info("Answer could be more technically sophisticated")
        
        return True

    # Copy essential methods from the original class
    def setup_safety_systems(self):
        """Safety systems setup"""
        self.emergency_stop_file = 'EMERGENCY_STOP_ULTRA_TECH'
        if os.path.exists(self.emergency_stop_file):
            os.remove(self.emergency_stop_file)
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        os.makedirs('checkpoints', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('ultra_technical_output', exist_ok=True)
        
        self.logger.info("🧬 Ultra-technical safety systems ready")
        
    def _signal_handler(self, signum, frame):
        """Signal handler"""
        self.logger.warning(f"Signal {signum} received. Ultra-technical shutdown...")
        self.emergency_shutdown()
        sys.exit(0)
        
    def emergency_shutdown(self):
        """Emergency shutdown for ultra-technical processor"""
        self.logger.critical("🚨 ULTRA-TECHNICAL EMERGENCY SHUTDOWN!")
        
        emergency_data = {
            "shutdown_time": datetime.now().isoformat(),
            "stats": getattr(self, 'stats', {}),
            "processed_files": list(getattr(self, 'processed_files', set())),
            "reason": "Ultra-technical emergency shutdown"
        }
        
        try:
            with open('emergency_shutdown_ultra_tech.json', 'w', encoding='utf-8') as f:
                json.dump(emergency_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'pdf_processing' in config:
                self._validate_enhanced_config(config)
            else:
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
                
    def _convert_legacy_config(self, config: Dict) -> Dict:
        """Convert legacy config"""
        required_keys = ['api_keys', 'pdf_folder', 'output_folder', 'output_filename']
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Convert to enhanced format
        enhanced_config = {
            'api_keys': config['api_keys'],
            'pdf_processing': {
                'pdf_folder': config['pdf_folder'],
                'output_folder': 'ultra_technical_output',  # Special output folder
                'output_filename': 'ultra_technical_dietitian_dataset.jsonl',
                'model_name': config.get('model_name', 'gemini-1.5-flash-latest'),
                'max_tokens_per_chunk': config.get('max_tokens_per_chunk', 50000),
                'chunk_overlap': config.get('chunk_overlap', 1000),
                'api_timeout_seconds': config.get('api_timeout_seconds', 600)
            },
            'safety_settings': {
                'max_retries_per_key': config.get('max_retries_per_key', 2),
                'api_rate_limit_delay': config.get('api_rate_limit_delay', 2),
                'min_delay_between_calls': config.get('min_delay_between_calls', 3),
                'max_delay_between_calls': config.get('max_delay_between_calls', 15),
                'adaptive_delay': config.get('adaptive_delay', True),
                'api_key_rotation_delay': config.get('api_key_rotation_delay', 5)
            },
            'multi_machine': config.get('multi_machine', {
                'machine_id': 0,
                'total_machines': 1
            })
        }
        
        self.logger.info("📄 Legacy config converted to ultra-technical enhanced format")
        return enhanced_config

    def _get_config_value(self, key_path: str, default=None):
        """Get nested config value"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def _setup_basic_logging(self):
        """Setup basic logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def _setup_logging(self):
        """Setup enhanced logging for ultra-technical processing"""
        # Create logger
        self.logger = logging.getLogger('UltraTechnicalDietitianProcessor')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for ultra-technical logs
        log_filename = self._get_config_value('pdf_processing.log_filename', 'ultra_technical_processing.log')
        
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
        
        # Timestamped log file for this session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        timestamped_handler = logging.FileHandler(
            f"logs/ultra_technical_dietitian_{timestamp}.log", 
            encoding='utf-8'
        )
        timestamped_handler.setLevel(logging.DEBUG)
        timestamped_handler.setFormatter(formatter)
        self.logger.addHandler(timestamped_handler)
    
    def _setup_output_directory(self):
        """Create ultra-technical output directory"""
        output_dir = Path(self._get_config_value('pdf_processing.output_folder', 'ultra_technical_output'))
        output_dir.mkdir(exist_ok=True)
        self.logger.info(f"Ultra-technical output directory ready: {output_dir}")
    
    def _configure_gemini(self):
        """Configure Gemini API"""
        if not self.config['api_keys']:
            raise ValueError("No API keys provided in configuration")
        
        genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
        self.logger.info(f"Configured Gemini API for ultra-technical processing: key index {self._current_api_key_index}")
    
    def _get_already_processed_files(self) -> Set[str]:
        """Get already processed files (disabled for ultra-technical reprocessing)"""
        processed_files = set()
        self.logger.info(f"Ultra-technical mode: reprocessing all files for expert-level content")
        return processed_files

    def _create_prompt(self) -> str:
        """Use ultra-technical prompt"""
        return self._create_ultra_technical_prompt()

    def _validate_qa_pair(self, qa: Dict) -> bool:
        """Use ultra-technical validation"""
        return self._validate_ultra_technical_qa(qa)


    def _rotate_api_key(self) -> bool:
        """Rotate to the next API key with thread safety."""
        with self._api_key_lock:
            self._current_api_key_index += 1
            
            if self._current_api_key_index >= len(self.config['api_keys']):
                self.logger.error("All API keys exhausted")
                return False
            
            try:
                genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
                self.logger.info(f"Rotated to API key index: {self._current_api_key_index}")
                
                delay = self._get_config_value('safety_settings.api_key_rotation_delay', 5)
                self.logger.info(f"Waiting {delay}s after API key rotation...")
                time.sleep(delay)
                
                return True
            except Exception as e:
                self.logger.error(f"Failed to configure new API key: {e}")
                return False

    def _adaptive_rate_limit(self):
        """Implement adaptive rate limiting for ultra-technical processing."""
        current_time = time.time()
        
        # Clean old call times
        self._api_call_times = [t for t in self._api_call_times if current_time - t < 60]
        
        calls_per_minute = len(self._api_call_times)
        
        if self._get_config_value('safety_settings.adaptive_delay', True):
            if calls_per_minute > 40:  # More conservative for ultra-technical
                self._current_delay = min(self._current_delay * 1.5, self._get_config_value('safety_settings.max_delay_between_calls', 20))
            elif calls_per_minute < 15:
                self._current_delay = max(self._current_delay * 0.8, self._get_config_value('safety_settings.min_delay_between_calls', 5))
        else:
            self._current_delay = self._get_config_value('safety_settings.api_rate_limit_delay', 3)
        
        # Ensure minimum time between calls
        time_since_last_call = current_time - self._last_api_call_time
        if time_since_last_call < self._current_delay:
            sleep_time = self._current_delay - time_since_last_call
            if sleep_time > 0.1:
                self.logger.debug(f"Ultra-technical rate limiting: waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self._api_call_times.append(time.time())
        self._last_api_call_time = time.time()

    def _extract_pdf_content(self, pdf_path: Path) -> Tuple[str, List[bytes]]:
        """Extract text and images from PDF for ultra-technical analysis."""
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            all_images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                all_text += f"\n--- Sayfa {page_num + 1} ---\n{text}"
                
                # Extract images for technical diagrams
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:
                            img_data = pix.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                        else:
                            pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix_rgb.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                            pix_rgb = None
                        
                        pix = None
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index}: {e}")
                        continue
                
                # Extract technical tables
                try:
                    if text.strip():
                        tables = page.find_tables()
                        if tables:
                            for table_index, table in enumerate(tables):
                                try:
                                    bbox = table.bbox
                                    mat = fitz.Matrix(2, 2)
                                    pix = page.get_pixmap(matrix=mat, clip=bbox)
                                    img_data = pix.pil_tobytes(format="PNG")
                                    all_images.append(img_data)
                                    pix = None
                                except Exception as e:
                                    if "not a textpage" not in str(e).lower():
                                        self.logger.warning(f"Table extraction error: {e}")
                                    continue
                except Exception as e:
                    if "not a textpage" not in str(e).lower():
                        self.logger.warning(f"Technical table processing error: {e}")
            
            doc.close()
            self.logger.info(f"Ultra-technical extraction from {pdf_path.name}: {len(all_text)} chars, {len(all_images)} images")
            return all_text, all_images
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from {pdf_path}: {e}")
            raise

    def _clean_and_fix_json(self, json_text: str) -> str:
        """Advanced JSON cleaning for ultra-technical responses."""
        import re
        
        # Remove markdown code blocks
        json_text = re.sub(r'```json\s*', '', json_text)
        json_text = re.sub(r'```\s*$', '', json_text)
        
        # Fix common JSON issues
        fixes_applied = []
        
        # Fix single quotes to double quotes
        if "'" in json_text:
            def fix_quotes_in_strings(match):
                content = match.group(1)
                fixed_content = content.replace("'", "'")
                return f'"{fixed_content}"'
            
            # Fix quotes in string values
            json_text = re.sub(r'"([^"]*)"', fix_quotes_in_strings, json_text)
            json_text = json_text.replace("'", '"')
            fixes_applied.append("single_quotes")
        
        # Fix trailing commas
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        # Fix missing commas between objects
        json_text = re.sub(r'}\s*{', '}, {', json_text)
        
        # Fix escaped characters that shouldn't be escaped
        json_text = json_text.replace('\\"', '"')
        
        if fixes_applied:
            self.logger.info(f"Applied ultra-technical JSON fixes: {', '.join(fixes_applied)}")
        
        return json_text.strip()

    def _extract_valid_qa_objects(self, text: str) -> str:
        """Extract valid Q&A objects from malformed ultra-technical JSON."""
        import re
        
        # Pattern to find individual Q&A objects
        qa_pattern = r'\{\s*"soru"\s*:\s*"([^"]+)"\s*,\s*"cevap"\s*:\s*"([^"]+)"\s*\}'
        
        matches = re.findall(qa_pattern, text, re.DOTALL)
        
        if matches:
            valid_objects = []
            for soru, cevap in matches:
                # Clean the extracted text
                soru = soru.strip().replace('\\"', '"')
                cevap = cevap.strip().replace('\\"', '"')
                
                if len(soru) > 20 and len(cevap) > 100:  # Ultra-technical minimum lengths
                    valid_objects.append({
                        "soru": soru,
                        "cevap": cevap
                    })
            
            if valid_objects:
                self.logger.info(f"Extracted {len(valid_objects)} valid ultra-technical Q&A objects")
                return json.dumps(valid_objects, ensure_ascii=False)
        
        return None

    def _call_gemini_api(self, text_content: str, images: List[bytes], max_retries: int = None) -> Optional[List[Dict]]:
        """Call Gemini API for ultra-technical content generation."""
        if max_retries is None:
            max_retries = self._get_config_value('safety_settings.max_retries_per_key', 3) * len(self.config['api_keys'])
        
        prompt = self._create_prompt()
        
        for attempt in range(max_retries):
            try:
                # self._adaptive_rate_limit()  # Will add this method later
                
                model = genai.GenerativeModel(self._get_config_value('pdf_processing.model_name', 'gemini-1.5-flash-latest'))
                
                content_parts = [prompt, text_content]
                
                # Add images (limit for performance)
                image_count = 0
                for img_data in images:
                    if image_count >= 8:  # Limit for ultra-technical processing
                        break
                    try:
                        pil_img = Image.open(io.BytesIO(img_data))
                        content_parts.append(pil_img)
                        image_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to process technical image: {e}")
                        continue
                
                response = model.generate_content(
                    content_parts,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=10240,  # Increased for technical content
                        temperature=0.1,  # Low temperature for consistency
                    ),
                    request_options={'timeout': self._get_config_value('pdf_processing.api_timeout_seconds', 600)}
                )
                
                if not response.text:
                    self.logger.warning("Empty response from Gemini API")
                    time.sleep(1)
                    continue
                
                # Parse ultra-technical JSON response
                try:
                    response_text = response.text.strip()
                    
                    # Remove markdown blocks
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.startswith('```'):
                        response_text = response_text[3:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    
                    response_text = response_text.strip()
                    
                    # Try to parse JSON directly
                    try:
                        qa_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Ultra-technical JSON parsing failed, trying fixes...")
                        # Try basic cleaning
                        response_text = response_text.replace("'", '"')
                        try:
                            qa_data = json.loads(response_text)
                        except json.JSONDecodeError as parse_error:
                            self.logger.warning(f"Ultra-technical JSON still invalid: {parse_error}")
                            continue
                    
                    if not isinstance(qa_data, list):
                        self.logger.warning("Ultra-technical response is not a list")
                        continue
                    
                    # Validate ultra-technical Q&A pairs
                    valid_qa_pairs = []
                    ultra_technical_count = 0
                    expert_level_count = 0
                    
                    for qa in qa_data:
                        if self._validate_qa_pair(qa):
                            valid_qa_pairs.append(qa)
                            
                            # Count ultra-technical indicators
                            soru_lower = qa["soru"].lower()
                            cevap_lower = qa["cevap"].lower()
                            
                            technical_indicators = ['enzim', 'protein', 'moleküler', 'biyokimyasal', 'farmakokinet', 'gen', 'polimorfizm']
                            if any(ind in soru_lower or ind in cevap_lower for ind in technical_indicators):
                                ultra_technical_count += 1
                            
                            expert_indicators = ['pathway', 'mekanizma', 'metabolizma', 'regülasyon', 'kinetik']
                            if any(ind in cevap_lower for ind in expert_indicators):
                                expert_level_count += 1
                    
                    if not valid_qa_pairs:
                        self.logger.warning("No valid ultra-technical Q&A pairs found after filtering")
                        continue
                    
                    # Calculate ultra-technical quality metrics
                    avg_q_length = sum(len(qa["soru"].split()) for qa in valid_qa_pairs) / len(valid_qa_pairs)
                    avg_a_length = sum(len(qa["cevap"].split()) for qa in valid_qa_pairs) / len(valid_qa_pairs)
                    
                    self.logger.info(f"🧬 Ultra-Technical Quality Metrics - Questions: {len(valid_qa_pairs)}, "
                                   f"Technical: {ultra_technical_count}, Expert: {expert_level_count}, "
                                   f"Avg Q Length: {avg_q_length:.1f}, Avg A Length: {avg_a_length:.1f} words")
                    
                    return valid_qa_pairs
                    
                except Exception as parse_error:
                    self.logger.error(f"Ultra-technical parsing error: {parse_error}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return None
                        
            except Exception as e:
                error_msg = str(e).lower()
                
                if 'quota' in error_msg or 'limit' in error_msg:
                    self.logger.warning(f"API quota/rate limit hit: {e}")
                    # Will add rotation method later
                    time.sleep(self.config.get('api_rate_limit_delay', 3))
                    continue
                    
                elif 'timeout' in error_msg or 'deadline' in error_msg:
                    self.logger.warning(f"Ultra-technical timeout error: {e}")
                    timeout_delay = min(7 * (attempt + 1), 35)
                    time.sleep(timeout_delay)
                    continue
                    
                else:
                    self.logger.warning(f"Ultra-technical API call failed: {e}")
                    if attempt < max_retries - 1:
                        delay = min(3 ** attempt + random.uniform(0, 2), 20)
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"All retry attempts failed for ultra-technical processing")
                        return None
        
        return None

    def _process_single_pdf(self, pdf_path: Path) -> bool:
        """Process single PDF for ultra-technical content."""
        try:
            self.logger.info(f"🧬 Ultra-technical processing: {pdf_path.name}")
            
            text_content, images = self._extract_pdf_content(pdf_path)
            
            if not text_content.strip():
                self.logger.warning(f"No text content for ultra-technical processing: {pdf_path.name}")
                return False
            
            # Larger chunks for ultra-technical content
            chunk_size = 60000  # Increased for technical content
            text_chunks = []
            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                text_chunks.append(chunk)
            
            images_per_chunk = max(1, len(images) // len(text_chunks)) if images else 0
            
            self.logger.info(f"🧬 Ultra-technical split {pdf_path.name} into {len(text_chunks)} chunks")
            
            all_qa_pairs = []
            
            for chunk_idx, text_chunk in enumerate(text_chunks):
                self.logger.info(f"🧬 Ultra-technical chunk {chunk_idx + 1}/{len(text_chunks)} of {pdf_path.name}")
                
                start_img = chunk_idx * images_per_chunk
                end_img = min((chunk_idx + 1) * images_per_chunk, len(images))
                chunk_images = images[start_img:end_img] if images else []
                
                qa_pairs = self._call_gemini_api(text_chunk, chunk_images)
                
                if qa_pairs:
                    all_qa_pairs.extend(qa_pairs)
                    self.logger.info(f"🧬 Ultra-technical chunk {chunk_idx + 1}: Generated {len(qa_pairs)} Q&A pairs")
                else:
                    self.logger.warning(f"Failed ultra-technical generation for chunk {chunk_idx + 1}")
                
                # Extended delay for ultra-technical processing
                if chunk_idx < len(text_chunks) - 1:
                    chunk_delay = 7  # Fixed delay for stability
                    self.logger.info(f"Ultra-technical delay {chunk_delay}s before next chunk...")
                    time.sleep(chunk_delay)
            
            if not all_qa_pairs:
                self.logger.error(f"Failed to generate ultra-technical Q&A pairs for {pdf_path.name}")
                return False
            
            # Save ultra-technical output
            output_file = Path(self.config['pdf_processing']['output_folder']) / self.config['pdf_processing']['output_filename']
            
            with open(output_file, 'a', encoding='utf-8') as f:
                for qa_pair in all_qa_pairs:
                    output_data = {
                        "soru": qa_pair["soru"],
                        "cevap": qa_pair["cevap"]
                    }
                    f.write(json.dumps(output_data, ensure_ascii=False) + '\n')
            
            self.logger.info(f"🧬 Ultra-technical SUCCESS {pdf_path.name}: {len(all_qa_pairs)} expert Q&A pairs from {len(text_chunks)} chunks")
            return True
            
        except Exception as e:
            self.logger.error(f"Ultra-technical error processing {pdf_path.name}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

    def _get_pdf_files(self) -> List[Path]:
        """Get PDF files for ultra-technical processing."""
        pdf_folder = Path(self._get_config_value('pdf_processing.pdf_folder', 'pdfs'))
        
        if not pdf_folder.exists():
            raise FileNotFoundError(f"PDF folder not found: {pdf_folder}")
        
        pdf_files = list(pdf_folder.glob('*.pdf'))
        
        unprocessed_files = [
            pdf for pdf in pdf_files 
            if pdf.name not in self.processed_files
        ]
        
        self.logger.info(f"Found {len(pdf_files)} total PDF files")
        self.logger.info(f"Found {len(unprocessed_files)} unprocessed files for ultra-technical processing")
        
        return unprocessed_files

    def run(self):
        """Main ultra-technical execution method."""
        try:
            self.logger.info("🧬 Starting ultra-technical dietitian Q&A dataset generation")
            
            pdf_files = self._get_pdf_files()
            
            if not pdf_files:
                self.logger.info("No unprocessed PDF files found for ultra-technical processing.")
                return
            
            successful_count = 0
            failed_count = 0
            
            # Sequential processing for ultra-technical content (more careful)
            for pdf_path in pdf_files:
                try:
                    success = self._process_single_pdf(pdf_path)
                    if success:
                        successful_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error(f"Unexpected ultra-technical error processing {pdf_path.name}: {e}")
                    failed_count += 1
                
                # Longer break between files for ultra-technical processing
                if pdf_path != pdf_files[-1]:  # Not the last file
                    inter_file_delay = 8
                    self.logger.info(f"Inter-file delay: {inter_file_delay}s for API stability...")
                    time.sleep(inter_file_delay)
            
            total_processed = successful_count + failed_count
            self.logger.info(f"🧬 Ultra-technical processing completed!")
            self.logger.info(f"Total files processed: {total_processed}")
            self.logger.info(f"Successful: {successful_count}")
            self.logger.info(f"Failed: {failed_count}")
            
            if successful_count > 0:
                output_path = Path(self._get_config_value('pdf_processing.output_folder', 'ultra_technical_output')) / self._get_config_value('pdf_processing.output_filename', 'ultra_technical_dietitian_dataset.jsonl')
                self.logger.info(f"🧬 Ultra-technical output saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Fatal ultra-technical error: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise


def main():
    """Main entry point for ultra-technical dietitian processor."""
    parser = argparse.ArgumentParser(
        description="Generate ultra-technical dietitian Q&A datasets from PDF files"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        processor = UltraTechnicalDietitianProcessor(config_path=args.config)
        processor.run()
    except KeyboardInterrupt:
        print("\n🧬 Ultra-technical operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal ultra-technical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 