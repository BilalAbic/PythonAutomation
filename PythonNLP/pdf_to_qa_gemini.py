# PDF'leri Gemini API kullanarak soru-cevap formatına dönüştürme
import fitz  # PyMuPDF
import json
import os
import time
import requests
from typing import List, Dict
import re
from random import choice

class PDFToQAConverter:
    def __init__(self, config_file: str = 'config.json'):
        """
        config_file: Yapılandırma dosyası yolu
        """
        self.load_config(config_file)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
    def load_config(self, config_file: str):
        """Yapılandırma dosyasını yükler"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # API anahtarlarını kontrol et
                if not config.get('api_keys'):
                    raise ValueError("API anahtarları bulunamadı")
                if not isinstance(config['api_keys'], list):
                    raise ValueError("API anahtarları liste formatında olmalı")
                if not all(isinstance(key, str) for key in config['api_keys']):
                    raise ValueError("Tüm API anahtarları metin formatında olmalı")
                if not all(len(key) > 20 for key in config['api_keys']):
                    raise ValueError("Geçersiz API anahtarı formatı")
                    
                self.api_keys = config['api_keys']
                self.retry_settings = config.get('retry_settings', {
                    "max_retries": 3,
                    "retry_delay": 5,
                    "rate_limit_delay": 10
                })
                self.chunk_settings = config.get('chunk_settings', {
                    "chunk_size": 3000,
                    "chunk_overlap": 200
                })
                
        except FileNotFoundError:
            print(f"❌ {config_file} dosyası bulunamadı!")
            print("Lütfen setup_qa_generator.py'yi çalıştırarak kurulumu tamamlayın.")
            raise
        except json.JSONDecodeError:
            print(f"❌ {config_file} dosyası geçerli bir JSON formatında değil!")
            raise
        except ValueError as e:
            print(f"❌ Yapılandırma hatası: {e}")
            print("Lütfen setup_qa_generator.py'yi çalıştırarak API anahtarlarını yeniden ekleyin.")
            raise
        except Exception as e:
            print(f"❌ Beklenmeyen bir hata oluştu: {e}")
            raise

    def get_random_api_key(self) -> str:
        """Rastgele bir API anahtarı döndürür"""
        return choice(self.api_keys)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF'den metin çıkarır"""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    page_text = page.get_text()
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"PDF okuma hatası {pdf_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Metni temizler ve düzenler"""
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        # Özel karakterleri temizle
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()

    def analyze_text_content(self, text: str) -> dict:
        """Metni analiz eder ve içerik özelliklerini belirler"""
        # Cümle sayısı
        sentences = text.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        
        # Anahtar kelime yoğunluğu
        keywords = ['beslenme', 'sağlık', 'vitamin', 'mineral', 'protein', 'karbonhidrat', 'yağ']
        keyword_density = sum(1 for word in text.lower().split() if word in keywords)
        
        # Bilgi yoğunluğu (sayılar, tarihler, ölçümler)
        info_density = len(re.findall(r'\d+', text))
        
        return {
            'sentence_count': sentence_count,
            'keyword_density': keyword_density,
            'info_density': info_density,
            'text_length': len(text)
        }

    def determine_question_count(self, content_analysis: dict) -> int:
        """İçerik analizine göre uygun soru sayısını belirler"""
        base_count = 3  # Minimum soru sayısı
        
        # Cümle sayısına göre artış
        if content_analysis['sentence_count'] > 10:
            base_count += 2
        
        # Anahtar kelime yoğunluğuna göre artış
        if content_analysis['keyword_density'] > 5:
            base_count += 1
        
        # Bilgi yoğunluğuna göre artış
        if content_analysis['info_density'] > 10:
            base_count += 1
        
        # Maksimum 10 soru
        return min(base_count, 10)

    def split_text_into_chunks(self, text: str, chunk_size: int = 3000) -> List[str]:
        """Metni küçük parçalara böler"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length <= chunk_size:
                current_chunk.append(word)
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def validate_qa_pair(self, qa_pair: Dict) -> bool:
        """Soru-cevap çiftinin kalitesini kontrol eder"""
        # Minimum uzunluk kontrolü
        if len(qa_pair['soru'].split()) < 3 or len(qa_pair['cevap'].split()) < 5:
            return False
        
        # Soru işareti kontrolü
        if '?' not in qa_pair['soru']:
            return False
        
        # Cevap/soru oranı kontrolü (cevap sorudan en az 2 kat uzun olmalı)
        if len(qa_pair['cevap']) < len(qa_pair['soru']) * 2:
            return False
        
        return True

    def generate_qa_with_gemini(self, text_chunk: str, pdf_name: str) -> List[Dict]:
        """Gemini API kullanarak soru-cevap çiftleri oluşturur"""
        content_analysis = self.analyze_text_content(text_chunk)
        question_count = self.determine_question_count(content_analysis)
        
        prompt = f"""
