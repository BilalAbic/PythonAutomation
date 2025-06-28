#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Anahtarı Kurulum Yardımcısı
Bu script Google Gemini API anahtarı kurulumunda yardımcı olur.
"""

def show_api_setup_instructions():
    """API anahtarı kurulum talimatlarını gösterir"""
    print("🔑 Google Gemini API Anahtarı Kurulumu")
    print("=" * 45)
    
    print("\n📋 ADIM ADIM TALİMATLAR:")
    print("\n1️⃣  Google AI Studio'ya Gidin:")
    print("   🌐 https://makersuite.google.com/app/apikey")
    print("   📝 Google hesabınızla giriş yapın")
    
    print("\n2️⃣  API Anahtarı Oluşturun:")
    print("   🔘 'Create API Key' butonuna tıklayın")
    print("   🔘 Bir proje seçin veya yeni proje oluşturun")
    print("   🔘 API anahtarınızı kopyalayın")
    
    print("\n3️⃣  API Anahtarını Sisteme Ekleyin:")
    print("   📂 pdf_to_qa_gemini.py dosyasını açın")
    print("   🔍 'YOUR_GEMINI_API_KEY_HERE' satırını bulun")
    print("   ✏️  Bu kısmı kendi API anahtarınızla değiştirin")
    
    print("\n📄 ÖRNEK:")
    print('   Eski: API_KEY = "YOUR_GEMINI_API_KEY_HERE"')
    print('   Yeni: API_KEY = "AIzaSyD...Xz1vQ"')
    
    print("\n⚠️  GÜVENLİK UYARILARI:")
    print("   🔒 API anahtarınızı kimseyle paylaşmayın")
    print("   🔒 GitHub gibi platformlara yüklemeyin")
    print("   🔒 Düzenli olarak yenileyin")
    
    print("\n💰 MALİYET BİLGİSİ:")
    print("   📊 Gemini API kullanım tabanlı ücretlendirilir")
    print("   💵 Aylık ücretsiz limit: 1,000 istek")
    print("   💳 Aşım durumunda kredi kartı gerekir")
    
    return True

def check_api_key_status():
    """Mevcut API anahtarı durumunu kontrol eder"""
    try:
        with open("pdf_to_qa_gemini.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if 'YOUR_GEMINI_API_KEY_HERE' in content:
            print("❌ API anahtarı henüz ayarlanmamış")
            return False
        else:
            print("✅ API anahtarı ayarlanmış görünüyor")
            return True
    except FileNotFoundError:
        print("❌ pdf_to_qa_gemini.py dosyası bulunamadı!")
        return False

def manual_api_setup():
    """Manuel API anahtarı kurulumu"""
    print("\n🔧 Manuel API Anahtarı Kurulumu")
    print("-" * 35)
    
    api_key = input("API anahtarınızı buraya yapıştırın: ").strip()
    
    if len(api_key) < 20:
        print("❌ Geçersiz API anahtarı! (çok kısa)")
        return False
    
    if not api_key.startswith("AIza"):
        print("⚠️  API anahtarı genellikle 'AIza' ile başlar. Emin misiniz?")
        confirm = input("Devam etmek istiyor musunuz? (e/h): ").lower()
        if confirm not in ['e', 'evet', 'y', 'yes']:
            print("İptal edildi.")
            return False
    
    try:
        # Dosyayı oku
        with open("pdf_to_qa_gemini.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # API anahtarını değiştir
        content = content.replace("YOUR_GEMINI_API_KEY_HERE", api_key)
        
        # Dosyayı kaydet
        with open("pdf_to_qa_gemini.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ API anahtarı başarıyla kaydedildi!")
        return True
        
    except Exception as e:
        print(f"❌ Kaydetme hatası: {e}")
        return False

def test_api_connection():
    """API bağlantısını test eder"""
    print("\n🧪 API Bağlantı Testi")
    print("-" * 25)
    
    try:
        import sys
        sys.path.append('.')
        from pdf_to_qa_gemini import PDFToQAConverter
        
        # Test için boş converter oluştur
        converter = PDFToQAConverter("test")
        print("✅ Sistem dosyaları çalışıyor")
        
        print("\n💡 Gerçek test için:")
        print("   python run_qa_generation.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ İmport hatası: {e}")
        return False
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def main():
    print("🚀 PDF'den Soru-Cevap Sistemi - API Kurulumu")
    print("=" * 50)
    
    # Mevcut durumu kontrol et
    print("\n🔍 Mevcut Durum Kontrolü:")
    api_configured = check_api_key_status()
    
    if api_configured:
        print("\n🎉 API anahtarı zaten ayarlanmış!")
        print("Sistemi test etmek için: python run_qa_generation.py")
        return
    
    # Talimatları göster
    show_api_setup_instructions()
    
    # Manuel kurulum seçeneği
    print("\n" + "="*50)
    setup_choice = input("\nAPI anahtarını şimdi ayarlamak istiyor musunuz? (e/h): ").lower()
    
    if setup_choice in ['e', 'evet', 'y', 'yes']:
        if manual_api_setup():
            test_api_connection()
            print("\n🎉 Kurulum tamamlandı!")
            print("\n📋 Sonraki Adımlar:")
            print("1. python run_qa_generation.py  # PDF'leri işle")
            print("2. python analyze_qa_data.py    # Verileri analiz et")
            print("3. python main.py               # Ana menü")
        else:
            print("\n❌ Kurulum başarısız!")
    else:
        print("\n📝 Manuel kurulum için yukarıdaki talimatları takip edin.")
    
    print(f"\n💡 Yardım için: README.md dosyasını inceleyin")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Kurulum iptal edildi.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
