#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe Safety Monitor
Güvenlik izleme, maliyet takibi ve performans monitörü
"""

import time
import json
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

class SafetyMonitor:
    """Güvenlik izleme sistemi"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Güvenlik thresholdları
        self.max_fails_per_hour = config['safety_settings']['max_fails_per_hour']
        self.emergency_threshold = config['safety_settings']['emergency_shutdown_threshold']
        
        # İzleme verileri
        self.failure_times: List[str] = []
        self.performance_data: List[Dict] = []
        self.alerts_sent = 0
        
    def record_failure(self, error_type: str, details: str):
        """Başarısızlık kaydet"""
        failure_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'details': details
        }
        
        self.failure_times.append(failure_record['timestamp'])
        self.logger.error(f"Başarısızlık kaydedildi: {error_type} - {details}")
        
        # Eski kayıtları temizle (son 1 saat)
        cutoff_time = datetime.now() - timedelta(hours=1)
        cutoff_time_str = cutoff_time.isoformat()
        self.failure_times = [t for t in self.failure_times if t > cutoff_time_str]
        
    def should_emergency_stop(self, current_stats: Dict) -> bool:
        """Acil durdurma gerekli mi?"""
        try:
            # Saatlik başarısızlık kontrolü
            recent_failures = len(self.failure_times)
            if recent_failures >= self.max_fails_per_hour:
                self.logger.critical(f"Saatlik basarisizlik limiti asildi: {recent_failures}")
                return True
                
            # Toplam başarısızlık kontrolü
            total_failures = current_stats.get('failed_batches', 0)
            if total_failures >= self.emergency_threshold:
                self.logger.critical(f"Toplam basarisizlik limiti asildi: {total_failures}")
                return True
                
            # Memory kontrolü
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                self.logger.critical(f"Memory kullanimi kritik: %{memory_percent}")
                return True
                
            # API key kontrolü
            # Bu main script'te kontrol edilecek
            
            return False
            
        except Exception as e:
            self.logger.error(f"Emergency check hatası: {e}")
            return False
            
    def generate_safety_report(self) -> Dict:
        """Güvenlik raporu oluştur"""
        return {
            'timestamp': datetime.now().isoformat(),
            'recent_failures_count': len(self.failure_times),
            'alerts_sent': self.alerts_sent,
            'memory_usage': psutil.virtual_memory().percent,
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent,
            'uptime': str(datetime.now() - datetime.now().replace(hour=0, minute=0, second=0))
        }

class CostTracker:
    """Maliyet takip sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Gemini API fiyatları (varsayılan - güncellenmeli)
        self.pricing = {
            'input_tokens_per_1k': 0.00025,  # $0.00025 per 1K tokens
            'output_tokens_per_1k': 0.0005,  # $0.0005 per 1K tokens
            'free_tier_limit': 50000  # Aylık ücretsiz token limiti
        }
        
        # Kullanım verileri
        self.usage_data = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_requests': 0,
            'estimated_cost': 0.0,
            'start_time': datetime.now().isoformat()
        }
        
    def track_request(self, batch_size: int, estimated_input_tokens: int = 2000, estimated_output_tokens: int = 3000):
        """İstek kullanımını takip et"""
        try:
            self.usage_data['total_requests'] += 1
            self.usage_data['total_input_tokens'] += estimated_input_tokens
            self.usage_data['total_output_tokens'] += estimated_output_tokens
            
            # Maliyet hesapla
            input_cost = (self.usage_data['total_input_tokens'] / 1000) * self.pricing['input_tokens_per_1k']
            output_cost = (self.usage_data['total_output_tokens'] / 1000) * self.pricing['output_tokens_per_1k']
            
            self.usage_data['estimated_cost'] = input_cost + output_cost
            
            # Ücretsiz limit kontrolü
            total_tokens = self.usage_data['total_input_tokens'] + self.usage_data['total_output_tokens']
            if total_tokens > self.pricing['free_tier_limit']:
                self.logger.warning(f"⚠️ Ücretsiz limit aşıldı: {total_tokens:,} tokens")
                
        except Exception as e:
            self.logger.error(f"Cost tracking hatası: {e}")
            
    def get_estimated_cost(self) -> str:
        """Tahmini maliyeti getir"""
        return f"${self.usage_data['estimated_cost']:.4f}"
        
    def get_full_report(self) -> Dict:
        """Tam maliyet raporu"""
        start_time = datetime.fromisoformat(self.usage_data['start_time'])
        elapsed_time = datetime.now() - start_time
        
        return {
            'total_requests': self.usage_data['total_requests'],
            'total_input_tokens': self.usage_data['total_input_tokens'],
            'total_output_tokens': self.usage_data['total_output_tokens'],
            'estimated_cost_usd': self.usage_data['estimated_cost'],
            'tokens_per_minute': (self.usage_data['total_input_tokens'] + self.usage_data['total_output_tokens']) / max(elapsed_time.total_seconds() / 60, 1),
            'elapsed_time': str(elapsed_time),
            'free_tier_remaining': max(0, self.pricing['free_tier_limit'] - (self.usage_data['total_input_tokens'] + self.usage_data['total_output_tokens']))
        }

class RateLimiter:
    """Akıllı rate limiting sistemi"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting ayarları
        self.base_delay = config['safety_settings']['delay_between_requests']
        self.current_delay = self.base_delay
        self.max_delay = 60  # Maximum 60 saniye
        self.min_delay = 1   # Minimum 1 saniye
        
        # Performans takibi
        self.success_streak = 0
        self.failure_streak = 0
        self.last_request_time = 0
        
        # Adaptif ayarlar
        self.adaptive_mode = True
        
    async def wait_if_needed(self):
        """Gerekirse bekle"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.current_delay:
                wait_time = self.current_delay - time_since_last
                self.logger.debug(f"Rate limit beklemesi: {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                
            self.last_request_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Rate limiter hatası: {e}")
            await asyncio.sleep(self.base_delay)
            
    def record_success(self):
        """Başarı kaydet"""
        self.success_streak += 1
        self.failure_streak = 0
        
        if self.adaptive_mode and self.success_streak >= 10:
            # Başarı streak'i varsa hızlan
            self.current_delay = max(self.min_delay, self.current_delay * 0.9)
            self.success_streak = 0
            self.logger.debug(f"Rate limit azaltıldı: {self.current_delay:.1f}s")
            
    def record_failure(self):
        """Başarısızlık kaydet"""
        self.failure_streak += 1
        self.success_streak = 0
        
        if self.adaptive_mode:
            # Başarısızlık varsa yavaşla
            self.current_delay = min(self.max_delay, self.current_delay * 1.5)
            self.logger.warning(f"Rate limit artırıldı: {self.current_delay:.1f}s")
            
    def get_current_delay(self) -> float:
        """Mevcut delay değeri"""
        return self.current_delay
        
    def reset_to_base(self):
        """Base delay'e sıfırla"""
        self.current_delay = self.base_delay
        self.success_streak = 0
        self.failure_streak = 0

