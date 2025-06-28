import json
import os
import re
from sentence_transformers import SentenceTransformer, util

def enrich_with_semantic_search(input_file_path='train.json', output_file_path='train_enriched.json'):
    """
    Veri setini anlamsal benzerlik kullanarak otomatik olarak etiketler.
    """
    print("Model yükleniyor... (Bu işlem ilk çalıştırmada biraz zaman alabilir)")
    # Türkçe için eğitilmiş, çok dilli ve güçlü bir model
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    print("Model yüklendi.")

    # Kategorileri ve onları temsil eden anahtar cümleleri tanımlıyoruz.
    # Bu listeyi projenize göre zenginleştirebilirsiniz.
    category_definitions = {
        "Obezite": "Kilo verme, şişmanlık ve vücut kitle indeksi hakkında bilgiler.",
        "Diyabet": "Şeker hastalığı, insülin direnci ve kan şekeri yönetimi ile ilgili konular.",
        "Kalp Sağlığı": "Kalp ve damar hastalıkları, tansiyon, kolesterol ve felç riskleri.",
        "Egzersiz ve Fiziksel Aktivite": "Spor, egzersiz programları, yürüme, hareketli yaşam ve fiziksel uygunluk.",
        "Anne & Bebek Sağlığı": "Hamilelik, gebelik, emzirme, anne sütü, bebek beslenmesi ve doğum sonrası dönem.",
        "Çocuk ve Ergen Beslenmesi": "Okul çağı çocukları, ergenler ve onların sağlıklı büyüme ve gelişimi.",
        "Gıda Güvenliği ve Hijyen": "Besinlerin doğru saklanması, pişirilmesi, bakteri ve gıda zehirlenmelerinden korunma.",
        "Vitaminler ve Mineraller": "Demir, kalsiyum, D vitamini gibi mikro besinlerin faydaları ve eksiklikleri.",
        "Genel Beslenme": "Yeterli ve dengeli beslenme, öğünler, porsiyonlar ve sağlıklı yaşam ilkeleri."
    }

    # Hedef kitle için anahtar kelimeler
    audience_keywords = {
        "Çocuk": ["çocuk", "bebek", "okul çağı"],
        "Ergen": ["ergen", "adolesan", "genç"],
        "Gebe": ["gebe", "hamile", "gebelik"],
        "Emziren Anne": ["emziren", "emziklilik", "anne sütü"],
        "Yaşlı": ["yaşlı", "yaşlılık", "menopoz"],
        "Sporcu": ["sporcu", "performans", "antrenman"],
        "Diyabet Hastası": ["diyabet", "şeker hastası"]
    }

    categories = list(category_definitions.keys())
    category_sentences = list(category_definitions.values())
    
    # Kategori tanımlarının vektörlerini (embedding) önceden hesaplıyoruz.
    print("Kategori vektörleri oluşturuluyor...")
    category_embeddings = model.encode(category_sentences, convert_to_tensor=True)
    print("Kategori vektörleri hazır.")

    # Ana veri setini yüklüyoruz
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Hata: '{input_file_path}' dosyası bulunamadı.")
        return

    enriched_data = []
    print(f"{len(data)} adet girdi işlenmeye başlanıyor...")

    for i, entry in enumerate(data):
        soru_text = entry.get('soru', '')
        if not soru_text:
            continue

        # Sorunun vektörünü hesaplıyoruz
        soru_embedding = model.encode(soru_text, convert_to_tensor=True)
        
        # Kosinüs benzerliği ile en yakın kategoriyi buluyoruz
        cos_scores = util.pytorch_cos_sim(soru_embedding, category_embeddings)[0]
        top_result_index = cos_scores.argmax()
        
        best_category = categories[top_result_index]
        
        # Hedef kitleyi anahtar kelimelerle belirliyoruz
        text_to_analyze = (soru_text + ' ' + entry.get('cevap', '')).lower()
        found_audiences = set()
        for audience, keywords in audience_keywords.items():
            if any(re.search(r'\b' + kw.lower() + r'\b', text_to_analyze) for kw in keywords):
                found_audiences.add(audience)

        # Zenginleştirilmiş girdiyi oluşturuyoruz
        enriched_entry = entry.copy()
        enriched_entry['id'] = f"DATA-{i+1:04d}"
        enriched_entry['kategori'] = best_category
        enriched_entry['hedef_kitle'] = list(found_audiences) if found_audiences else ["Genel"]
        
        enriched_data.append(enriched_entry)
        
        if (i + 1) % 100 == 0:
            print(f"{i + 1} / {len(data)} işlendi...")

    # Sonucu dosyaya yazdırıyoruz
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)

    print(f"İşlem tamamlandı! Zenginleştirilmiş veri '{output_file_path}' dosyasına kaydedildi.")

# Scripti çalıştır
if __name__ == "__main__":
    enrich_with_semantic_search()