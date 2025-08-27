import json
import pandas as pd
import sys
import os

# LOAD KAMUS TEMA
kamus_path = './Data/kamus_tema.json'

try:
    with open(kamus_path, 'r', encoding='utf-8') as f:
        kamus_data = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: File {kamus_path} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    print(f"❌ Error: File {kamus_path} bukan JSON yang valid.")
    sys.exit()

# Ambil daftar tema dari "klasifikasi_topik"
if "klasifikasi_topik" not in kamus_data:
    print("❌ Struktur JSON tidak sesuai (tidak ada key 'klasifikasi_topik').")
    sys.exit()

THEMES = {item["nama"]: item["keywords"] for item in kamus_data["klasifikasi_topik"]}


# LOAD DATA PEMDA
data_path = './Data/data_pemda.json'

try:
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: File {data_path} tidak ditemukan.")
    sys.exit()
except json.JSONDecodeError:
    print(f"❌ Error: File {data_path} bukan JSON yang valid.")
    sys.exit()


# PILIH TEMA
print("\n📌 Daftar Tema yang tersedia:")
for idx, tema in enumerate(THEMES.keys(), start=1):
    print(f"{idx}. {tema}")

try:
    pilihan = int(input("\nMasukkan nomor tema yang ingin dianalisis: "))
    tema_utama = list(THEMES.keys())[pilihan - 1]
except (ValueError, IndexError):
    print("❌ Pilihan tidak valid.")
    sys.exit()

keywords_to_search = THEMES[tema_utama]

# PROSES ANALISIS PENYEBARAN
hasil_analisis = []
for item in raw_data['data']:
    nama_pemda = item['namapemda']
    list_program = item['data']

    jumlah_isu_tema = sum(
        1 for program in list_program
        if any(keyword.lower() in program.lower() for keyword in keywords_to_search)
    )

    hasil_analisis.append({
        'Nama_Pemda': nama_pemda,
        'Skor_Tema': jumlah_isu_tema
    })

# Urutkan berdasarkan skor
df_hasil_sorted = pd.DataFrame(hasil_analisis).sort_values(by='Skor_Tema', ascending=False)


# SIMPAN KE JSON
os.makedirs('./Output', exist_ok=True)
output_path = f'./Output/hasil_tema_{tema_utama.replace(" ", "_")}.json'

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hasil_analisis, f, ensure_ascii=False, indent=2)
    print(f"📂 Hasil analisis tersimpan di {output_path}")
except Exception as e:
    print(f"❌ Gagal menyimpan file: {e}")

# TAMPILKAN HASIL
print("\n📊 Hasil Analisis Penyebaran:")
print(df_hasil_sorted.to_string(index=False))