Aşağıdaki metin "{pdf_name}" dosyasından alınmıştır. Bu metinden beslenme ve sağlık konularında soru-cevap çiftleri oluştur.

Metin Analizi:
- Cümle Sayısı: {content_analysis['sentence_count']}
- Anahtar Kelime Yoğunluğu: {content_analysis['keyword_density']}
- Bilgi Yoğunluğu: {content_analysis['info_density']}

Kurallar:
1. Sorular Türkçe olmalı ve metindeki bilgilere dayanmalı
2. Cevaplar detaylı, bilgilendirici ve doğru olmalı
3. JSON formatında döndür
4. Her soru-cevap çifti şu formatta olmalı:
   {{"soru": "Soru metni", "cevap": "Cevap metni", "kaynak": "{pdf_name}"}}
5. Sadece metinde yeterli bilgi olan konulardan soru üret
6. Eğer metin yeterli bilgi içermiyorsa, daha az soru üret

Metin:
{text_chunk}

Lütfen sadece JSON formatında cevap ver, başka açıklama ekleme.
"""

        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        retry_count = 0
        while retry_count < self.retry_settings['max_retries']:
            try:
                api_key = self.get_random_api_key()
                response = requests.post(
                    f"{self.base_url}?key={api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']['parts'][0]['text']
                        
                        try:
                            if '```json' in content:
                                content = content.split('```json')[1].split('```')[0]
                            elif '```' in content:
                                content = content.split('```')[1].split('```')[0]
                            
                            qa_pairs = json.loads(content)
                            if isinstance(qa_pairs, list):
                                return [qa for qa in qa_pairs if self.validate_qa_pair(qa)]
                            else:
                                return [qa_pairs] if self.validate_qa_pair(qa_pairs) else []
                        except json.JSONDecodeError as e:
                            print(f"JSON parse hatası: {e}")
                            print(f"İçerik: {content}")
                            retry_count += 1
                            time.sleep(self.retry_settings['retry_delay'])
                            continue
                    else:
                        print("API'den boş cevap geldi")
                        retry_count += 1
                        time.sleep(self.retry_settings['retry_delay'])
                        continue
                
                elif response.status_code == 503:
                    print(f"Model aşırı yüklendi, farklı API anahtarı deneniyor...")
                    retry_count += 1
                    time.sleep(self.retry_settings['retry_delay'])
                    continue
                
                elif response.status_code == 429:
                    print(f"Rate limit aşıldı, bekleniyor...")
                    retry_count += 1
                    time.sleep(self.retry_settings['rate_limit_delay'])
                    continue
                
                else:
                    print(f"API hatası: {response.status_code} - {response.text}")
                    retry_count += 1
                    time.sleep(self.retry_settings['retry_delay'])
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Bağlantı hatası: {e}")
                retry_count += 1
                time.sleep(self.retry_settings['retry_delay'])
                continue
        
        print(f"Maksimum deneme sayısına ulaşıldı ({self.retry_settings['max_retries']})")
        return []

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Tek bir PDF'i işler"""
        pdf_name = os.path.basename(pdf_path)
        print(f"\n{pdf_name} işleniyor...")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Metinler çıkarılamadı: {pdf_name}")
            return []
        
        cleaned_text = self.clean_text(text)
        chunks = self.split_text_into_chunks(cleaned_text, self.chunk_settings['chunk_size'])
        print(f"{len(chunks)} parça halinde işlenecek")
        
        all_qa_pairs = []
        
        for i, chunk in enumerate(chunks):
            print(f"  Parça {i+1}/{len(chunks)} işleniyor...")
            
            content_analysis = self.analyze_text_content(chunk)
            if content_analysis['sentence_count'] < 3 or content_analysis['keyword_density'] < 2:
                print(f"  ⚠️  Parça {i+1} yeterli içerik içermiyor, atlanıyor...")
                continue
            
            qa_pairs = self.generate_qa_with_gemini(chunk, pdf_name)
            all_qa_pairs.extend(qa_pairs)
            
            # API limitleri için bekleme
            time.sleep(2)
        
        print(f"{pdf_name} tamamlandı. {len(all_qa_pairs)} soru-cevap çifti oluşturuldu.")
        return all_qa_pairs

    def process_all_pdfs(self, pdf_folder: str, output_file: str):
        """Tüm PDF'leri işler"""
        all_qa_data = []
        
        # PDF dosyalarını listele
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        print(f"Toplam {len(pdf_files)} PDF dosyası bulundu.")
        
        for i, pdf_file in enumerate(pdf_files):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f"\n[{i+1}/{len(pdf_files)}] {pdf_file} işleniyor...")
            
            qa_pairs = self.process_pdf(pdf_path)
            all_qa_data.extend(qa_pairs)
            
            # Her 5 PDF'den sonra ara kayıt yap
            if (i + 1) % 5 == 0:
                self.save_qa_data(all_qa_data, f"interim_{output_file}")
                print(f"Ara kayıt yapıldı: {len(all_qa_data)} soru-cevap çifti")
        
        # Final kayıt
        self.save_qa_data(all_qa_data, output_file)
        print(f"\nTüm işlem tamamlandı!")
        print(f"Toplam {len(all_qa_data)} soru-cevap çifti oluşturuldu.")
        print(f"Veriler {output_file} dosyasına kaydedildi.")

    def save_qa_data(self, qa_data: List[Dict], output_file: str):
        """Soru-cevap verilerini JSON dosyasına kaydeder"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, ensure_ascii=False, indent=2)

def main():
    """Ana fonksiyon"""
    print("🤖 PDF'den Soru-Cevap Üreticisi")
    print("=" * 40)
    
    # Sistem kontrolü
    print("🔍 Sistem kontrolü yapılıyor...")
    
    # PDF klasörünü kontrol et
    pdf_folder = "pdfs"
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
        print("✅ 'pdfs' klasörü oluşturuldu")
        print("\n⚠️ Lütfen PDF dosyalarını 'pdfs' klasörüne kopyalayın ve tekrar deneyin.")
        return
    
    # PDF dosyalarını say
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("❌ 'pdfs' klasöründe PDF dosyası bulunamadı!")
        return
    print(f"✅ {len(pdf_files)} PDF dosyası bulundu")
    
    # Config dosyasını kontrol et
    if not os.path.exists('config.json'):
        print("\n❌ config.json dosyası bulunamadı!")
        print("Lütfen setup_qa_generator.py'yi çalıştırarak kurulumu tamamlayın.")
        return
    
    # Config dosyasını yükle ve API anahtarlarını kontrol et
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not config.get('api_keys'):
                print("\n❌ config.json dosyasında API anahtarı bulunamadı!")
                print("Lütfen setup_qa_generator.py'yi çalıştırarak API anahtarlarını ekleyin.")
                return
    except Exception as e:
        print(f"\n❌ config.json dosyası okuma hatası: {e}")
        return
    
    # Kullanıcıya bilgi ver
    print("\n⚠️  Bu işlem uzun sürebilir ve internet bağlantısı gerektirir!")
    response = input("Devam etmek istiyor musunuz? (e/h): ")
    if response.lower() != 'e':
        return
    
    # Converter'ı başlat ve işlemi yürüt
    converter = PDFToQAConverter()
    output_file = "qa_output.json"
    converter.process_all_pdfs(pdf_folder, output_file)

if __name__ == "__main__":
    main()
