import json
import os
import logging
from datetime import datetime

# Setup logging
LOG_FILE = os.path.join("Output", "proses.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Path ke file JSON
INPUT_FILE = os.path.join("Data", "data_klasifikasi.json")
OUTPUT_FOLDER = "Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def analisis_tema():
    logging.info("=== Mulai analisis tema ===")
    try:
        # Load file JSON
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info(f"Berhasil load file JSON: {INPUT_FILE}")
    except FileNotFoundError:
        logging.error(f"File {INPUT_FILE} tidak ditemukan.")
        print(f"❌ File {INPUT_FILE} tidak ditemukan.")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Gagal parse JSON: {e}")
        print("❌ File JSON tidak valid.")
        return

    # Ambil semua tema
    semua_tema = list(data.get("klasifikasi_tema", {}).keys())
    if not semua_tema:
        logging.warning("Tidak ada tema di file JSON.")
        print("⚠️ Tidak ada tema di file JSON.")
        return

    print("\nDaftar Tema Tersedia:")
    for idx, tema in enumerate(semua_tema, start=1):
        print(f"{idx}. {tema}")

    try:
        pilihan = int(input("\nPilih nomor tema: "))
        tema_terpilih = semua_tema[pilihan - 1]
        logging.info(f"Tema dipilih: {tema_terpilih}")
    except (ValueError, IndexError):
        logging.warning("Pilihan tidak valid.")
        print("❌ Pilihan tidak valid.")
        return

    tema_data = data["klasifikasi_tema"][tema_terpilih]
    hasil = {
        "tema": tema_terpilih,
        "jumlah_kegiatan": len(tema_data),
        "kegiatan": tema_data
    }

    output_path = os.path.join(OUTPUT_FOLDER, f"hasil_tema_{tema_terpilih}.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hasil, f, indent=4, ensure_ascii=False)
        logging.info(f"Hasil analisis disimpan ke {output_path}")
    except Exception as e:
        logging.error(f"Gagal simpan file hasil: {e}")
        print("❌ Gagal simpan file hasil.")
        return

    print(f"\n✅ Hasil analisis tema '{tema_terpilih}' disimpan ke: {output_path}")
    logging.info("=== Analisis tema selesai ===")

if __name__ == "__main__":
    analisis_tema()
