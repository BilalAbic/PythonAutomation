import google.generativeai as genai
import openai
import json
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass

@dataclass
class APIProvider:
    name: str
    api_keys: List[str]
    model: str
    enabled: bool
    rate_limit_delay: float
    max_requests_per_minute: int
    key_rotation_strategy: str = "round_robin"
    
    def __post_init__(self):
        self.current_key_index = 0
        self.active_keys = [key for key in self.api_keys if key and not key.startswith("YOUR_")]
        if not self.active_keys:
            logging.warning(f"{self.name} için geçerli API anahtarı bulunamadı!")
    
    def get_next_api_key(self) -> str:
        """Strateji'ye göre bir sonraki API anahtarını döndürür"""
        if not self.active_keys:
            raise ValueError(f"{self.name} için aktif API anahtarı yok!")
            
        if self.key_rotation_strategy == "round_robin":
            key = self.active_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.active_keys)
            return key
        elif self.key_rotation_strategy == "random":
            import random
            return random.choice(self.active_keys)
        else:
            return self.active_keys[0]  # Default: ilk anahtarı kullan

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Config dosyasını yükler"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config dosyası bulunamadı: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Config dosyası JSON formatında değil: {e}")
            raise
    
    def get_enabled_providers(self) -> List[APIProvider]:
        """Aktif API sağlayıcılarını döndürür"""
        providers = []
        for provider_config in self.config['api_settings']['providers']:
            if provider_config['enabled']:
                providers.append(APIProvider(**provider_config))
        return providers
    
    def get_augmentation_settings(self) -> Dict[str, Any]:
        return self.config['augmentation_settings']
    
    def get_processing_settings(self) -> Dict[str, Any]:
        return self.config['processing_settings']

