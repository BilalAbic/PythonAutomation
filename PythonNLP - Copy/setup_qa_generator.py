# PDF'den Soru-Cevap Üretimi - Kurulum ve Kullanım Rehberi

print("PDF'den Soru-Cevap Üretimi Kurulum Başlatılıyor...")
print("=" * 50)

import subprocess
import sys
import os

def install_requirements():
    """Gerekli paketleri yükler"""
    print("Gerekli Python paketleri yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Paketler başarıyla yüklendi!")
    except subprocess.CalledProcessError:
        print("❌ Paket yükleme hatası!")
        return False
    return True

def check_api_key():
    """API anahtarı kontrolü"""
    print("\n📋 API Anahtarı Kurulumu:")
    print("1. Google AI Studio'ya gidin: https://makersuite.google.com/app/apikey")
    print("2. Yeni API anahtarı oluşturun")
    print("3. pdf_to_qa_gemini.py dosyasındaki API_KEY değişkenine anahtarınızı girin")
    
    api_key = input("\nAPI anahtarınızı buraya girin (test için): ").strip()
    
    if len(api_key) > 20:  # Basit kontrol
        # API anahtarını dosyaya yaz
        with open("pdf_to_qa_gemini.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("YOUR_GEMINI_API_KEY_HERE", api_key)
        
        with open("pdf_to_qa_gemini.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ API anahtarı kaydedildi!")
        return True
    else:
        print("❌ Geçersiz API anahtarı!")
        return False

def main():
    print("🚀 Kurulum başlatılıyor...\n")
    
    # Paketleri yükle
    if not install_requirements():
        return
    
    # API anahtarını ayarla
    if not check_api_key():
        print("\n⚠️  API anahtarını manuel olarak pdf_to_qa_gemini.py dosyasında ayarlayın.")
    
    print("\n🎉 Kurulum tamamlandı!")
    print("\nKullanım:")
    print("python pdf_to_qa_gemini.py")
    print("\nVeya:")
    print("python run_qa_generation.py")

if __name__ == "__main__":
    main()
