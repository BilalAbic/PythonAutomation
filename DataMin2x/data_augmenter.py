#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe Sağlık Chatbot Veri Çoğaltma Sistemi
12 API Key + Maksimum güvenlik kontrolü
"""

import json
import time
import asyncio
import logging
import os
import gc
import hashlib
import signal
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import google.generativeai as genai

# Import custom modules
from validators import MedicalValidator, DuplicateDetector, CitationPreserver, TurkishValidator, ContentFilter
from safety_monitor import SafetyMonitor, CostTracker, RateLimiter, PerformanceMonitor, AlertSystem
from utils import JsonSafeParser, MemoryManager, FileManager, TextProcessor, ProgressTracker, ConfigValidator

class UltraSafeDataAugmenter:
    """Ultra güvenli veri çoğaltma sistemi"""
    
    def __init__(self, config_path="config.json"):
        print("Ultra Safe Data Augmenter baslatiliyor...")
        
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
            'total_processed': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'duplicates_found': 0,
            'invalid_responses': 0,
            'api_failures': 0,
            'start_time': datetime.now().isoformat()
        }
        
        self.logger.info("Ultra Safe sistem hazır!")
        
    def load_and_validate_config(self, config_path: str):
        """Config yükle ve doğrula"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Config validation
            validator = ConfigValidator()
            if not validator.validate_config(self.config):
                raise ValueError("Config doğrulama başarısız")
                
            # Config dosyası bilgilerini sakla (hot reload için)
            self.config_file_path = config_path
            self.config_last_modified = os.path.getmtime(config_path)
                
        except Exception as e:
            print(f"Config hatasi: {e}")
            sys.exit(1)
            
    def setup_logging(self):
        """Logging sistemi kurulumu"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/ultra_safe_{datetime.now().strftime("%Y%m%d_%H%M")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Validator loggerlarını SILENT yap
        logging.getLogger('validators').setLevel(logging.ERROR)
        logging.getLogger('utils').setLevel(logging.ERROR)
        
        self.logger = logging.getLogger(__name__)
        
    def setup_core_systems(self):
        """Core sistemleri kurulumu"""
        # Validators
        self.medical_validator = MedicalValidator(self.config)
        self.turkish_validator = TurkishValidator()
        self.citation_preserver = CitationPreserver()
        self.duplicate_detector = DuplicateDetector(self.config['safety_settings']['duplicate_threshold'])
        self.content_filter = ContentFilter()
        
        # Safety & Monitoring
        self.safety_monitor = SafetyMonitor(self.config)
        self.cost_tracker = CostTracker()
        self.rate_limiter = RateLimiter(self.config)
        self.performance_monitor = PerformanceMonitor()
        self.alert_system = AlertSystem()
        
        # Utilities
        self.json_parser = JsonSafeParser()
        self.memory_manager = MemoryManager()
        self.file_manager = FileManager(self.config)
        self.text_processor = TextProcessor()
        self.progress_tracker = ProgressTracker()
        
        # Emergency stop file
        self.emergency_stop_file = 'EMERGENCY_STOP'
        if os.path.exists(self.emergency_stop_file):
            os.remove(self.emergency_stop_file)
            
    def setup_apis(self):
        """API sistemleri kurulumu"""
        self.healthy_models = []
        self.failed_models = []
        
        for i, api_key in enumerate(self.config['api_keys']):
            try:
                self.logger.info(f"API Key {i+1} test ediliyor...")
                
                # Configure and test
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Test call
                test_response = model.generate_content("Test")
                if test_response.text:
                    self.healthy_models.append({
                        'model': model,
                        'api_key': api_key[:10] + "...",
                        'index': i,
                        'success_count': 0,
                        'error_count': 0,
                        'last_used': None
                    })
                    self.logger.info(f"API Key {i+1} aktif")
                else:
                    raise Exception("Boş response")
                    
            except Exception as e:
                error_str = str(e)
                if "quota" in error_str.lower() or "429" in error_str:
                    self.logger.warning(f"API Key {i+1} quota aşıldı: {e}")
                else:
                    self.logger.error(f"API Key {i+1} başarısız: {e}")
                self.failed_models.append(i)
                
        if len(self.healthy_models) == 0:
            raise RuntimeError("❌ Hiçbir API key çalışmıyor!")
            
        self.logger.info(f"{len(self.healthy_models)}/{len(self.config['api_keys'])} API key aktif")
        
        # Düşük API key sayısı uyarısı
        if len(self.healthy_models) < 5:
            self.logger.warning(f"⚠️ Sadece {len(self.healthy_models)} API key aktif. İşlem yavaş olabilir.")
        if len(self.healthy_models) < 3:
            self.logger.warning("⚠️ Çok az API key! Rate limiting problemi olabilir.")
        
    def setup_signal_handlers(self):
        """Signal handlers - graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.warning(f"Signal {signum} alındı. Güvenli shutdown...")
            self.emergency_shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def get_best_model(self):
        """En iyi performanslı model seç"""
        if not self.healthy_models:
            self.logger.critical("⚠️ TÜM API KEYLER QUOTA AŞTI!")
            self.logger.critical("🔄 Lütfen bir süre bekleyin veya yeni API keyler ekleyin")
            raise RuntimeError("Kullanılabilir API key kalmadı!")
            
        # Success rate'e göre sırala
        self.healthy_models.sort(key=lambda x: x['success_count'] - x['error_count'], reverse=True)
        
        best_model = self.healthy_models[0]
        best_model['last_used'] = datetime.now().isoformat()
        
        self.logger.debug(f"API Key {best_model['index']+1} seçildi (Success: {best_model['success_count']}, Error: {best_model['error_count']})")
        
        return best_model
        
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
            
            # Eski key sayısını sakla
            old_key_count = len(self.healthy_models)
            old_api_keys = set(model['api_key'] for model in self.healthy_models)
            
            # Config'i yeniden yükle
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            
            # Config validation
            validator = ConfigValidator()
            if not validator.validate_config(new_config):
                self.logger.error("❌ Yeni config validation başarısız")
                return False
            
            # Yeni API keyleri test et
            new_healthy_models = []
            new_failed_models = []
            
            for i, api_key in enumerate(new_config['api_keys']):
                api_key_preview = api_key[:10] + "..."
                
                # Mevcut modellerde var mı kontrol et
                existing_model = None
                for model in self.healthy_models:
                    if model['api_key'] == api_key_preview:
                        existing_model = model
                        break
                
                if existing_model:
                    # Mevcut model'i koru
                    existing_model['index'] = i  # Index güncelle
                    new_healthy_models.append(existing_model)
                    self.logger.debug(f"API Key {i+1} mevcut model korundu")
                else:
                    # Yeni key test et
                    try:
                        self.logger.info(f"🆕 Yeni API Key {i+1} test ediliyor...")
                        
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Test call
                        test_response = model.generate_content("Test")
                        if test_response.text:
                            new_healthy_models.append({
                                'model': model,
                                'api_key': api_key_preview,
                                'index': i,
                                'success_count': 0,
                                'error_count': 0,
                                'last_used': None
                            })
                            self.logger.info(f"✅ Yeni API Key {i+1} eklendi")
                        else:
                            raise Exception("Boş response")
                            
                    except Exception as e:
                        error_str = str(e)
                        if "quota" in error_str.lower() or "429" in error_str:
                            self.logger.warning(f"⚠️ Yeni API Key {i+1} quota aşıldı")
                        else:
                            self.logger.error(f"❌ Yeni API Key {i+1} başarısız: {e}")
                        new_failed_models.append(i)
            
            # Model listelerini güncelle
            self.healthy_models = new_healthy_models
            self.failed_models = new_failed_models
            self.config = new_config
            self.config_last_modified = os.path.getmtime(self.config_file_path)
            
            new_key_count = len(self.healthy_models)
            new_api_keys = set(model['api_key'] for model in self.healthy_models)
            added_keys = len(new_api_keys - old_api_keys)
            
            if added_keys > 0:
                self.logger.info(f"🎉 {added_keys} yeni API key eklendi! Toplam aktif: {new_key_count}")
                
                # Yeni keyleri listele
                for model in self.healthy_models:
                    if model['api_key'] not in old_api_keys:
                        self.logger.info(f"   ➕ Key {model['index']+1}: {model['api_key']}")
                        
            elif new_key_count != old_key_count:
                self.logger.info(f"🔄 Config reload tamamlandı. Aktif keyler: {old_key_count} ➜ {new_key_count}")
            else:
                self.logger.info(f"🔄 Config reload tamamlandı. Aktif keyler: {new_key_count}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Config reload hatası: {e}")
            return False
            
    def _create_fallback_data(self, batch: List[Dict]) -> Optional[Dict]:
        """JSON parse başarısız olduğunda fallback data oluştur"""
        try:
            self.logger.info("Fallback data oluşturuluyor...")
            
            fallback_data = {
                "augmented_data": []
            }
            
            # Her QA için basit varyant oluştur
            for i, qa in enumerate(batch):
                question = qa.get('soru', '')
                answer = qa.get('cevap', '')
                
                # Basit paraphrase dene
                variants = []
                
                # Variant 1: Başına "Doktor," ekle
                if not question.startswith(('Doktor', 'Dr')):
                    variant1 = {
                        'soru': f"Doktor, {question.lower()}",
                        'cevap': answer
                    }
                    variants.append(variant1)
                
                # Variant 2: Sonuna "...hakkında bilgi verir misiniz?" ekle
                if len(question) < 100:
                    base_q = question.rstrip('?').rstrip('.')
                    variant2 = {
                        'soru': f"{base_q} hakkında bilgi verir misiniz?",
                        'cevap': answer
                    }
                    variants.append(variant2)
                
                if variants:
                    fallback_data['augmented_data'].append({
                        'original_id': i + 1,
                        'variants': variants
                    })
            
            if fallback_data['augmented_data']:
                self.logger.info(f"Fallback data oluşturuldu: {len(fallback_data['augmented_data'])} item")
                return fallback_data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Fallback data hatası: {e}")
            return None
        
    def create_ultra_safe_prompt(self, qa_pairs: List[Dict]) -> str:
        """Ultra güvenli prompt oluşturma"""
        prompt = f"""Sağlık alanında chatbot eğitimi için profesyonel veri çoğaltması yapıyoruz.

GÖREV: Aşağıdaki {len(qa_pairs)} soru-cevap çiftinin her biri için 2 farklı varyant oluştur.

KRİTİK KURALLAR:
🏥 Medikal doğruluğu MUTLAKA koru
🔍 [cite: X] referanslarını AYNEN koru  
🇹🇷 Türkçe dil bilgisi kurallarına uy
⚠️ Tehlikeli tavsiyeler verme
🎯 Profesyonel ton kullan
📝 JSON formatında yanıt ver

VARYANT TÜRLERİ:
1. Paraphrasing: Aynı anlam, farklı kelimeler
2. Context variation: Farklı hasta senaryoları

"""
        
        for i, qa in enumerate(qa_pairs, 1):
            prompt += f"""
━━━ {i}. ORİJİNAL ━━━
Soru: {qa['soru']}
Cevap: {qa['cevap'][:400]}{'...' if len(qa['cevap']) > 400 else ''}

"""

        prompt += """
ÇIKTI FORMATI (ZORUNLU):
```json
{
  "augmented_data": [
    {
      "original_id": 1,
      "variants": [
        {"soru": "Paraphrased soru", "cevap": "Paraphrased cevap [cite: X]"},
        {"soru": "Context variation soru", "cevap": "Context variation cevap [cite: X]"}
      ]
    }
  ]
}
```

Sadece JSON yanıtı ver!"""
        return prompt
        
    async def process_batch_ultra_safe(self, batch: List[Dict], batch_id: int) -> Optional[List[Dict]]:
        """Ultra güvenli batch işleme"""
        start_time = time.time()
        
        for attempt in range(self.config['safety_settings']['max_retries']):
            try:
                # Emergency stop check - artık exception fırlatacak
                self.check_emergency_stop()
                
                # Memory check
                self.memory_manager.check_memory_usage()
                
                # Rate limiting
                await self.rate_limiter.wait_if_needed()
                
                # Model selection
                model_info = self.get_best_model()
                
                # Create prompt
                prompt = self.create_ultra_safe_prompt(batch)
                
                # Token check
                estimated_tokens = self.text_processor.estimate_tokens(prompt)
                if estimated_tokens > self.config['safety_settings']['max_tokens_per_request']:
                    self.logger.warning(f"Batch {batch_id} token limiti aşıyor")
                    return await self.split_batch_and_process(batch, batch_id)
                
                self.logger.info(f"Batch {batch_id} isleniyor (Deneme: {attempt+1})")
                
                # API call
                api_start = time.time()
                response = model_info['model'].generate_content(prompt)
                api_time = time.time() - api_start
                
                # Response kontrolü
                if not response or not hasattr(response, 'text'):
                    raise Exception("API response objesi geçersiz")
                
                response_text = response.text
                if not response_text or response_text.strip() == "":
                    self.logger.warning(f"Batch {batch_id} boş response alındı")
                    raise Exception("Boş response")
                
                # Response debugging
                self.logger.debug(f"Response length: {len(response_text)}")
                self.logger.debug(f"Response preview: {response_text[:100]}...")
                    
                # JSON parse
                parsed_data = self.json_parser.safe_parse(response_text)
                if not parsed_data:
                    self.logger.warning(f"JSON parse başarısız, response: {response_text[:200]}...")
                    # Fallback: basit data oluştur
                    parsed_data = self._create_fallback_data(batch)
                    if not parsed_data:
                        raise Exception("JSON parse ve fallback başarısız")
                    
                # Validation
                validated_data = await self.validate_batch_data(parsed_data, batch)
                
                # Success metrics
                model_info['success_count'] += 1
                self.stats['successful_batches'] += 1
                self.rate_limiter.record_success()
                self.performance_monitor.record_batch_time(time.time() - start_time)
                self.performance_monitor.record_api_time(api_time)
                self.cost_tracker.track_request(len(batch), estimated_tokens)
                
                self.logger.info(f"Batch {batch_id} başarılı ({len(validated_data)} varyant)")
                return validated_data
                
            except Exception as e:
                error_str = str(e)
                
                # Quota hatalarını özel olarak işle
                if "quota" in error_str.lower() or "429" in error_str:
                    self.logger.warning(f"Batch {batch_id} quota hatası (Deneme {attempt+1}): {e}")
                    if 'model_info' in locals():
                        self.healthy_models.remove(model_info)
                        self.logger.warning(f"API Key {model_info['index']+1} quota aşıldı, devre dışı")
                else:
                    self.logger.error(f"Batch {batch_id} hatası (Deneme {attempt+1}): {e}")
                
                if 'model_info' in locals() and "quota" not in error_str.lower():
                    model_info['error_count'] += 1
                    if model_info['error_count'] > 5:
                        if model_info in self.healthy_models:
                            self.healthy_models.remove(model_info)
                            self.logger.warning(f"API Key {model_info['index']+1} çok fazla hata, devre dışı")
                
                self.stats['failed_batches'] += 1
                self.rate_limiter.record_failure()
                self.safety_monitor.record_failure("batch_processing", str(e))
                
                # Exponential backoff
                wait_time = (2 ** attempt) * 2
                await asyncio.sleep(wait_time)
                
        # All attempts failed
        self.logger.error(f"Batch {batch_id} kalici basarisiz")
        return None
        
    async def validate_batch_data(self, parsed_data: Dict, original_batch: List[Dict]) -> List[Dict]:
        """Batch veri doğrulama"""
        validated_results = []
        
        augmented_data = parsed_data.get('augmented_data', [])
        
        for i, item in enumerate(augmented_data):
            if i >= len(original_batch):
                break
                
            original_qa = original_batch[i]
            variants = item.get('variants', [])
            
            for variant in variants:
                # Medical validation
                if not self.medical_validator.validate_medical_content(variant):
                    self.stats['invalid_responses'] += 1
                    continue
                    
                # Turkish validation
                if not self.turkish_validator.validate(variant):
                    continue
                    
                # Content filter
                if not self.content_filter.filter_content(variant):
                    continue
                    
                # Citation preservation
                variant = self.citation_preserver.preserve_citations(original_qa['cevap'], variant)
                
                # Duplicate check
                if not self.duplicate_detector.is_duplicate(variant):
                    validated_results.append(variant)
                    self.duplicate_detector.add_to_database(variant)
                else:
                    self.stats['duplicates_found'] += 1
                    
        return validated_results
        
    async def split_batch_and_process(self, batch: List[Dict], batch_id: int) -> List[Dict]:
        """Büyük batch'i böl"""
        mid = len(batch) // 2
        batch1 = batch[:mid]
        batch2 = batch[mid:]
        
        results = []
        
        result1 = await self.process_batch_ultra_safe(batch1, f"{batch_id}a")
        if result1:
            results.extend(result1)
            
        result2 = await self.process_batch_ultra_safe(batch2, f"{batch_id}b")
        if result2:
            results.extend(result2)
            
        return results
        
    def check_emergency_stop(self) -> bool:
        """Emergency stop kontrolü - gerçek durdurma"""
        if self.safety_monitor.should_emergency_stop(self.stats):
            self.logger.critical("Safety monitor emergency stop!")
            with open(self.emergency_stop_file, 'w') as f:
                f.write(f"Emergency stop: {datetime.now().isoformat()}")
            
            # GERÇEKTENstoı burada durdur!
            self.emergency_shutdown()
            raise SystemExit("Emergency stop triggered by safety monitor")
            
        return False  # Artık hiçbir zaman True dönmeyecek
        
    def emergency_shutdown(self):
        """Emergency shutdown"""
        self.logger.critical("EMERGENCY SHUTDOWN!")
        
        # Save emergency data
        emergency_data = {
            "shutdown_time": datetime.now().isoformat(),
            "stats": self.stats,
            "reason": "Emergency shutdown"
        }
        
        with open('emergency_shutdown.json', 'w', encoding='utf-8') as f:
            json.dump(emergency_data, f, ensure_ascii=False, indent=2)
            
    def save_checkpoint(self, batch_id: int, processed_data: List[Dict]):
        """Checkpoint kaydet"""
        checkpoint = {
            "last_batch": batch_id,
            "processed_count": len(processed_data),
            "total_stats": self.stats.copy(),
            "timestamp": datetime.now().isoformat(),
            "resume_point": batch_id + 1
        }
        
        os.makedirs('checkpoints', exist_ok=True)
        with open('checkpoints/latest.json', 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
    def resume_from_checkpoint(self) -> int:
        """Checkpoint'ten devam"""
        try:
            with open('checkpoints/latest.json', 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            return checkpoint.get('resume_point', 0)
        except:
            return 0
            
    def print_progress_report(self):
        """Progress raporu"""
        start_time = datetime.fromisoformat(self.stats['start_time'])
        elapsed = datetime.now() - start_time
        success_rate = (self.stats['successful_batches'] / 
                       max(self.stats['successful_batches'] + self.stats['failed_batches'], 1) * 100)
        
        self.logger.info(f"""
📊 === İLERLEME RAPORU ===
⏱️  Geçen süre: {elapsed}
✅ Başarılı: {self.stats['successful_batches']}
❌ Başarısız: {self.stats['failed_batches']}
📈 Başarı oranı: %{success_rate:.1f}
🔍 Duplicate: {self.stats['duplicates_found']}
⚠️  Geçersiz: {self.stats['invalid_responses']}
💰 Maliyet: {self.cost_tracker.get_estimated_cost()}
=========================""")
        
    async def augment_data_ultra_safe(self, input_file: str = None):
        """Ultra güvenli ana çoğaltma fonksiyonu"""
        try:
            if not input_file:
                input_file = self.config['file_settings']['input_file']
                
            self.logger.info("Ultra Safe Data Augmentation baslatildi")
            
            # Load data
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.logger.info(f"Toplam {len(data)} cift yuklendi")
            
            # Resume check
            resume_point = self.resume_from_checkpoint()
            
            # Create batches
            batch_size = self.config['safety_settings']['batch_size']
            batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]
            
            if resume_point > 0:
                batches = batches[resume_point:]
                self.logger.info(f"⏩ {resume_point} batch atlandı")
                
            self.logger.info(f"{len(batches)} batch olusturuldu")
            
            # Process batches
            all_augmented_data = []
            
            for i, batch in enumerate(batches, start=resume_point):
                progress = (i / len(batches)) * 100
                self.logger.info(f"Ilerleme: %{progress:.1f} - Batch {i+1}")
                
                # Config change kontrolü (her 5 batch'te bir)
                if i % 5 == 0 and self.check_config_changes():
                    self.logger.info("🔄 Config değişikliği tespit edildi, API keyleri güncelleniyor...")
                    reload_success = self.reload_config_and_apis()
                    if reload_success:
                        self.logger.info("✅ Config reload başarılı")
                    else:
                        self.logger.warning("⚠️ Config reload başarısız, eski config ile devam")
                
                result = await self.process_batch_ultra_safe(batch, i+1)
                
                if result:
                    all_augmented_data.extend(result)
                    
                # Checkpoint
                if i % 10 == 0:
                    self.save_checkpoint(i, all_augmented_data)
                    
                # Auto backup
                if i % self.config['safety_settings']['auto_backup_frequency'] == 0:
                    self.file_manager.safe_write_json(
                        all_augmented_data, 
                        f"backups/backup_batch_{i}_{datetime.now().strftime('%H%M')}.json"
                    )
                    
                # Memory cleanup ve monitoring
                if i % 20 == 0:
                    gc.collect()
                    self.print_progress_report()
                    
                    # API key health check
                    active_count = len(self.healthy_models)
                    if active_count < 3:
                        self.logger.warning(f"⚠️ Düşük API key sayısı: {active_count}. Config'e yeni key eklemeyi düşünün.")
                    
                # Performance monitoring
                self.performance_monitor.take_system_snapshot()
                    
            # Save final results
            await self.save_final_results(data, all_augmented_data)
            
        except Exception as e:
            self.logger.critical(f"Kritik hata: {e}")
            self.emergency_shutdown()
            raise
            
    async def save_final_results(self, original_data: List[Dict], augmented_data: List[Dict]):
        """Final results kaydet"""
        os.makedirs('output', exist_ok=True)
        
        # Augmented data
        augmented_file = f"output/augmented_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        self.file_manager.safe_write_json(augmented_data, augmented_file)
        
        # Combined dataset
        final_dataset = original_data + augmented_data
        final_file = f"output/final_dataset_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        self.file_manager.safe_write_json(final_dataset, final_file)
        
        # Report
        report = {
            "completion_time": datetime.now().isoformat(),
            "original_count": len(original_data),
            "augmented_count": len(augmented_data),
            "final_count": len(final_dataset),
            "multiplication_factor": len(final_dataset) / len(original_data),
            "stats": self.stats,
            "cost_analysis": self.cost_tracker.get_full_report(),
            "performance_summary": self.performance_monitor.get_performance_summary(),
            "safety_report": self.safety_monitor.generate_safety_report(),
            "files": {
                "augmented": augmented_file,
                "final": final_file
            }
        }
        
        self.file_manager.safe_write_json(report, 'output/final_report.json')
        
        self.logger.info(f"""
🎉 === ULTRA SAFE AUGMENTATION TAMAMLANDI! ===
📊 Orijinal: {len(original_data):,} çift
🆕 Yeni üretilen: {len(augmented_data):,} çift  
📈 Toplam: {len(final_dataset):,} çift
🔢 Çarpan: {len(final_dataset) / len(original_data):.1f}x
💾 Dosyalar: output/ klasöründe
===============================================""")

if __name__ == "__main__":
    try:
        augmenter = UltraSafeDataAugmenter()
        asyncio.run(augmenter.augment_data_ultra_safe())
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 