class PerformanceMonitor:
    """Performans izleme sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'batch_processing_times': [],
            'api_response_times': [],
            'validation_times': [],
            'memory_snapshots': [],
            'cpu_snapshots': []
        }
        
    def record_batch_time(self, processing_time: float):
        """Batch işlem süresini kaydet"""
        self.metrics['batch_processing_times'].append({
            'timestamp': datetime.now().isoformat(),
            'duration': processing_time
        })
        
        # Son 100 kayıt tut
        if len(self.metrics['batch_processing_times']) > 100:
            self.metrics['batch_processing_times'] = self.metrics['batch_processing_times'][-100:]
            
    def record_api_time(self, response_time: float):
        """API yanıt süresini kaydet"""
        self.metrics['api_response_times'].append({
            'timestamp': datetime.now().isoformat(),
            'duration': response_time
        })
        
        if len(self.metrics['api_response_times']) > 100:
            self.metrics['api_response_times'] = self.metrics['api_response_times'][-100:]
            
    def take_system_snapshot(self):
        """Sistem anlık görüntüsü"""
        try:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(),
                'available_memory_gb': psutil.virtual_memory().available / (1024**3)
            }
            
            self.metrics['memory_snapshots'].append(snapshot)
            
            # Son 50 snapshot tut
            if len(self.metrics['memory_snapshots']) > 50:
                self.metrics['memory_snapshots'] = self.metrics['memory_snapshots'][-50:]
                
        except Exception as e:
            self.logger.error(f"System snapshot hatası: {e}")
            
    def get_performance_summary(self) -> Dict:
        """Performans özeti"""
        try:
            # Batch processing ortalaması
            batch_times = [m['duration'] for m in self.metrics['batch_processing_times']]
            avg_batch_time = sum(batch_times) / len(batch_times) if batch_times else 0
            
            # API response ortalaması
            api_times = [m['duration'] for m in self.metrics['api_response_times']]
            avg_api_time = sum(api_times) / len(api_times) if api_times else 0
            
            # Memory ortalaması
            memory_values = [m['memory_percent'] for m in self.metrics['memory_snapshots']]
            avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
            
            return {
                'average_batch_time': avg_batch_time,
                'average_api_time': avg_api_time,
                'average_memory_usage': avg_memory,
                'total_batches_monitored': len(batch_times),
                'total_api_calls_monitored': len(api_times)
            }
            
        except Exception as e:
            self.logger.error(f"Performance summary hatası: {e}")
            return {}

class AlertSystem:
    """Uyarı sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_history = []
        
    def send_alert(self, level: str, message: str, details: Dict = None):
        """Uyarı gönder"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'details': details or {}
        }
        
        self.alert_history.append(alert)
        
        # Log level'a göre kaydet
        if level == 'critical':
            self.logger.critical(f"CRITICAL ALERT: {message}")
        elif level == 'warning':
            self.logger.warning(f"⚠️ WARNING: {message}")
        elif level == 'info':
            self.logger.info(f"ℹ️ INFO: {message}")
            
        # Alert history'yi sınırla
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-500:]
            
    def get_recent_alerts(self, hours: int = 1) -> List[Dict]:
        """Son uyarıları getir"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_time_str = cutoff_time.isoformat()
        return [alert for alert in self.alert_history if alert['timestamp'] > cutoff_time_str] 