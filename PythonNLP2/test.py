import pandas as pd
import os

# CSV dosyalarının bulunduğu klasör
klasor_yolu = "csv_klasoru"

# Birleştirilmiş veriyi tutacak liste
birlesik_veri = []

# Klasördeki tüm CSV dosyalarını oku
for dosya in os.listdir(klasor_yolu):
    if dosya.endswith(".csv"):  # Sadece .csv uzantılı dosyaları oku
        dosya_yolu = os.path.join(klasor_yolu, dosya)
        try:
            df = pd.read_csv(dosya_yolu)  # CSV dosyasını oku
            birlesik_veri.append(df)  # Listeye ekle
            print(f"{dosya} başarıyla okundu.")
        except Exception as e:
            print(f"{dosya} dosyasını okurken hata oluştu: {e}")

# Eğer liste boşsa kullanıcıyı bilgilendir
if not birlesik_veri:
    print("Birleştirilecek dosya bulunamadı. Lütfen klasör yolunu ve dosyaları kontrol edin.")
else:
    # Tüm DataFrame'leri birleştir
    final_df = pd.concat(birlesik_veri, ignore_index=True)
    # Sonuçları yeni bir CSV dosyasına yaz
    final_df.to_csv("birlesik_verii.csv", index=False)
    print("Dosyalar başarıyla birleştirildi ve 'birlesik_veri.csv' dosyasına kaydedildi!")
