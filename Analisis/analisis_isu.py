import json
import re
import sys
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,  # level minimal log yang mau ditampilin
    format="%(asctime)s - %(levelname)s - %(message)s",  # format log
    handlers=[
        logging.FileHandler("./Output/proses.log", encoding="utf-8"),  # simpan log ke file
        logging.StreamHandler(sys.stdout)  # tetep nampilin ke console
    ]
)

# 1. LOAD DATA & KAMUS TEMA
try:
    with open('./Data/data_pemda.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    logging.info("File data_pemda.json berhasil dimuat.")
except FileNotFoundError:
    logging.error("File data_pemda.json tidak ditemukan.")
    sys.exit()

try:
    with open('./Data/kamus_tema.json', 'r', encoding='utf-8') as f:
        common_themes = json.load(f)
    logging.info("File kamus_tema.json berhasil dimuat.")
except FileNotFoundError:
    logging.error("File kamus_tema.json tidak ditemukan.")
    sys.exit()


# 2. FUNGSI UTILITAS
def get_issue_themes(text):
    text_lower = text.lower()
    matched_themes = set()
    for theme, keywords in common_themes.items():
        if any(kw in text_lower for kw in keywords):
            matched_themes.add(theme)
    return matched_themes


def explain_similarity(original_text_clean, matched_text_clean):
    original_text_lower = original_text_clean.lower()
    matched_text_lower = matched_text_clean.lower()
    found_themes_in_both = set()
    for theme, keywords in common_themes.items():
        original_has_keyword = any(kw in original_text_lower for kw in keywords)
        matched_has_keyword = any(kw in matched_text_lower for kw in keywords)
        if original_has_keyword and matched_has_keyword:
            found_themes_in_both.add(theme)
    if found_themes_in_both:
        return "Fokus tema umum yang terdeteksi: " + ", ".join(sorted(list(found_themes_in_both))) + "."
    else:
        return "Kecocokan berdasarkan makna kalimat secara umum."


# 3. PERSIAPAN DATA ISU
all_individual_issues = []
for item in data['data']:
    pemda_name = item['namapemda']
    for issue_text in item['data']:
        if issue_text and issue_text.strip():
            issue_clean_text = re.sub(r'^\d+\.\s*', '', issue_text).strip()
            all_individual_issues.append({
                "pemda_name": pemda_name,
                "issue_original_text": issue_text,
                "issue_clean_text": issue_clean_text
            })

kota_acuan_pembanding = sorted(list(set(item['pemda_name'] for item in all_individual_issues)))
themes_list = sorted(list(common_themes.keys()))

logging.info(f"Total isu individu: {len(all_individual_issues)}")
logging.info(f"Total daerah unik: {len(kota_acuan_pembanding)}")
logging.info(f"Total tema: {len(themes_list)}")


# 4. LOAD MODEL SEMANTIK
logging.info("📦 Memuat model semantik...")
try:
    model = SentenceTransformer('intfloat/multilingual-e5-large')
    logging.info("✅ Model berhasil dimuat.")
except Exception as e:
    logging.critical(f"Gagal memuat model: {e}")
    sys.exit()

logging.info("🔄 Memproses embedding isu...")
individual_issue_texts = [item['issue_clean_text'] for item in all_individual_issues]
individual_issue_embeddings = model.encode(individual_issue_texts, convert_to_tensor=False, show_progress_bar=True)

logging.info("📊 Menghitung matriks similaritas...")
similarity_matrix_individual = cosine_similarity(individual_issue_embeddings)


# 5. PROSES ANALISIS 
relevance_threshold = 0.5
hasil_analisis = []

logging.info("🚀 Memulai analisis otomatis...")
for daerah_idx, daerah in enumerate(kota_acuan_pembanding, start=1):
    logging.info(f"[{daerah_idx}/{len(kota_acuan_pembanding)}] 📍 Memproses daerah: {daerah}")

    for tema_idx, tema in enumerate(themes_list, start=1):
        isu_tersaring = [
            (i, issue_data)
            for i, issue_data in enumerate(all_individual_issues)
            if issue_data['pemda_name'] == daerah and tema in get_issue_themes(issue_data['issue_clean_text'])
        ]

        if not isu_tersaring:
            continue

        logging.info(f"   - ({tema_idx}/{len(themes_list)}) Tema '{tema}': {len(isu_tersaring)} isu ditemukan")

        for indeks_isu_terpilih, isu_terpilih_data in isu_tersaring:
            best_match_per_region = {}
            for j, isu_pembanding in enumerate(all_individual_issues):
                if indeks_isu_terpilih == j or isu_pembanding['pemda_name'] == daerah:
                    continue

                skor = float(similarity_matrix_individual[indeks_isu_terpilih][j])
                nama_pemda_pembanding = isu_pembanding['pemda_name']

                if nama_pemda_pembanding not in best_match_per_region or skor > best_match_per_region[nama_pemda_pembanding]['skor']:
                    best_match_per_region[nama_pemda_pembanding] = {
                        'pemda_pembanding': nama_pemda_pembanding,
                        'isu_pembanding': isu_pembanding['issue_original_text'],
                        'skor': skor,
                        'analisis_tema': explain_similarity(
                            isu_terpilih_data['issue_clean_text'],
                            isu_pembanding['issue_clean_text']
                        )
                    }

            hasil_analisis.append({
                'daerah_asal': daerah,
                'tema': tema,
                'isu_asal': isu_terpilih_data['issue_original_text'],
                'peringkat_kemiripan': sorted(best_match_per_region.values(), key=lambda x: x['skor'], reverse=True)
            })

logging.info("✅ Analisis selesai, menyimpan hasil...")


# 6. SIMPAN HASIL 
try:
    with open('./Output/hasil.json', 'w', encoding='utf-8') as f:
        json.dump(hasil_analisis, f, ensure_ascii=False, indent=2)
    logging.info("📂 Hasil analisis tersimpan di ./Output/hasil.json")
except Exception as e:
    logging.error(f"Gagal menyimpan file hasil.json: {e}")
