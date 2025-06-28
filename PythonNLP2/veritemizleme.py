import re
import json

# Çıkarılan metni temizleme

def clean_text(raw_text):
    """Metni temizlemek ve düzenlemek için bir fonksiyon."""
    # Gereksiz boşlukları kaldır
    cleaned_text = re.sub(r"\s+", " ", raw_text.strip())
    # Özel karakterleri kaldır
    cleaned_text = re.sub(r"[^\w\s.,!?\-]", "", cleaned_text)
    return cleaned_text

# Soru-Cevap çiftleri oluşturma (isteğe bağlı)
def generate_question_answer_pairs(text):
    """Metni analiz ederek örnek soru-cevap çiftleri oluşturur."""
    sentences = text.split(".")  # Noktadan bölerek cümleleri al
    qa_pairs = []
    for sentence in sentences:
        if len(sentence.split()) > 5:  # Uzun cümlelerden soru oluştur
            question = f"Bu cümlede ne anlatılıyor: {sentence.strip()}?"
            answer = sentence.strip()
            qa_pairs.append({"question": question, "answer": answer})
    return qa_pairs

# JSON olarak kaydetme
def save_as_json(data, output_path):
    """Veriyi JSON formatında kaydeder."""
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Ana işlem
input_path = "combined_output.json"  # Önceki adımdaki çıktı dosyası
output_cleaned_path = "cleaned_text.json"  # Temizlenmiş metin için
output_qa_path = "qa_pairs.json"  # Soru-cevap çiftleri için

# Çıkarılan metni yükle
with open(input_path, "r", encoding="utf-8") as file:
    extracted_data = json.load(file)
    raw_text = extracted_data.get("content", "")

# Metni temizle
cleaned_text = clean_text(raw_text)

# Temizlenmiş metni kaydet
save_as_json({"cleaned_text": cleaned_text}, output_cleaned_path)

# Soru-cevap çiftleri oluştur ve kaydet
qa_pairs = generate_question_answer_pairs(cleaned_text)
save_as_json(qa_pairs, output_qa_path)

print(f"Temizlenmiş metin {output_cleaned_path} dosyasına kaydedildi.")
print(f"Soru-cevap çiftleri {output_qa_path} dosyasına kaydedildi.")
