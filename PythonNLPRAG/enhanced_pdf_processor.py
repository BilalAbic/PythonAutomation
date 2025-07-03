#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe PDF to Q&A Dataset Generator
Enhanced PDF processing system for ML training data generation
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
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image
import io

# Import working modules
from pdf_api_manager import APIKeyManager

class UltraSafePDFProcessor:
    """Ultra güvenli PDF işleme sistemi - ML eğitimi için optimize edilmiş"""
    
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
            'start_time': datetime.now().isoformat(),
            'categories_distribution': {},
            'difficulty_distribution': {},
            'avg_quality_score': 0.0
        }
        
        # PDF specific
        self.processed_files = self._get_already_processed_files()
        
        self.logger.info("🛡️ Ultra Safe PDF Processor hazır!")
        
    def load_and_validate_config(self, config_path: str):
        """Enhanced config loading with validation"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Basic validation
            required_keys = ['api_keys', 'pdf_folder', 'output_folder', 'output_filename']
            for key in required_keys:
                if key not in self.config:
                    raise ValueError(f"Missing required config key: {key}")
                    
            # Config dosyası bilgilerini sakla
            self.config_file_path = config_path
            self.config_last_modified = os.path.getmtime(config_path)
                
        except Exception as e:
            print(f"❌ Config hatası: {e}")
            sys.exit(1)
            
    def setup_logging(self):
        """Enhanced logging system"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/enhanced_pdf_processor_{datetime.now().strftime("%Y%m%d_%H%M")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def setup_core_systems(self):
        """Core systems setup"""
        # Create necessary directories
        os.makedirs('checkpoints', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs(self.config.get('output_folder', 'output_json'), exist_ok=True)
        
        # Emergency stop file
        self.emergency_stop_file = 'EMERGENCY_STOP_PDF'
        if os.path.exists(self.emergency_stop_file):
            os.remove(self.emergency_stop_file)
            
        self.logger.info("🛡️ Core systems initialized")
            
    def setup_apis(self):
        """API systems setup"""
        self.api_manager = APIKeyManager(self.config['api_keys'], self.logger)
        
        # Test all keys
        active_count = self.api_manager.test_all_keys()
        
        if active_count == 0:
            raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            
        self.logger.info(f"✅ {active_count}/{len(self.config['api_keys'])} API key aktif")
        
        if active_count < 3:
            self.logger.warning(f"⚠️ Sadece {active_count} API key aktif. İşlem yavaş olabilir.")
        
    def setup_signal_handlers(self):
        """Signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.warning(f"Signal {signum} alındı. Güvenli shutdown...")
            self.emergency_shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def _get_already_processed_files(self) -> Set[str]:
        """Get already processed files from checkpoint"""
        try:
            with open('checkpoints/processed_files.json', 'r') as f:
                return set(json.load(f))
        except:
            return set()

    def create_ml_optimized_prompt(self) -> str:
        """ML training için optimize edilmiş prompt"""
        max_questions = self.config.get('max_questions_per_pdf', 20)
        
        return f"""
Sen, makine öğrenmesi modelleri için profesyonel seviyede eğitim verisi üreten uzman bir AI sistemisin.

**GÖREV**: PDF içeriğini analiz ederek, farklı kategorilerde ve zorluk seviyelerinde yüksek kaliteli soru-cevap çiftleri üret.

**KATEGORİLER** (Her kategoriden minimum 2 soru):
1. **Faktuel Bilgi**: Tanımlar, sayısal veriler, spesifik bilgiler
2. **Kavramsal Anlama**: Açıklamalar, sebep-sonuç ilişkileri, karşılaştırmalar
3. **Analitik Düşünme**: Çıkarımlar, analizler, değerlendirmeler
4. **Uygulama**: Pratik kullanım, örnekler, problem çözme
5. **Eleştirel Değerlendirme**: Avantaj-dezavantajlar, kritik değerlendirme

**ZORLUK SEVİYELERİ**:
- **Temel**: Doğrudan metinden alınabilir (30%)
- **Orta**: Hafif çıkarım gerektirir (50%)
- **İleri**: Derin analiz gerektirir (20%)

**KALİTE KURALLARI**:
✅ Sorular 20-150 karakter, net ve spesifik
✅ Cevaplar 100-400 kelime, detaylı ve yapılandırılmış
✅ Bilimsel doğruluk ve kesinlik
✅ Örneklerle desteklenmiş açıklamalar
✅ Belirsiz ifadeler yasak ("muhtemelen", "genellikle")
✅ Tablo/şekil referansları yasak

**ÇIKTI FORMATI** (Kesinlikle bu format):
```json
[
  {{
    "soru": "Açık ve spesifik soru metni",
    "cevap": "Detaylı, yapılandırılmış cevap (100-400 kelime)",
    "kategori": "Faktuel Bilgi",
    "zorluk": "Temel",
    "anahtar_kelimeler": ["anahtar1", "anahtar2", "anahtar3"],
    "kaynak_tipi": "metin"
  }}
]
```

**HEDEF**: {max_questions} adet benzersiz, yüksek kaliteli soru-cevap çifti üret.
Her soru farklı bir açıdan konuyu ele almalı.
"""

    def validate_qa_quality(self, qa_data: Dict) -> Tuple[bool, int, List[str]]:
        """Q&A kalitesini değerlendir"""
        quality_score = 0
        issues = []
        
        if not isinstance(qa_data, dict):
            return False, 0, ["Invalid format"]
            
        # Required fields check
        required_fields = ['soru', 'cevap', 'kategori', 'zorluk', 'anahtar_kelimeler', 'kaynak_tipi']
        missing_fields = [f for f in required_fields if f not in qa_data]
        if missing_fields:
            return False, 0, [f"Missing fields: {missing_fields}"]
        
        question = qa_data['soru'].strip()
        answer = qa_data['cevap'].strip()
        
        # Length checks
        if 20 <= len(question) <= 150:
            quality_score += 15
        else:
            issues.append(f"Question length issue: {len(question)} chars")
            
        word_count = len(answer.split())
        if 100 <= len(answer) <= 1600 and word_count >= 15:  # Character and word count
            quality_score += 25
        else:
            issues.append(f"Answer length issue: {len(answer)} chars, {word_count} words")
        
        # Content quality checks
        forbidden_patterns = [
            r'tablo\s*\d+', r'şekil\s*\d+', r'grafik\s*\d+',
            r'yukarıdaki\s+(tablo|şekil|grafik)', r'aşağıdaki\s+(tablo|şekil|grafik)'
        ]
        
        full_text = (question + " " + answer).lower()
        if not any(re.search(pattern, full_text) for pattern in forbidden_patterns):
            quality_score += 20
        else:
            issues.append("Contains forbidden table/figure references")
        
        # Category validation
        valid_categories = ['Faktuel Bilgi', 'Kavramsal Anlama', 'Analitik Düşünme', 'Uygulama', 'Eleştirel Değerlendirme']
        if qa_data['kategori'] in valid_categories:
            quality_score += 10
        else:
            issues.append(f"Invalid category: {qa_data['kategori']}")
        
        # Difficulty validation
        valid_difficulties = ['Temel', 'Orta', 'İleri']
        if qa_data['zorluk'] in valid_difficulties:
            quality_score += 10
        else:
            issues.append(f"Invalid difficulty: {qa_data['zorluk']}")
        
        # Keywords validation
        keywords = qa_data.get('anahtar_kelimeler', [])
        if isinstance(keywords, list) and len(keywords) >= 2:
            quality_score += 10
        else:
            issues.append("Insufficient keywords")
        
        # Vague language check
        vague_patterns = ['muhtemelen', 'sanırım', 'galiba', 'belki', 'çoğunlukla', 'genellikle']
        vague_count = sum(1 for pattern in vague_patterns if pattern in answer.lower())
        if vague_count == 0:
            quality_score += 10
        elif vague_count > 2:
            issues.append(f"Too much vague language: {vague_count}")
        
        return quality_score >= 70, quality_score, issues

    async def process_with_gemini(self, text_content: str, images: List[bytes]) -> Optional[List[Dict]]:
        """Enhanced Gemini API processing"""
        start_time = time.time()
        
        try:
            # Get best model
            model_info = self.api_manager.get_best_model()
            if not model_info:
                self.logger.error("No available API models")
                return None
            
            model = model_info['model']
            prompt = self.create_ml_optimized_prompt()
            
            # Prepare content
            content_parts = [prompt, text_content]
            
            # Add images (limit to 5 for performance)
            for i, img_data in enumerate(images[:5]):
                try:
                    pil_img = Image.open(io.BytesIO(img_data))
                    content_parts.append(pil_img)
                except Exception as e:
                    self.logger.warning(f"Image {i} processing failed: {e}")
            
            # Generate response
            response = model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=8192,
                    temperature=0.1
                )
            )
            
            if not response.text:
                self.api_manager.record_failure(model_info)
                return None
            
            # Parse and validate response
            try:
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                qa_pairs = json.loads(response_text)
                
                if not isinstance(qa_pairs, list):
                    self.logger.warning("Response is not a JSON array")
                    return None
                
                # Validate each Q&A pair
                valid_pairs = []
                for qa in qa_pairs:
                    is_valid, score, issues = self.validate_qa_quality(qa)
                    
                    if is_valid:
                        # Add metadata for ML training
                        qa['kalite_skoru'] = score
                        qa['kelime_sayisi'] = len(qa['cevap'].split())
                        qa['karakter_sayisi'] = len(qa['cevap'])
                        valid_pairs.append(qa)
                        
                        # Update stats
                        category = qa.get('kategori', 'Unknown')
                        difficulty = qa.get('zorluk', 'Unknown')
                        self.stats['categories_distribution'][category] = self.stats['categories_distribution'].get(category, 0) + 1
                        self.stats['difficulty_distribution'][difficulty] = self.stats['difficulty_distribution'].get(difficulty, 0) + 1
                    else:
                        self.logger.warning(f"Q&A rejected (score: {score}): {' | '.join(issues)}")
                
                if valid_pairs:
                    self.api_manager.record_success(model_info)
                    
                    # Calculate average quality score
                    if self.stats['total_questions_generated'] > 0:
                        self.stats['avg_quality_score'] = (
                            self.stats['avg_quality_score'] * self.stats['total_questions_generated'] + 
                            sum(qa['kalite_skoru'] for qa in valid_pairs)
                        ) / (self.stats['total_questions_generated'] + len(valid_pairs))
                    else:
                        self.stats['avg_quality_score'] = sum(qa['kalite_skoru'] for qa in valid_pairs) / len(valid_pairs)
                    
                    self.stats['total_questions_generated'] += len(valid_pairs)
                    
                    self.logger.info(f"Generated {len(valid_pairs)} quality Q&A pairs in {time.time() - start_time:.2f}s")
                    return valid_pairs
                else:
                    self.logger.warning("No valid Q&A pairs after quality filtering")
                    return None
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed: {e}")
                self.api_manager.record_failure(model_info)
                return None
                
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            if model_info:
                self.api_manager.record_failure(model_info)
            return None
            
    def check_emergency_stop(self) -> bool:
        """Emergency stop check"""
        # This method is no longer needed as safety monitoring is removed.
        # Keeping it for now, but it will always return False.
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
        """Checkpoint save"""
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
        """Progress report"""
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
        
    def extract_pdf_content(self, pdf_path: Path) -> Tuple[str, List[bytes]]:
        """PDF içeriğini çıkar - enhanced version"""
        try:
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
            if len(text_content.strip()) < 100:
                raise ValueError("Çıkarılan içerik çok kısa")
                
            self.logger.info(f"📄 {pdf_path.name}: {len(text_content)} karakter, {len(images)} resim")
            return text_content, images
            
        except Exception as e:
            self.logger.error(f"PDF content extraction hatası: {e}")
            raise

    async def process_single_pdf(self, pdf_path: Path) -> bool:
        """Tek PDF işleme - enhanced version"""
        try:
            # Skip if already processed
            if str(pdf_path) in self.processed_files:
                self.logger.info(f"⏭️ Atlanıyor (işlenmiş): {pdf_path.name}")
                return True
                
            self.logger.info(f"📄 PDF işleniyor: {pdf_path.name}")
            
            # Extract content
            text_content, images = self.extract_pdf_content(pdf_path)
            
            # Process with Gemini
            qa_pairs = await self.process_with_gemini(text_content, images)
            
            if not qa_pairs:
                self.logger.warning(f"❌ {pdf_path.name}: Soru-cevap üretilemedi")
                return False
                
            # Save results (Enhanced JSONL format)
            output_file = Path(self.config['output_folder']) / self.config['output_filename']
            
            with open(output_file, 'a', encoding='utf-8') as f:
                for qa in qa_pairs:
                    # Enhanced ML training format
                    ml_format = {
                        'soru': qa['soru'],
                        'cevap': qa['cevap'],
                        'kategori': qa['kategori'],
                        'zorluk': qa['zorluk'],
                        'anahtar_kelimeler': qa['anahtar_kelimeler'],
                        'kaynak_tipi': qa['kaynak_tipi'],
                        'kalite_skoru': qa['kalite_skoru'],
                        'kelime_sayisi': qa['kelime_sayisi'],
                        'karakter_sayisi': qa['karakter_sayisi'],
                        'kaynak_dosya': pdf_path.stem,
                        'uretim_tarihi': datetime.now().isoformat(),
                        'model_versiyonu': self.config.get('model_name', 'gemini-1.5-flash-latest'),
                        'processor_version': '3.0_enhanced_ml'
                    }
                    
                    f.write(json.dumps(ml_format, ensure_ascii=False) + '\n')
                     
            # Update stats
            self.stats['total_pdfs_processed'] += 1
            
            # Mark as processed
            self.processed_files.add(str(pdf_path))
            
            self.logger.info(f"✅ {pdf_path.name}: {len(qa_pairs)} soru üretildi")
            return True
                 
        except Exception as e:
            self.logger.error(f"❌ PDF işleme hatası {pdf_path.name}: {e}")
            self.stats['failed_pages'] += 1
            return False

    async def save_final_results(self):
        """Final results kaydet - cleaned version"""
        os.makedirs('output', exist_ok=True)
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.stats['start_time'])
        
        final_report = {
            "timestamp": end_time.isoformat(),
            "processing_duration": str(end_time - start_time),
            "summary": {
                "total_pdfs": self.stats['total_pdfs_processed'],
                "total_questions": self.stats['total_questions_generated'],
                "success_rate": round(
                    self.stats['successful_pages'] / 
                    max(self.stats['successful_pages'] + self.stats['failed_pages'], 1) * 100),
                "avg_quality_score": round(self.stats['avg_quality_score'], 2),
                "categories_distribution": self.stats['categories_distribution'],
                "difficulty_distribution": self.stats['difficulty_distribution']
            },
            "detailed_stats": self.stats,
            "api_status": self.api_manager.get_status_report(),
            "processed_files": list(self.processed_files)
        }
        
        # Save comprehensive report
        with open('output/enhanced_processing_report.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
            
        self.logger.info("📊 Final rapor kaydedildi: output/enhanced_processing_report.json")

    async def process_all_pdfs(self):
        """Tüm PDF'leri işle - enhanced main function"""
        try:
            self.logger.info("🚀 Enhanced PDF Processing başlatıldı")
            
            # PDF dosyalarını bul
            pdf_folder = Path(self.config['pdf_folder'])
            pdf_files = list(pdf_folder.glob('*.pdf'))
            
            if not pdf_files:
                self.logger.warning(f"❌ {pdf_folder} klasöründe PDF bulunamadı!")
                return
                
            self.logger.info(f"📁 {len(pdf_files)} PDF dosyası bulundu")
            
            successful_count = 0
            failed_count = 0
            
            for i, pdf_path in enumerate(pdf_files):
                self.logger.info(f"📊 Progress: {i+1}/{len(pdf_files)} - {pdf_path.name}")
                
                # Process PDF
                success = await self.process_single_pdf(pdf_path)
                
                if success:
                    successful_count += 1
                else:
                    failed_count += 1
                
                # Checkpoint (her 10 dosyada bir)
                if (i + 1) % 10 == 0:
                    self.save_checkpoint()
                    
                # Memory cleanup
                if (i + 1) % 5 == 0:
                    gc.collect()
                    self.print_progress_report()
                    
                # Rate limiting between files
                await asyncio.sleep(2)
                     
            # Final stats update
            self.stats['successful_pages'] = successful_count
            self.stats['failed_pages'] = failed_count
            
            # Save final results
            await self.save_final_results()
            
            self.logger.info(f"""
🎉 === ENHANCED PDF İŞLEME TAMAMLANDI! ===
📄 İşlenen PDF: {successful_count}
❌ Başarısız: {failed_count}
❓ Toplam soru: {self.stats['total_questions_generated']}
⭐ Ortalama kalite: {self.stats['avg_quality_score']:.1f}
📈 Başarı oranı: %{(successful_count/(successful_count+failed_count)*100) if (successful_count+failed_count) > 0 else 0:.1f}
📊 Kategori dağılımı: {self.stats['categories_distribution']}
📈 Zorluk dağılımı: {self.stats['difficulty_distribution']}
========================================""")
                  
        except Exception as e:
            self.logger.critical(f"❌ Kritik hata: {e}")
            self.emergency_shutdown()
            raise

# Main function
async def main():
    """Enhanced main function"""
    try:
        processor = UltraSafePDFProcessor()
        await processor.process_all_pdfs()
    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        
if __name__ == "__main__":
    asyncio.run(main()) 