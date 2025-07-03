import google.generativeai as genai
import json
import os
import time
import asyncio
from tqdm.asyncio import tqdm_asyncio # Eş zamanlı işlemler için tqdm

def load_api_keys():
    """Config dosyasından API anahtarlarını yükle"""
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('api_keys', [])
    else:
        print("⚠️ config.json bulunamadı! config_example.json'dan kopyalayın.")
        return []

# API keyleri config'den yükle
API_KEYS = load_api_keys()

INPUT_FILE = "train.json"
OUTPUT_FILE = "train_augmented.json"

# EŞ ZAMANLI İSTEK SAYISI: Aynı anda kaç API isteği gönderilecek?
# Genellikle API anahtarı sayınızla orantılı iyi bir değerdir. 4-10 arası idealdir.
MAX_CONCURRENT_REQUESTS = 5

# HATA DURUMUNDA YENİDEN DENEME SAYISI
MAX_RETRIES = 3

# Test için sadece ilk N veriyi işlemek isterseniz bu değeri değiştirin.
# Tüm veriyi işlemek için None yapın. Örn: PROCESS_LIMIT = 10
PROCESS_LIMIT = None
# -------------------------

def get_augmentation_prompt(soru, cevap):
    """Verilen soru ve cevap için kullanılacak olan Mega Prompt'u formatlar."""
    return f"""
PROMPT BAŞLANGICI

**ROL:** Sen, Türkçe dilbilgisine ve farklı konuşma tarzlarına hakim bir metin üreticisisin.
**GÖREV:** Sana verilen Orijinal Soru-Cevap çiftindeki soruyu, anlamını koruyarak ama tamamen farklı ifade tarzları kullanarak 10 YENİ VERSİYONUNU oluştur. Bu yeni sorular, gerçek bir insanın bir sağlık asistanıyla konuşurken kullanabileceği farklı tarzları yansıtmalıdır.

**YENİ SORU VERSİYONLARI İÇİN KURALLAR:**
1.  **Kişisel Senaryo (2 adet):** Sanki bir kullanıcı kendi başından geçen bir olayı anlatıp soru soruyormuş gibi yaz.
2.  **Samimi/Günlük Dil (2 adet):** Daha rahat, günlük bir konuşma dili kullan.
3.  **Basit ve Direkt (2 adet):** Soruyu çok daha basit ve net bir şekilde ifade et.
4.  **Yazım Hatalı (2 adet):** Birkaç harf hatası veya eksik karakter içeren, gerçekçi yazım hataları yap.
5.  **Farklı Soru Kökü (2 adet):** "... nedir?" yerine "... hakkında bilgi verir misin?", "... nasıl yapılır?" gibi farklı soru yapıları kullan.

**ÇIKTI FORMATI:** Tüm yeni soruları bir JSON listesi olarak ver. Her eleman, yeni soruyu ve orijinal cevabı içermeli. Sadece JSON listesini ver, başka hiçbir açıklama ekleme.

---
**İŞLENECEK VERİ:**

**Orijinal Soru:**
"{soru}"

**Orijinal Cevap:**
"{cevap}"
---

PROMPT SONU
"""

async def process_entry_async(entry, api_key, semaphore):
    """
    Tek bir veri girdisini eş zamanlı olarak işler ve API'ye gönderir.
    Semaphore, aynı anda çalışan görev sayısını sınırlar.
    """
    async with semaphore: # Aynı anda çalışan görev sayısını limitle
        original_soru = entry.get('soru')
        original_cevap = entry.get('cevap')

        if not original_soru or not original_cevap:
            return []

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = get_augmentation_prompt(original_soru, original_cevap)

        for attempt in range(MAX_RETRIES):
            try:
                # Eş zamanlı (asynchronous) API çağrısı
                response = await model.generate_content_async(prompt)
                
                response_text = response.text
                # JSON'u daha güvenilir bir şekilde ayıklamak için ```json ... ``` bloğunu arayalım
                if '```json' in response_text:
                    json_start = response_text.find('```json\n') + len('```json\n')
                    json_end = response_text.rfind('```')
                else: # Eski yöntemle devam et
                    json_start = response_text.find('[')
                    json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_string = response_text[json_start:json_end]
                    new_qa_pairs = json.loads(json_string)
                    # Gelen verinin bir liste olduğundan emin olalım
                    if isinstance(new_qa_pairs, list):
                        return new_qa_pairs
                    else:
                         print(f"UYARI: Model liste formatında JSON döndürmedi. Soru: '{original_soru[:30]}...'. Yeniden denenecek...")
                         continue
                else:
                    # Model geçerli JSON döndürmediyse, bu denemeyi başarısız say
                    print(f"UYARI: Geçersiz JSON formatı. Soru: '{original_soru[:30]}...'. Yeniden denenecek...")
                    continue # Döngünün bir sonraki adımına geç

            except json.JSONDecodeError:
                print(f"UYARI: JSON parse hatası. Modelin çıktısı geçerli değil. Soru: '{original_soru[:30]}...'. Yeniden denenecek...")
                await asyncio.sleep(1) # Kısa bir bekleme süresi
                continue

            except Exception as e:
                # Rate limit hatası (ResourceExhausted) veya başka bir API hatası
                if "Resource has been exhausted" in str(e) or "429" in str(e):
                    print(f"UYARI: API Limiti aşıldı (Anahtar: ...{api_key[-4:]}). "
                          f"{(attempt + 1) * 5} saniye bekleniyor. Deneme {attempt + 1}/{MAX_RETRIES}")
                    await asyncio.sleep((attempt + 1) * 5) # Üstel bekleme
                else:
                    print(f"HATA: Beklenmedik bir sorun oluştu. Soru: '{original_soru[:30]}...'. Hata: {e}")
                    # Diğer hatalarda hemen bir sonraki denemeye geç
                    await asyncio.sleep(2)
        
        print(f"BAŞARISIZ: Soru '{original_soru[:50]}...' {MAX_RETRIES} deneme sonunda işlenemedi.")
        return [] # Tüm denemeler başarısız olursa boş liste döndür


