#!/usr/bin/env python3
"""API Key Ekleme Helper Script"""

import json
import sys
import os
from datetime import datetime

def load_config():
    """Mevcut config'i yükle"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Config yüklenemedi: {e}")
        return None

def save_config(config):
    """Config'i kaydet"""
    try:
        # Backup oluştur
        backup_file = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"📁 Backup oluşturuldu: {backup_file}")
        
        # Ana config'i güncelle
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ Config güncellendi")
        return True
    except Exception as e:
        print(f"❌ Config kaydetme hatası: {e}")
        return False

def test_api_key(api_key):
    """API key'i test et"""
    try:
        import google.generativeai as genai
        
        print(f"🧪 API Key test ediliyor...", end=" ")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Test")
        
        if response.text:
            print("✅ AKTİF")
            return True
        else:
            print("❌ BOŞ RESPONSE")
            return False
            
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            print("⚠️ QUOTA AŞILDI (Eklenebilir)")
            return True  # Quota aşsa bile geçerli key
        elif "403" in error_str:
            print("🚫 YETKİSİZ")
            return False
        else:
            print(f"❌ HATA: {str(e)[:50]}...")
            return False

def add_api_key():
    """Yeni API key ekle"""
    print("🔑 API KEY EKLEME SCRIPTI")
    print("=" * 40)
    
    # Config yükle
    config = load_config()
    if not config:
        return
    
    current_keys = config.get('api_keys', [])
    print(f"📊 Mevcut API key sayısı: {len(current_keys)}")
    
    # Yeni key al
    print("\n📝 Yeni API key'i girin:")
    print("   (AIzaSy... şeklinde başlamalı)")
    new_key = input("➤ API Key: ").strip()
    
    if not new_key:
        print("❌ Boş key girdiniz!")
        return
    
    if not new_key.startswith("AIzaSy"):
        print("⚠️ Geçersiz format! AIzaSy... ile başlamalı.")
        confirm = input("Yine de eklemek istiyor musunuz? (y/N): ")
        if confirm.lower() != 'y':
            return
    
    # Duplicate kontrolü
    if new_key in current_keys:
        print("⚠️ Bu API key zaten mevcut!")
        return
    
    # Test et
    if test_api_key(new_key):
        # Config'e ekle
        current_keys.append(new_key)
        config['api_keys'] = current_keys
        
        if save_config(config):
            print(f"🎉 API Key başarıyla eklendi!")
            print(f"📈 Toplam key sayısı: {len(current_keys)}")
            print("\n💡 Çalışan sistem otomatik olarak yeni key'i algılayacak!")
        else:
            print("❌ Config kaydetme başarısız!")
    else:
        print("❌ API Key test başarısız, eklenmedi!")

def list_api_keys():
    """Mevcut API keyleri listele"""
    print("📋 MEVCUT API KEYLER")
    print("=" * 40)
    
    config = load_config()
    if not config:
        return
    
    api_keys = config.get('api_keys', [])
    
    if not api_keys:
        print("❌ Hiç API key bulunamadı!")
        return
    
    print(f"📊 Toplam {len(api_keys)} API key bulundu:\n")
    
    for i, key in enumerate(api_keys, 1):
        preview = key[:10] + "..." + key[-5:] if len(key) > 15 else key
        print(f"   {i:2d}. {preview}")
    
    print(f"\n💾 Config dosyası: config.json")

def remove_api_key():
    """API key sil"""
    print("🗑️ API KEY SİLME")
    print("=" * 40)
    
    config = load_config()
    if not config:
        return
    
    api_keys = config.get('api_keys', [])
    
    if not api_keys:
        print("❌ Silinecek API key bulunamadı!")
        return
    
    print(f"📊 Mevcut {len(api_keys)} API key:")
    for i, key in enumerate(api_keys, 1):
        preview = key[:10] + "..." + key[-5:] if len(key) > 15 else key
        print(f"   {i:2d}. {preview}")
    
    try:
        choice = int(input(f"\nSilinecek key numarası (1-{len(api_keys)}): "))
        if 1 <= choice <= len(api_keys):
            removed_key = api_keys.pop(choice - 1)
            config['api_keys'] = api_keys
            
            preview = removed_key[:10] + "..." + removed_key[-5:]
            print(f"🗑️ Silinen key: {preview}")
            
            if save_config(config):
                print(f"✅ API Key silindi! Kalan: {len(api_keys)}")
            else:
                print("❌ Config kaydetme başarısız!")
        else:
            print("❌ Geçersiz numara!")
    except ValueError:
        print("❌ Geçersiz giriş!")

def main():
    """Ana menü"""
    while True:
        print("\n🔑 API KEY YÖNETİM SCRIPTI")
        print("=" * 40)
        print("1. 🆕 Yeni API key ekle")
        print("2. 📋 Mevcut keyleri listele")
        print("3. 🗑️ API key sil")
        print("4. 🧪 Config'deki tüm keyleri test et")
        print("5. ❌ Çıkış")
        print("-" * 40)
        
        try:
            choice = input("Seçiminiz (1-5): ").strip()
            
            if choice == '1':
                add_api_key()
            elif choice == '2':
                list_api_keys()
            elif choice == '3':
                remove_api_key()
            elif choice == '4':
                os.system('python api_test.py')
            elif choice == '5':
                print("👋 Çıkış yapılıyor...")
                break
            else:
                print("❌ Geçersiz seçim!")
                
        except KeyboardInterrupt:
            print("\n👋 Çıkış yapılıyor...")
            break
        except Exception as e:
            print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main() 