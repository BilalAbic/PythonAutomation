import pandas as pd

# Dosyayı yükle
file_path = 'birlesik_verii.csv'
data = pd.read_csv(file_path)

# Tekrar eden verileri kontrol et
duplicated_rows = data[data.duplicated()]

# Tekrar eden veri sayısı
duplicated_count = duplicated_rows.shape[0]

duplicated_rows.head(), duplicated_count