async def main_orchestrator():
    """
    Tüm veri çoğaltma sürecini yönetir, görevleri oluşturur, çalıştırır
    ve yarıda kalırsa kaldığı yerden devam eder.
    """
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except FileNotFoundError:
        print(f"HATA: '{INPUT_FILE}' bulunamadı.")
        return
    except json.JSONDecodeError:
        print(f"HATA: '{INPUT_FILE}' geçerli bir JSON dosyası değil.")
        return

    # --- Kaldığı Yerden Devam Etme Mantığı ---
    previously_processed_data = []
    processed_original_questions = set()
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                # Daha önce işlenmiş veriyi güvenli bir şekilde yükle
                content = f.read()
                if content:
                    previously_processed_data = json.loads(content)
                    # Orijinal verileri ayırt etmek için, orijinal veri setindeki soruları referans alacağız.
                    original_questions_set = {entry['soru'] for entry in original_data}
                    
                    # Çıktı dosyasında bulunan ve orijinal veri setinde de olan soruları "işlenmiş" kabul et
                    for entry in previously_processed_data:
                        if entry['soru'] in original_questions_set:
                            processed_original_questions.add(entry['soru'])
            
            if processed_original_questions:
                print(f"Bilgi: Önceki çalıştırmadan kalan '{OUTPUT_FILE}' dosyası bulundu.")
                print(f"{len(processed_original_questions)} orijinal soru daha önce işlenmiş ve tekrar işlenmeyecek.")

        except json.JSONDecodeError:
            print(f"UYARI: '{OUTPUT_FILE}' dosyası bozuk veya geçersiz JSON içeriyor. "
                  "Güvenlik için sıfırdan başlanacak. Dosyayı kontrol edin veya silin.")
            previously_processed_data = [] # Veriyi sıfırla
            processed_original_questions = set()
        except Exception as e:
            print(f"HATA: '{OUTPUT_FILE}' okunurken bir hata oluştu: {e}")
            return


    # Sadece işlenmemiş verileri filtrele
    data_to_process_full = [
        entry for entry in original_data 
        if entry['soru'] not in processed_original_questions
    ]

    if not data_to_process_full:
        print("\n--- İŞLEM TAMAMLANDI ---")
        print(f"Tüm orijinal veriler zaten işlenmiş görünüyor.")
        print(f"Toplam Veri Sayısı: {len(previously_processed_data)}")
        print(f"Sonuçlar '{OUTPUT_FILE}' dosyasında güncel.")
        return

    # İşlem limitini uygula
    data_to_process = data_to_process_full[:PROCESS_LIMIT] if PROCESS_LIMIT is not None else data_to_process_full
    
    print(f"\nToplam {len(original_data)} orijinal girdiden {len(data_to_process_full)} tanesi işlenecek.")
    if PROCESS_LIMIT is not None:
        print(f"İşlem limiti ({PROCESS_LIMIT}) uygulandı. Bu çalıştırmada {len(data_to_process)} veri işlenecek.")

    print(f"Kullanılacak API Anahtarı Sayısı: {len(API_KEYS)}")
    print(f"Maksimum Eş Zamanlı İstek: {MAX_CONCURRENT_REQUESTS}")
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    tasks = []
    for i, entry in enumerate(data_to_process):
        api_key_for_task = API_KEYS[i % len(API_KEYS)]
        task = process_entry_async(entry, api_key_for_task, semaphore)
        tasks.append(task)

    # tqdm_asyncio.gather ile görevleri çalıştır ve ilerleme çubuğunu göster
    all_new_results = await tqdm_asyncio.gather(*tasks, desc="Yeni Veriler İşleniyor")
    
    # Yeni üretilen Soru-Cevap çiftlerini tek bir listede topla
    newly_augmented_pairs = [item for sublist in all_new_results for item in sublist]
    
    # Orijinal veriyi (sadece bu turda işlenenleri) ve yeni üretilen veriyi birleştir
    # ÖNEMLİ: `data_to_process` listesi, bu turda işlenen orijinal girdileri içerir.
    data_from_this_run = data_to_process + newly_augmented_pairs

    # Sonuçları daha önce işlenmiş verilerle birleştir
    final_data = previously_processed_data + data_from_this_run

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("\n--- İŞLEM TAMAMLANDI ---")
    print(f"Önceki Veri Sayısı: {len(previously_processed_data)}")
    print(f"Bu Çalıştırmada İşlenen Orijinal Veri: {len(data_to_process)}")
    print(f"Bu Çalıştırmada Yeni Üretilen Veri: {len(newly_augmented_pairs)}")
    print(f"Toplam Veri Sayısı: {len(final_data)}")
    print(f"Tüm sonuçlar '{OUTPUT_FILE}' dosyasına kaydedildi.")


if __name__ == "__main__":
    if not API_KEYS or "AIzaSyCtouTxAmnxmHGStK_nlRjBr_xBVpCz-L0" in API_KEYS[0]:
        print("LÜTFEN KODUN İÇİNDEKİ `API_KEYS` LİSTESİNİ KENDİ ANAHTARLARINIZLA GÜNCELLEYİN.")
    else:
        asyncio.run(main_orchestrator())