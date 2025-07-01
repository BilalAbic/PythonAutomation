# PDF'leri Gemini API kullanarak soru-cevap formatına dönüştürme
import fitz  # PyMuPDF
import json
import os
import time
import requests
from typing import List, Dict
import re

class PDFToQAConverter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        
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

    def generate_qa_with_gemini(self, text_chunk: str, pdf_name: str) -> List[Dict]:
        """Gemini API kullanarak soru-cevap çiftleri oluşturur"""
        prompt = f"""
Aşağıdaki metin "{pdf_name}" dosyasından alınmıştır. Bu metinden beslenme ve sağlık konularında 5-8 adet soru-cevap çifti oluştur.

Kurallar:
1. Sorular Türkçe olmalı ve metindeki bilgilere dayanmalı
2. Cevaplar detaylı, bilgilendirici ve doğru olmalı
3. JSON formatında döndür
4. Her soru-cevap çifti şu formatta olmalı:
   {{"soru": "Soru metni", "cevap": "Cevap metni", "kaynak": "{pdf_name}"}}

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
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # JSON içeriğini çıkar
                    try:
                        # Eğer ```json ile başlıyorsa temizle
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0]
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0]
                        
                        qa_pairs = json.loads(content)
                        if isinstance(qa_pairs, list):
                            return qa_pairs
                        else:
                            return [qa_pairs]
                    except json.JSONDecodeError as e:
                        print(f"JSON parse hatası: {e}")
                        print(f"İçerik: {content}")
                        return []
                else:
                    print("API'den boş cevap geldi")
                    return []
            else:
                print(f"API hatası: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"API isteği hatası: {e}")
            return []

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Tek bir PDF'i işler"""
        pdf_name = os.path.basename(pdf_path)
        print(f"\n{pdf_name} işleniyor...")
        
        # PDF'den metin çıkar
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Metinler çıkarılamadı: {pdf_name}")
            return []
        
        # Metni temizle
        cleaned_text = self.clean_text(text)
        
        # Metni parçalara böl
        chunks = self.split_text_into_chunks(cleaned_text)
        print(f"{len(chunks)} parça halinde işlenecek")
        
        all_qa_pairs = []
        
        for i, chunk in enumerate(chunks):
            print(f"  Parça {i+1}/{len(chunks)} işleniyor...")
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
    # Gemini API anahtarını buraya girin
    API_KEY = ""
    
    if API_KEY == "":
        print("⚠️  Lütfen API anahtarınızı girin!")
        print("Google AI Studio'dan API anahtarı alabilirsiniz: https://makersuite.google.com/app/apikey")
        return
    
    # Klasör yolları
    pdf_folder = "pdfs"
    output_file = "pdf_qa_pairs.json"
    
    # Converter'ı başlat
    converter = PDFToQAConverter(API_KEY)
    
    # Tüm PDF'leri işle
    converter.process_all_pdfs(pdf_folder, output_file)

if __name__ == "__main__":
    main()
