#!/usr/bin/env python3
"""API Key Test Script - Detaylı Analiz"""

import json
import time
import google.generativeai as genai
from datetime import datetime

def load_config():
    """Config dosyasını yükle"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Config yüklenemedi: {e}")
        return None

def test_single_api_key(api_key, index):
    """Tek API key test et"""
    try:
        print(f"🔑 API Key {index+1} test ediliyor...", end=" ")
        
        # Configure
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test call with timeout
        start_time = time.time()
        response = model.generate_content("Test mesajı için kısa bir cevap ver.")
        response_time = time.time() - start_time
        
        if response.text:
            print(f"✅ AKTİF ({response_time:.2f}s)")
            return {
                'status': 'active',
                'response_time': response_time,
                'response_length': len(response.text),
                'error': None
            }
        else:
            print("❌ BOŞ RESPONSE")
            return {
                'status': 'empty_response',
                'response_time': response_time,
                'response_length': 0,
                'error': 'Empty response'
            }
            
    except Exception as e:
        error_str = str(e)
        
        if "quota" in error_str.lower() or "429" in error_str:
            print("⚠️ QUOTA AŞILDI")
            return {
                'status': 'quota_exceeded',
                'response_time': None,
                'response_length': 0,
                'error': 'Quota exceeded'
            }
        elif "403" in error_str:
            print("🚫 YETKİSİZ")
            return {
                'status': 'unauthorized',
                'response_time': None,
                'response_length': 0,
                'error': 'Unauthorized'
            }
        elif "timeout" in error_str.lower():
            print("⏰ TIMEOUT")
            return {
                'status': 'timeout',
                'response_time': None,
                'response_length': 0,
                'error': 'Timeout'
            }
        else:
            print(f"❌ HATA: {str(e)[:50]}...")
            return {
                'status': 'error',
                'response_time': None,
                'response_length': 0,
                'error': str(e)[:100]
            }

def main():
    """Ana test fonksiyonu"""
    print("🚀 API KEY TEST SCRIPTI")
    print("=" * 60)
    print(f"⏰ Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Config yükle
    config = load_config()
    if not config:
        return
    
    api_keys = config.get('api_keys', [])
    if not api_keys:
        print("❌ Config'de API key bulunamadı!")
        return
    
    print(f"🔍 Toplam {len(api_keys)} API key test edilecek\n")
    
    # Test sonuçları
    results = []
    active_keys = 0
    quota_exceeded = 0
    error_keys = 0
    
    # Her API key'i test et
    for i, api_key in enumerate(api_keys):
        result = test_single_api_key(api_key, i)
        result['key_index'] = i + 1
        result['key_preview'] = api_key[:10] + "..."
        results.append(result)
        
        # İstatistik güncelle
        if result['status'] == 'active':
            active_keys += 1
        elif result['status'] == 'quota_exceeded':
            quota_exceeded += 1
        else:
            error_keys += 1
        
        # Rate limiting için kısa bekleme
        time.sleep(0.5)
    
    # Sonuçları analiz et
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    print(f"✅ Aktif Keyler: {active_keys}/{len(api_keys)} (%{active_keys/len(api_keys)*100:.1f})")
    print(f"⚠️ Quota Aşan: {quota_exceeded}/{len(api_keys)} (%{quota_exceeded/len(api_keys)*100:.1f})")
    print(f"❌ Hatalı Keyler: {error_keys}/{len(api_keys)} (%{error_keys/len(api_keys)*100:.1f})")
    
    # Detaylı rapor
    print("\n📋 DETAYLI RAPOR:")
    print("-" * 60)
    
    for result in results:
        status_emoji = {
            'active': '✅',
            'quota_exceeded': '⚠️',
            'unauthorized': '🚫',
            'timeout': '⏰',
            'error': '❌',
            'empty_response': '⚪'
        }
        
        emoji = status_emoji.get(result['status'], '❓')
        key_num = result['key_index']
        
        if result['status'] == 'active':
            print(f"{emoji} Key {key_num:2d}: AKTİF - {result['response_time']:.2f}s - {result['response_length']} char")
        else:
            print(f"{emoji} Key {key_num:2d}: {result['status'].upper()} - {result['error']}")
    
    # Öneriler
    print("\n💡 ÖNERİLER:")
    print("-" * 60)
    
    if active_keys >= 10:
        print("🎉 Mükemmel! Yeterli aktif key var.")
    elif active_keys >= 5:
        print("👍 İyi! İşlem için yeterli key var.")
    elif active_keys >= 3:
        print("⚠️ Dikkat! Az key var, yavaş olabilir.")
    else:
        print("🚨 Uyarı! Çok az key aktif!")
    
    if quota_exceeded > 0:
        print(f"⏰ {quota_exceeded} key quota aştı. 24 saat bekleyin veya yeni key ekleyin.")
    
    # Performance tahmini
    if active_keys > 0:
        estimated_speed = active_keys * 15  # 15 requests/minute per key
        total_batches = 1147  # 11,467 / 10
        estimated_hours = total_batches / (estimated_speed * 6)  # 6 batches per minute max
        
        print(f"\n⚡ PERFORMANS TAHMİNİ:")
        print(f"   • Aktif keyler: {active_keys}")
        print(f"   • Hız: ~{estimated_speed} request/dakika")
        print(f"   • Tahmini süre: ~{estimated_hours:.1f} saat")
    
    print("\n" + "=" * 60)
    print("✅ API Key test tamamlandı!")

def test_api_keys():
    """Test API keys to see which ones are still working"""
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_keys = config['api_keys']
    working_keys = []
    exhausted_keys = []
    
    print(f"🔍 Testing {len(api_keys)} API keys...")
    print("=" * 50)
    
    for i, api_key in enumerate(api_keys, 1):
        print(f"Testing key {i}/{len(api_keys)}: {api_key[:10]}...")
        
        try:
            # Configure API
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Simple test
            response = model.generate_content("Hello", generation_config={"max_output_tokens": 10})
            
            if response.text:
                working_keys.append(api_key)
                print(f"✅ Key {i}: WORKING")
            else:
                exhausted_keys.append(api_key)
                print(f"❌ Key {i}: NO RESPONSE")
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                exhausted_keys.append(api_key)
                print(f"🚫 Key {i}: QUOTA EXCEEDED")
            elif "invalid" in error_msg.lower() or "403" in error_msg:
                print(f"❌ Key {i}: INVALID KEY")
            else:
                print(f"⚠️ Key {i}: ERROR - {error_msg[:50]}...")
        
        # Small delay between tests
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY:")
    print(f"✅ Working keys: {len(working_keys)}")
    print(f"🚫 Exhausted keys: {len(exhausted_keys)}")
    print(f"❌ Other issues: {len(api_keys) - len(working_keys) - len(exhausted_keys)}")
    
    if working_keys:
        print(f"\n🎯 RECOMMENDATION: Use only working keys")
        print("Working keys:")
        for key in working_keys:
            print(f"  - {key[:15]}...")
    else:
        print(f"\n⏰ ALL KEYS EXHAUSTED - Wait for quota reset (usually 24 hours)")

if __name__ == "__main__":
    test_api_keys() 