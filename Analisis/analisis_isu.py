import json
import re
import sys
import logging
import argparse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("./Output/proses.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)


# PARSE ARGUMEN
parser = argparse.ArgumentParser(description="Analisis isu per daerah & tema")
parser.add_argument("--daerah", type=str, help="Nama daerah spesifik yang mau dianalisis")
parser.add_argument("--tema", type=str, help="Nama tema spesifik yang mau dianalisis")
args = parser.parse_args()


# LOAD DATA PEMDA
try:
    with open('./Data/data_pemda.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    logging.info("File data_pemda.json berhasil dimuat.")
except FileNotFoundError:
    logging.error("File data_pemda.json tidak ditemukan.")
    sys.exit()


# LOAD KAMUS TEMA
try:
    with open('./Data/kamus_tema.json', 'r', encoding='utf-8') as f:
        kamus_raw = json.load(f)
    logging.info("File kamus_tema.json berhasil dimuat.")
except FileNotFoundError:
    logging.error("File kamus_tema.json tidak ditemukan.")
    sys.exit()

# Ubah format jadi dict {id: {"nama":..., "keywords":...}}
common_themes = {
    tema["id"]: {
        "nama": tema["nama"],
        "keywords": tema["keywords"]
    }
    for tema in kamus_raw["klasifikasi_topik"]
}

# Mapping id -> nama
themes_list = {
    tema_id: tema_data["nama"]
    for tema_id, tema_data in common_themes.items()
}

# Kalau user pilih tema, cek id temanya
tema_filter_id = None
if args.tema:
    tema_filter_id = next((tid for tid, tnama in themes_list.items() if tnama.lower() == args.tema.lower()), None)
    if tema_filter_id is None:
        logging.error(f"Tema '{args.tema}' tidak ditemukan dalam kamus tema.")
        sys.exit()


# 3. FUNGSI UTILITAS
def get_issue_themes(text):
    """Deteksi tema apa aja yg muncul di text berdasarkan keywords"""
    text_lower = text.lower()
    matched_themes = set()
    for tema_id, tema_data in common_themes.items():
        if any(isinstance(kw, str) and kw in text_lower for kw in tema_data["keywords"]):
            matched_themes.add(tema_id)
    return matched_themes


def explain_similarity(original_text_clean, matched_text_clean):
    """Kasih penjelasan similarity berdasarkan keyword sama"""
    original_text_lower = original_text_clean.lower()
    matched_text_lower = matched_text_clean.lower()
    found_themes_in_both = set()
    
    for tema_id, tema_data in common_themes.items():
        keywords = tema_data["keywords"]
        if any(kw in original_text_lower for kw in keywords) and any(kw in matched_text_lower for kw in keywords):
            found_themes_in_both.add(tema_data["nama"])  
    
    if found_themes_in_both:
        return "Fokus tema umum yang terdeteksi: " + ", ".join(sorted(found_themes_in_both)) + "."
    else:
        return "Kecocokan berdasarkan makna kalimat secara umum."

# PERSIAPAN DATA ISU
all_individual_issues = []
for item in data['data']:
    kodepemda = item['kodepemda']
    pemda_name = item['namapemda']
    for issue_text in item['data']:
        if issue_text and issue_text.strip():
            issue_clean_text = re.sub(r'^\d+\.\s*', '', issue_text).strip()
            all_individual_issues.append({
                "pemda_name": pemda_name,
                "kodepemda": kodepemda,   
                "issue_original_text": issue_text,
                "issue_clean_text": issue_clean_text
            })

kota_acuan_pembanding = sorted(list(set(item['pemda_name'] for item in all_individual_issues)))

logging.info(f"Total isu individu: {len(all_individual_issues)}")
logging.info(f"Total daerah unik: {len(kota_acuan_pembanding)}")
logging.info(f"Total tema: {len(themes_list)}")

# LOAD MODEL SEMANTIK
logging.info("📦 Memuat model semantik...")
try:
    model = SentenceTransformer('intfloat/multilingual-e5-large') #paraphrase-multilingual-mpnet-base-v2   Model yang disarankan karena ringan.
    logging.info("✅ Model berhasil dimuat.")
except Exception as e:
    logging.critical(f"Gagal memuat model: {e}")
    sys.exit()

logging.info("🔄 Memproses embedding isu...")
individual_issue_texts = [item['issue_clean_text'] for item in all_individual_issues]
individual_issue_embeddings = model.encode(individual_issue_texts, convert_to_tensor=False, show_progress_bar=True)

logging.info("📊 Menghitung matriks similaritas...")
similarity_matrix_individual = cosine_similarity(individual_issue_embeddings)

# PROSES ANALISIS
relevance_threshold = 0.5
hasil_analisis = []

logging.info("🚀 Memulai analisis otomatis...")

# Filter daerah
daerah_terpilih = kota_acuan_pembanding
if args.daerah:
    if args.daerah not in kota_acuan_pembanding:
        logging.error(f"Daerah '{args.daerah}' tidak ditemukan dalam data.")
        sys.exit()
    daerah_terpilih = [args.daerah]

for daerah_idx, daerah in enumerate(daerah_terpilih, start=1):
    logging.info(f"[{daerah_idx}/{len(daerah_terpilih)}] 📍 Memproses daerah: {daerah}")

    for tema_id, tema_nama in themes_list.items():
        if tema_filter_id and tema_id != tema_filter_id:
            continue  # skip kalau bukan tema yang diminta

        isu_tersaring = [
            (i, issue_data)
            for i, issue_data in enumerate(all_individual_issues)
            if issue_data['pemda_name'] == daerah and tema_id in get_issue_themes(issue_data['issue_clean_text'])
        ]

        if not isu_tersaring:
            continue

        logging.info(f"   - Tema '{tema_nama}': {len(isu_tersaring)} isu ditemukan")

        for indeks_isu_terpilih, isu_terpilih_data in isu_tersaring:
            best_match_per_region = {}
            for j, isu_pembanding in enumerate(all_individual_issues):
                if indeks_isu_terpilih == j or isu_pembanding['pemda_name'] == daerah:
                    continue

                skor = float(similarity_matrix_individual[indeks_isu_terpilih][j])
                if skor < relevance_threshold:
                    continue  # skip hasil jelek

                nama_pemda_pembanding = isu_pembanding['pemda_name']
                if nama_pemda_pembanding not in best_match_per_region or skor > best_match_per_region[nama_pemda_pembanding]['skor']:
                    best_match_per_region[nama_pemda_pembanding] = {
                        'pemda_pembanding': nama_pemda_pembanding,
                        'isu_pembanding': isu_pembanding['issue_original_text'],
                        'skor': skor,
                        'analisis_tema': explain_similarity(
                            isu_terpilih_data['issue_clean_text'],
                            isu_pembanding['issue_clean_text']
                        ),
                        'kodepemda_pembanding': isu_pembanding['kodepemda']
                    }

            if best_match_per_region:
                hasil_analisis.append({
                    'daerah_asal': daerah,
                    'kodepemda_asal': isu_terpilih_data['kodepemda'],   
                    'tema_id': tema_id,
                    'tema_nama': tema_nama,
                    'isu_asal': isu_terpilih_data['issue_original_text'],
                    'peringkat_kemiripan': sorted([
                        {
                            'pemda_pembanding': v['pemda_pembanding'],
                            'kodepemda_pembanding': v['kodepemda_pembanding'],
                            'isu_pembanding': v['isu_pembanding'],
                            'skor': v['skor'],
                            'analisis_tema': v['analisis_tema']
                        }
                        for v in best_match_per_region.values()
                    ], key=lambda x: x['skor'], reverse=True)
                })

logging.info("✅ Analisis selesai, menyimpan hasil...")

# SIMPAN HASIL
try:
    with open('./Output/hasil.json', 'w', encoding='utf-8') as f:
        json.dump(hasil_analisis, f, ensure_ascii=False, indent=2)
    logging.info("📂 Hasil analisis tersimpan di ./Output/hasil.json")
except Exception as e:
    logging.error(f"Gagal menyimpan file hasil.json: {e}")
