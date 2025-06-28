import fitz  # PyMuPDF
import json
import os

# PDF'den metin çıkarma
def extract_text_with_pymupdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            # Sayfa üzerindeki metni çıkar
            text += page.get_text()
    return text

# Çoklu PDF işleme
def process_multiple_pdfs(pdf_folder):
    combined_text = ""
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"{filename} işleniyor...")
            combined_text += extract_text_with_pymupdf(pdf_path) + "\n"
    return combined_text

# JSON olarak kaydetme
def save_text_as_json(text, output_path):
    data = {"content": text}
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Ana işlem
pdf_folder = "pdfs"  # PDF dosyalarının bulunduğu klasör
output_path = "combined_output.json"  # Çıktının kaydedileceği yol

# PDF'leri işle ve kaydet
combined_text = process_multiple_pdfs(pdf_folder)
save_text_as_json(combined_text, output_path)

print(f"Veriler {output_path} dosyasına kaydedildi.")
