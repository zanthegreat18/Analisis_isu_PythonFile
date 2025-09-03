import json
import os

# Path ke file json
INPUT_FILE = os.path.join("Data", "data_klasifikasi.json")
OUTPUT_FOLDER = "Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def analisis_tema():
    # Load file JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ambil semua tema (seperti ekonomi,geopark,dll)
    semua_tema = list(data.get("klasifikasi_tema", {}).keys())
    
    if not semua_tema:
        print("⚠️ Tidak ada tema di file JSON.")
        return

    # Tampilkan daftar tema
    print("\nDaftar Tema Tersedia:")
    for idx, tema in enumerate(semua_tema, start=1):
        print(f"{idx}. {tema}")

    # Pilih tema
    try:
        pilihan = int(input("\nPilih nomor tema: "))
        tema_terpilih = semua_tema[pilihan - 1]
    except (ValueError, IndexError):
        print("❌ Pilihan tidak valid.")
        return

    # Ambil data kegiatan
    tema_data = data["klasifikasi_tema"][tema_terpilih]

    # Buat hasil analisis
    hasil = {
        "tema": tema_terpilih,
        "jumlah_kegiatan": len(tema_data),
        "kegiatan": tema_data
    }

    # Simpan ke JSON
    output_path = os.path.join(OUTPUT_FOLDER, f"hasil_tema_{tema_terpilih}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hasil, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Hasil analisis tema '{tema_terpilih}' disimpan ke: {output_path}")

if __name__ == "__main__":
    analisis_tema()
