#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe PDF to Q&A Dataset Generator
DataMin2x tabanlı gelişmiş PDF işleme sistemi
Ana mantığı koruyup güvenlik ve modülerlik eklenmiştir
"""

import json
import time
import asyncio
import logging
import os
import gc
import threading
import signal
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image

# Enhanced modules (DataMin2x'ten uyarlanmış) - TEMPORARILY DISABLED DUE TO MISSING FILES
# from pdf_validators import PDFValidator, QAValidator, TurkishValidator, ContentFilter
# from pdf_safety_monitor import SafetyMonitor, CostTracker, RateLimiter, PerformanceMonitor, AlertSystem
# from pdf_utils import JsonSafeParser, MemoryManager, FileManager, TextProcessor, ProgressTracker, ConfigValidator
from pdf_api_manager import APIKeyManager

class UltraSafePDFProcessor:
    """Ultra güvenli PDF işleme sistemi"""
    
    def __init__(self, config_path="config.json"):
        print("🛡️ Ultra Safe PDF Processor başlatılıyor...")
        
        # Config yükle ve doğrula
        self.load_and_validate_config(config_path)
        
        # Logging sistemi
        self.setup_logging()
        
        # Core componentler
        self.setup_core_systems()
        
        # API sistemleri
        self.setup_apis()
        
        # Signal handlers
        self.setup_signal_handlers()
        
        # Stats
        self.stats = {
            'total_pdfs_processed': 0,
            'total_questions_generated': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'api_failures': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # PDF specific
        self.processed_files = self._get_already_processed_files()
        
        self.logger.info("🛡️ Ultra Safe PDF Processor hazır!")
        
    def load_and_validate_config(self, config_path: str):
        """Config yükle ve doğrula"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Config validation (DataMin2x tarzı)
            validator = ConfigValidator()
            if not validator.validate_pdf_config(self.config):
                raise ValueError("Config doğrulama başarısız")
                
            # Config dosyası bilgilerini sakla (hot reload için)
            self.config_file_path = config_path
            self.config_last_modified = os.path.getmtime(config_path)
                
        except Exception as e:
            print(f"❌ Config hatası: {e}")
            sys.exit(1)
            
    def setup_logging(self):
        """Gelişmiş logging sistemi"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/pdf_processor_{datetime.now().strftime("%Y%m%d_%H%M")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def setup_core_systems(self):
        """Core sistemleri kurulumu"""
        # TEMPORARILY DISABLED - Missing modules
        # Validators
        # self.pdf_validator = PDFValidator()
        # self.qa_validator = QAValidator(self.config)
        # self.turkish_validator = TurkishValidator()
        # self.content_filter = ContentFilter()
        
        # Safety & Monitoring (DataMin2x'ten uyarlanmış)
        # self.safety_monitor = SafetyMonitor(self.config)
        # self.cost_tracker = CostTracker()
        # self.rate_limiter = RateLimiter(self.config)
        # self.performance_monitor = PerformanceMonitor()
        # self.alert_system = AlertSystem()
        
        # Utilities
        # self.json_parser = JsonSafeParser()
        # self.memory_manager = MemoryManager()
        # self.file_manager = FileManager(self.config)
        # self.text_processor = TextProcessor()
        # self.progress_tracker = ProgressTracker()
        
        # Emergency stop file
        self.emergency_stop_file = 'EMERGENCY_STOP_PDF'
        if os.path.exists(self.emergency_stop_file):
            os.remove(self.emergency_stop_file)
            
    def setup_apis(self):
        """API sistemleri kurulumu"""
        self.api_manager = APIKeyManager(self.config['api_keys'], self.logger)
        
        # Test all keys
        active_count = self.api_manager.test_all_keys()
        
        if active_count == 0:
            raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            
        self.logger.info(f"✅ {active_count}/{len(self.config['api_keys'])} API key aktif")
        
        # Düşük API key sayısı uyarısı
        if active_count < 5:
            self.logger.warning(f"⚠️ Sadece {active_count} API key aktif. İşlem yavaş olabilir.")
        
    def setup_signal_handlers(self):
        """Signal handlers - graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.warning(f"Signal {signum} alındı. Güvenli shutdown...")
            self.emergency_shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def _get_already_processed_files(self) -> Set[str]:
        """İşlenmiş dosyaları checkpoint'ten al"""
        try:
            with open('checkpoints/processed_files.json', 'r') as f:
                return set(json.load(f))
        except:
            return set()
            
    def check_config_changes(self) -> bool:
        """Config dosyasında değişiklik var mı kontrol et"""
        try:
            if not hasattr(self, 'config_file_path'):
                return False
                
            current_modified = os.path.getmtime(self.config_file_path)
            if current_modified > self.config_last_modified:
                self.logger.info("🔄 Config dosyasında değişiklik tespit edildi")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Config change check hatası: {e}")
            return False
            
    def reload_config_and_apis(self):
        """Config'i reload et ve API keyleri güncelle"""
        try:
            self.logger.info("🔄 Config reload başlıyor...")
            
            # Config'i yeniden yükle
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            
            # Config validation
            validator = ConfigValidator()
            if not validator.validate_pdf_config(new_config):
                self.logger.error("❌ Yeni config validation başarısız")
                return False
            
            # API keylerini güncelle
            old_key_count = len(self.api_manager.healthy_models)
            
            self.api_manager.update_api_keys(new_config['api_keys'])
            new_key_count = len(self.api_manager.healthy_models)
            
            self.config = new_config
            self.config_last_modified = os.path.getmtime(self.config_file_path)
            
            if new_key_count != old_key_count:
                self.logger.info(f"🔄 API key güncelleme: {old_key_count} ➜ {new_key_count}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Config reload hatası: {e}")
            return False
            
    def extract_pdf_content(self, pdf_path: Path) -> Tuple[str, List[bytes]]:
        """PDF içeriğini çıkar (orijinal mantık)"""
        try:
            # PDF validation
            if not self.pdf_validator.validate_pdf_file(pdf_path):
                raise ValueError(f"PDF validation başarısız: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            text_content = ""
            images = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Text extraction
                page_text = page.get_text()
                if page_text.strip():
                    text_content += f"\n--- Sayfa {page_num + 1} ---\n"
                    text_content += page_text
                    
                # Image extraction (eğer config'de aktifse)
                if self.config.get('extract_images', False):
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            if pix.n - pix.alpha < 4:  # GRAY or RGB
                                img_data = pix.tobytes("png")
                                images.append(img_data)
                            pix = None
                        except:
                            continue
                            
            doc.close()
            
            # Content validation
            if not self.pdf_validator.validate_extracted_content(text_content):
                raise ValueError("Çıkarılan içerik çok kısa veya geçersiz")
                
            self.logger.debug(f"📄 {pdf_path.name}: {len(text_content)} karakter, {len(images)} resim")
            return text_content, images
            
        except Exception as e:
            self.logger.error(f"PDF content extraction hatası: {e}")
            raise
            
    def create_pdf_prompt(self) -> str:
        """PDF için özelleştirilmiş prompt (orijinal mantık iyileştirilmiş)"""
        return """PDF içeriğinden Türkçe soru-cevap çiftleri oluşturun.

KRİTİK KURALLAR:
📚 PDF içeriğine sadık kalın
🇹🇷 Türkçe dil bilgisi kurallarına uyun
📝 Net ve anlaşılır sorular oluşturun
✅ Tam ve doğru cevaplar verin
⚠️ Yanlış bilgi vermeyin

ÇIKTI FORMATI (ZORUNLU):
```json
{
  "questions": [
    {
      "question": "Soru metni burada?",
      "answer": "Cevap metni burada.",
      "page_reference": "sayfa numarası",
      "confidence": 0.95
    }
  ]
}
```

PDF İÇERİĞİ:
{content}

Sadece JSON yanıtı verin!"""
        
    async def process_with_gemini(self, text_content: str, images: List[bytes]) -> Optional[List[Dict]]:
        """Gemini API ile işleme (güvenli)"""
        start_time = time.time()
        
        for attempt in range(self.config.get('max_retries', 3)):
            try:
                # Emergency stop check
                self.check_emergency_stop()
                
                # Memory check
                self.memory_manager.check_memory_usage()
                
                # Rate limiting
                await self.rate_limiter.wait_if_needed()
                
                # API key selection
                model_info = self.api_manager.get_best_model()
                if not model_info:
                    raise RuntimeError("Kullanılabilir API key kalmadı!")
                
                # Create prompt
                prompt = self.create_pdf_prompt().format(content=text_content[:8000])  # Token limit
                
                self.logger.debug(f"Gemini API call başlatılıyor (Deneme: {attempt+1})")
                
                # API call
                api_start = time.time()
                response = model_info['model'].generate_content(prompt)
                api_time = time.time() - api_start
                
                # Response kontrolü
                if not response or not hasattr(response, 'text'):
                    raise Exception("API response objesi geçersiz")
                
                response_text = response.text
                if not response_text or response_text.strip() == "":
                    raise Exception("Boş response")
                    
                # JSON parse (güvenli)
                parsed_data = self.json_parser.safe_parse(response_text)
                if not parsed_data or 'questions' not in parsed_data:
                    raise Exception("JSON parse başarısız veya geçersiz format")
                
                # Validation
                questions = parsed_data['questions']
                validated_questions = []
                
                for q in questions:
                    if self.qa_validator.validate_qa_pair(q):
                        if self.turkish_validator.validate(q):
                            if self.content_filter.filter_content(q):
                                validated_questions.append(q)
                
                # Success metrics
                self.api_manager.record_success(model_info)
                self.stats['successful_pages'] += 1
                self.rate_limiter.record_success()
                self.performance_monitor.record_api_time(api_time)
                
                self.logger.debug(f"✅ Gemini başarılı: {len(validated_questions)} soru")
                return validated_questions
                
            except Exception as e:
                error_str = str(e)
                
                # Quota hatalarını özel olarak işle
                if "quota" in error_str.lower() or "429" in error_str:
                    self.logger.warning(f"Quota hatası (Deneme {attempt+1}): {e}")
                    if 'model_info' in locals():
                        self.api_manager.mark_quota_exceeded(model_info)
                else:
                    self.logger.error(f"Gemini hatası (Deneme {attempt+1}): {e}")
                
                if 'model_info' in locals():
                    self.api_manager.record_failure(model_info)
                
                self.stats['failed_pages'] += 1
                self.rate_limiter.record_failure()
                self.safety_monitor.record_failure("gemini_api", str(e))
                
                # Exponential backoff
                wait_time = (2 ** attempt) * 2
                await asyncio.sleep(wait_time)
                
        # All attempts failed
        self.logger.error(f"Gemini API kalıcı başarısız")
        return None
        
    async def process_single_pdf(self, pdf_path: Path) -> bool:
        """Tek PDF işleme (enhanced)"""
        try:
            # Skip if already processed
            if str(pdf_path) in self.processed_files:
                self.logger.info(f"⏭️ Atlanıyor (işlenmiş): {pdf_path.name}")
                return True
                
            self.logger.info(f"📄 PDF işleniyor: {pdf_path.name}")
            
            # Extract content
            text_content, images = self.extract_pdf_content(pdf_path)
            
            # Process with Gemini
            questions = await self.process_with_gemini(text_content, images)
            
            if not questions:
                return False
                
            # Save results (JSONL format)
            output_file = Path(self.config['output_folder']) / self.config['output_filename']
            
            with open(output_file, 'a', encoding='utf-8') as f:
                for q in questions:
                    # Add metadata
                    q.update({
                        'source_file': pdf_path.name,
                        'timestamp': datetime.now().isoformat(),
                        'processor_version': '2.0_ultra_safe'
                    })
                    
                    # Write JSONL line
                    f.write(json.dumps(q, ensure_ascii=False) + '\n')
                    
            # Update stats
            self.stats['total_pdfs_processed'] += 1
            self.stats['total_questions_generated'] += len(questions)
            
            # Mark as processed
            self.processed_files.add(str(pdf_path))
            
            self.logger.info(f"✅ {pdf_path.name}: {len(questions)} soru üretildi")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ PDF işleme hatası {pdf_path.name}: {e}")
            return False
            
    def check_emergency_stop(self) -> bool:
        """Emergency stop kontrolü"""
        if self.safety_monitor.should_emergency_stop(self.stats):
            self.logger.critical("🚨 Safety monitor emergency stop!")
            with open(self.emergency_stop_file, 'w') as f:
                f.write(f"Emergency stop: {datetime.now().isoformat()}")
            
            self.emergency_shutdown()
            raise SystemExit("Emergency stop triggered by safety monitor")
            
        return False
        
    def emergency_shutdown(self):
        """Emergency shutdown"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN!")
        
        # Save emergency data
        emergency_data = {
            "shutdown_time": datetime.now().isoformat(),
            "stats": self.stats,
            "processed_files": list(self.processed_files),
            "reason": "Emergency shutdown"
        }
        
        with open('emergency_shutdown_pdf.json', 'w', encoding='utf-8') as f:
            json.dump(emergency_data, f, ensure_ascii=False, indent=2)
            
    def save_checkpoint(self):
        """Checkpoint kaydet"""
        checkpoint = {
            "processed_files": list(self.processed_files),
            "stats": self.stats.copy(),
            "timestamp": datetime.now().isoformat()
        }
        
        os.makedirs('checkpoints', exist_ok=True)
        with open('checkpoints/processed_files.json', 'w', encoding='utf-8') as f:
            json.dump(list(self.processed_files), f, ensure_ascii=False, indent=2)
            
        with open('checkpoints/latest_pdf.json', 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
    def print_progress_report(self):
        """Progress raporu"""
        start_time = datetime.fromisoformat(self.stats['start_time'])
        elapsed = datetime.now() - start_time
        
        if self.stats['total_pdfs_processed'] > 0:
            success_rate = (self.stats['successful_pages'] / 
                           max(self.stats['successful_pages'] + self.stats['failed_pages'], 1) * 100)
        else:
            success_rate = 0
        
        self.logger.info(f"""
📊 === PDF İŞLEME RAPORU ===
⏱️  Geçen süre: {elapsed}
📄 İşlenen PDF: {self.stats['total_pdfs_processed']}
❓ Üretilen soru: {self.stats['total_questions_generated']}
✅ Başarılı sayfa: {self.stats['successful_pages']}
❌ Başarısız sayfa: {self.stats['failed_pages']}
📈 Başarı oranı: %{success_rate:.1f}
💰 Maliyet: {self.cost_tracker.get_estimated_cost()}
=========================""")
        
    async def process_all_pdfs(self):
        """Tüm PDF'leri işle (ana fonksiyon)"""
        try:
            self.logger.info("🚀 Ultra Safe PDF Processing başlatıldı")
            
            # PDF dosyalarını bul
            pdf_folder = Path(self.config['pdf_folder'])
            pdf_files = list(pdf_folder.glob('*.pdf'))
            
            if not pdf_files:
                self.logger.warning(f"❌ {pdf_folder} klasöründe PDF bulunamadı!")
                return
                
            self.logger.info(f"📁 {len(pdf_files)} PDF dosyası bulundu")
            
            # Progress tracker başlat
            self.progress_tracker.update_progress(0, len(pdf_files))
            
            for i, pdf_path in enumerate(pdf_files):
                # Config change kontrolü (her 5 dosyada bir)
                if i % 5 == 0 and self.check_config_changes():
                    self.logger.info("🔄 Config değişikliği tespit edildi, güncelleniyor...")
                    self.reload_config_and_apis()
                
                # Process PDF
                success = await self.process_single_pdf(pdf_path)
                
                # Progress update
                self.progress_tracker.update_progress(i + 1, len(pdf_files))
                
                # Checkpoint (her 10 dosyada bir)
                if (i + 1) % 10 == 0:
                    self.save_checkpoint()
                    
                # Memory cleanup ve monitoring
                if (i + 1) % 5 == 0:
                    gc.collect()
                    self.print_progress_report()
                    
                # Performance monitoring
                self.performance_monitor.take_system_snapshot()
                    
            # Save final results
            await self.save_final_results()
            
        except Exception as e:
            self.logger.critical(f"❌ Kritik hata: {e}")
            self.emergency_shutdown()
            raise
            
    async def save_final_results(self):
        """Final results kaydet"""
        os.makedirs('output', exist_ok=True)
        
        # Final report
        report = {
            "completion_time": datetime.now().isoformat(),
            "total_pdfs_processed": self.stats['total_pdfs_processed'],
            "total_questions_generated": self.stats['total_questions_generated'],
            "successful_pages": self.stats['successful_pages'],
            "failed_pages": self.stats['failed_pages'],
            "success_rate": (self.stats['successful_pages'] / 
                           max(self.stats['successful_pages'] + self.stats['failed_pages'], 1) * 100),
            "stats": self.stats,
            "cost_analysis": self.cost_tracker.get_full_report(),
            "performance_summary": self.performance_monitor.get_performance_summary(),
            "safety_report": self.safety_monitor.generate_safety_report(),
            "processed_files": list(self.processed_files)
        }
        
        with open('output/pdf_processing_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"""
🎉 === PDF İŞLEME TAMAMLANDI! ===
📄 İşlenen PDF: {self.stats['total_pdfs_processed']}
❓ Üretilen soru: {self.stats['total_questions_generated']}
📈 Başarı oranı: %{report['success_rate']:.1f}
💾 Rapor: output/pdf_processing_report.json
========================================""")

# Ana fonksiyon
async def main():
    """Ana fonksiyon"""
    try:
        processor = UltraSafePDFProcessor()
        await processor.process_all_pdfs()
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 