class AdvancedDataAugmentor:
    def __init__(self, config_file: str = "config.json"):
        self.config_manager = ConfigManager(config_file)
        self.providers = self.config_manager.get_enabled_providers()
        self.augmentation_settings = self.config_manager.get_augmentation_settings()
        self.processing_settings = self.config_manager.get_processing_settings()
        
        # Logging kurulumu
        self.setup_logging()
        
        # API istemcilerini başlat
        self.setup_api_clients()
        
        # Eşzamanlılık kontrolü
        self.semaphore = threading.Semaphore(self.processing_settings['max_concurrent_requests'])
        
    def setup_logging(self):
        """Logging sistemini kurar"""
        log_config = self.config_manager.config['logging']
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file'], encoding='utf-8'),
                logging.StreamHandler() if log_config['console_output'] else logging.NullHandler()            ]
        )
        
    def setup_api_clients(self):
        """API istemcilerini kurar"""
        for provider in self.providers:
            if provider.name == "gemini":
                # Gemini için ilk API anahtarını varsayılan olarak ayarla
                if provider.active_keys:
                    genai.configure(api_key=provider.active_keys[0])
            elif provider.name == "openai":
                # OpenAI için ilk API anahtarını varsayılan olarak ayarla
                if provider.active_keys:
                    openai.api_key = provider.active_keys[0]
                
    def get_dynamic_augmentation_prompt(self, soru: str, cevap: str) -> str:
        """Dinamik sayıda varyasyon için prompt oluşturur"""
        variation_count = self.augmentation_settings['variations_per_question']
        variation_types = self.augmentation_settings['variation_types']
        
        # Varyasyon tiplerini dinamik olarak oluştur
        type_instructions = []
        for type_name, count in variation_types.items():
            type_map = {
                'kisisel_senaryo': f"**Kişisel Senaryo ({count} adet):** Sanki bir kullanıcı kendi başından geçen bir olayı anlatıp soru soruyormuş gibi yaz.",
                'samimi_gunluk': f"**Samimi/Günlük Dil ({count} adet):** Daha rahat, günlük bir konuşma dili kullan.",
                'basit_direkt': f"**Basit ve Direkt ({count} adet):** Soruyu çok daha basit ve net bir şekilde ifade et.",
                'yazim_hatali': f"**Yazım Hatalı ({count} adet):** Birkaç harf hatası veya eksik karakter içeren, gerçekçi yazım hataları yap.",
                'farkli_soru_koku': f"**Farklı Soru Kökü ({count} adet):** \"... nedir?\" yerine \"... hakkında bilgi verir misin?\", \"... nasıl yapılır?\" gibi farklı soru yapıları kullan."
            }
            if type_name in type_map:
                type_instructions.append(type_map[type_name])
        
        return f"""
PROMPT BAŞLANGICI

**ROL:** Sen, Türkçe dilbilgisine ve farklı konuşma tarzlarına hakim bir metin üreticisisin.
**GÖREV:** Sana verilen Orijinal Soru-Cevap çiftindeki soruyu, anlamını koruyarak ama tamamen farklı ifade tarzları kullanarak {variation_count} YENİ VERSİYONUNU oluştur.

**YENİ SORU VERSİYONLARI İÇİN KURALLAR:**
{chr(10).join(f"{i+1}. {instruction}" for i, instruction in enumerate(type_instructions))}

**ÇIKTI FORMATI:** Tüm yeni soruları bir JSON listesi olarak ver. Her eleman {{"soru": "yeni_soru", "cevap": "orijinal_cevap"}} formatında olmalı. Sadece JSON listesini ver, başka hiçbir açıklama ekleme.

---
**İŞLENECEK VERİ:**

**Orijinal Soru:**
"{soru}"

**Orijinal Cevap:**
"{cevap}"
---

PROMPT SONU
"""    def generate_with_gemini(self, prompt: str, provider: APIProvider) -> Optional[List[Dict]]:
        """Gemini API ile içerik üretir"""
        try:
            # Bir sonraki API anahtarını al ve kullan
            current_api_key = provider.get_next_api_key()
            genai.configure(api_key=current_api_key)
            
            model = genai.GenerativeModel(provider.model)
            response = model.generate_content(prompt)
            
            response_text = response.text
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end != 0:
                json_string = response_text[json_start:json_end]
                return json.loads(json_string)
            return None
            
        except Exception as e:
            logging.error(f"Gemini API hatası (key: {current_api_key[-10:]}...): {e}")
            return None
            
    def generate_with_openai(self, prompt: str, provider: APIProvider) -> Optional[List[Dict]]:
        """OpenAI API ile içerik üretir"""
        try:
            # Bir sonraki API anahtarını al ve kullan
            current_api_key = provider.get_next_api_key()
            openai.api_key = current_api_key
            
            response = openai.ChatCompletion.create(
                model=provider.model,
                messages=[
                    {"role": "system", "content": "Sen Türkçe soru-cevap çiftleri üreten bir asistansın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            
            if json_start != -1 and json_end != 0:
                json_string = content[json_start:json_end]
                return json.loads(json_string)
            return None
            
        except Exception as e:
            logging.error(f"OpenAI API hatası (key: {current_api_key[-10:]}...): {e}")
            return None
    
    def process_single_entry(self, entry: Dict[str, str], entry_index: int, total_entries: int) -> List[Dict[str, str]]:
        """Tek bir girdiyi işler (thread-safe)"""
        with self.semaphore:
            original_soru = entry.get('soru')
            original_cevap = entry.get('cevap')
            
            if not original_soru or not original_cevap:
                return []
            
            logging.info(f"İşleniyor: [{entry_index+1}/{total_entries}] - Soru: {original_soru[:50]}...")
            
            prompt = self.get_dynamic_augmentation_prompt(original_soru, original_cevap)
            
            # Aktif sağlayıcılar arasından birini seç (round-robin)
            provider = self.providers[entry_index % len(self.providers)]
            
            result = None
            if provider.name == "gemini":
                result = self.generate_with_gemini(prompt, provider)
            elif provider.name == "openai":
                result = self.generate_with_openai(prompt, provider)
            
            # Rate limiting
            time.sleep(provider.rate_limit_delay)
            
            return result if result else []
    
    def create_backup(self, data: List[Dict], timestamp: str):
        """Veri yedeği oluşturur"""
        if self.processing_settings['backup_enabled']:
            backup_file = f"backup_{timestamp}_{self.processing_settings['input_file']}"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Yedek dosya oluşturuldu: {backup_file}")
    
    def process_data_augmentation(self):
        """Ana veri çoğaltma işlemi"""
        input_file = self.processing_settings['input_file']
        output_file = self.processing_settings['output_file']
        process_limit = self.processing_settings['process_limit']
        max_workers = self.processing_settings['max_concurrent_requests']
        
        # Veriyi yükle
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
        except FileNotFoundError:
            logging.error(f"Girdi dosyası bulunamadı: {input_file}")
            return
        
        # İşlenecek veri miktarını belirle
        data_to_process = original_data[:process_limit] if process_limit else original_data
        
        # Yedek oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.create_backup(original_data, timestamp)
        
        logging.info(f"Toplam {len(data_to_process)} girdi için soru çoğaltma işlemi başlıyor...")
        logging.info(f"Aktif API sağlayıcıları: {[p.name for p in self.providers]}")
        logging.info(f"Maksimum eşzamanlı istek: {max_workers}")
        
        augmented_data = []
        
        # Eşzamanlı işleme
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Tüm görevleri başlat
            future_to_entry = {
                executor.submit(self.process_single_entry, entry, i, len(data_to_process)): entry 
                for i, entry in enumerate(data_to_process)
            }
            
            # Tamamlanan görevleri işle
            for future in as_completed(future_to_entry):
                try:
                    result = future.result()
                    if result:
                        augmented_data.extend(result)
                except Exception as e:
                    logging.error(f"Görev işlenirken hata: {e}")
        
        # Sonuçları birleştir ve kaydet
        final_data = original_data + augmented_data
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        # İstatistikleri yazdır
        logging.info(f"İşlem tamamlandı!")
        logging.info(f"{len(original_data)} orijinal girdi")
        logging.info(f"{len(augmented_data)} yeni üretilen girdi")
        logging.info(f"Toplam {len(final_data)} girdi '{output_file}' dosyasına kaydedildi.")
        
        # Başarı oranını hesapla
        expected_augmented = len(data_to_process) * self.augmentation_settings['variations_per_question']
        success_rate = (len(augmented_data) / expected_augmented * 100) if expected_augmented > 0 else 0
        logging.info(f"Başarı oranı: {success_rate:.1f}%")

def main():
    """Ana fonksiyon"""
    try:
        augmentor = AdvancedDataAugmentor()
        augmentor.process_data_augmentation()
    except Exception as e:
        logging.error(f"Ana işlem hatası: {e}")
        print(f"HATA: {e}")

if __name__ == "__main__":
    main()
