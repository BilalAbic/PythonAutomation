#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key Manager for PDF Processing
DataMin2x tabanlı gelişmiş API key yönetimi
"""

import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional
import google.generativeai as genai

class APIKeyManager:
    """Gelişmiş API key yönetim sistemi"""
    
    def __init__(self, api_keys: List[str], logger):
        self.api_keys = api_keys
        self.logger = logger
        self.healthy_models = []
        self.failed_models = []
        self.api_key_lock = threading.Lock()
        
    def test_all_keys(self) -> int:
        """Tüm API keyleri test et ve aktif olanları belirle"""
        self.healthy_models = []
        self.failed_models = []
        
        for i, api_key in enumerate(self.api_keys):
            try:
                self.logger.info(f"🔑 API Key {i+1} test ediliyor...")
                
                # Configure and test
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Test call
                test_response = model.generate_content("Test mesajı")
                if test_response.text:
                    self.healthy_models.append({
                        'model': model,
                        'api_key': api_key[:10] + "...",
                        'index': i,
                        'success_count': 0,
                        'error_count': 0,
                        'last_used': None,
                        'quota_exceeded': False
                    })
                    self.logger.info(f"✅ API Key {i+1} aktif")
                else:
                    raise Exception("Boş response")
                    
            except Exception as e:
                error_str = str(e)
                if "quota" in error_str.lower() or "429" in error_str:
                    self.logger.warning(f"⚠️ API Key {i+1} quota aşıldı")
                else:
                    self.logger.error(f"❌ API Key {i+1} başarısız: {e}")
                self.failed_models.append(i)
                
        return len(self.healthy_models)
        
    def get_best_model(self) -> Optional[Dict]:
        """En iyi performanslı model seç"""
        with self.api_key_lock:
            if not self.healthy_models:
                return None
                
            # Success rate'e göre sırala
            self.healthy_models.sort(
                key=lambda x: x['success_count'] - x['error_count'], 
                reverse=True
            )
            
            best_model = self.healthy_models[0]
            best_model['last_used'] = datetime.now().isoformat()
            
            return best_model
            
    def record_success(self, model_info: Dict):
        """Başarı kaydet"""
        model_info['success_count'] += 1
        
    def record_failure(self, model_info: Dict):
        """Başarısızlık kaydet"""
        model_info['error_count'] += 1
        
        # Çok fazla hata varsa devre dışı bırak
        if model_info['error_count'] > 10:
            if model_info in self.healthy_models:
                self.healthy_models.remove(model_info)
                self.logger.warning(f"API Key {model_info['index']+1} çok fazla hata, devre dışı")
                
    def mark_quota_exceeded(self, model_info: Dict):
        """Quota aşımı işaretle"""
        model_info['quota_exceeded'] = True
        if model_info in self.healthy_models:
            self.healthy_models.remove(model_info)
            
    def update_api_keys(self, new_api_keys: List[str]):
        """API keyleri güncelle (hot reload)"""
        old_count = len(self.healthy_models)
        
        # Yeni keyleri ekle
        for i, api_key in enumerate(new_api_keys):
            if i >= len(self.api_keys):  # Yeni key
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    test_response = model.generate_content("Test")
                    if test_response.text:
                        self.healthy_models.append({
                            'model': model,
                            'api_key': api_key[:10] + "...",
                            'index': i,
                            'success_count': 0,
                            'error_count': 0,
                            'last_used': None,
                            'quota_exceeded': False
                        })
                        self.logger.info(f"➕ Yeni API Key {i+1} eklendi")
                except:
                    pass
                    
        self.api_keys = new_api_keys
        new_count = len(self.healthy_models)
        
        if new_count > old_count:
            self.logger.info(f"🎉 {new_count - old_count} yeni API key eklendi!")
            
    def get_status_report(self) -> Dict:
        """API key durumu raporu"""
        return {
            'total_keys': len(self.api_keys),
            'healthy_keys': len(self.healthy_models),
            'failed_keys': len(self.failed_models),
            'keys_with_quota': len([m for m in self.healthy_models if m.get('quota_exceeded', False)]),
            'best_performing_key': self.healthy_models[0]['index'] + 1 if self.healthy_models else None
        } 