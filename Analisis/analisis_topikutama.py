import json
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load Kamus Tema dari file 
with open("Data/kamus_tema.json", "r", encoding="utf-8") as f:
    THEMES = json.load(f)

# Fungsi pembersihan teks 
def clean_issue(issue_text):
    return re.sub(r'^[a-z0-9\.\-)\s]+', '', issue_text.lower().strip())

# Analisis satu pemda
def analyze_single_region_issues_tfidf(pemda_data, threshold=0.25):
    issues = pemda_data.get('data', [])
    if not issues or not issues[0]:
        return None, None, None, None

    theme_counts = Counter()
    theme_scores = {theme: [] for theme in THEMES}
    matched_issues_by_theme = {theme: [] for theme in THEMES}
    unmatched_issues = []

    # Gabungkan keyword setiap tema jadi satu teks
    theme_representations = {theme: " ".join(keywords) for theme, keywords in THEMES.items()}

    # Precompute TF-IDF untuk semua tema
    vectorizer = TfidfVectorizer()

    for issue in issues:
        cleaned_issue = clean_issue(issue)
        if not cleaned_issue:
            continue

        best_theme = None
        best_score = 0

        for theme, theme_text in theme_representations.items():
            tfidf_matrix = vectorizer.fit_transform([cleaned_issue, theme_text])
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            if score > best_score:
                best_score = score
                best_theme = theme

        if best_score >= threshold and best_theme:
            theme_counts[best_theme] += 1
            theme_scores[best_theme].append(round(best_score * 100, 2))
            matched_issues_by_theme[best_theme].append(issue.strip())
        else:
            unmatched_issues.append(issue.strip())

    return theme_counts, unmatched_issues, matched_issues_by_theme, theme_scores

# Main: proses semua pemda 
with open("Data/data_pemda.json", "r", encoding="utf-8") as f:
    data = json.load(f)["data"]

hasil_akhir = []

for pemda in data:
    theme_counts, unmatched, matched, scores = analyze_single_region_issues_tfidf(pemda)
    if not theme_counts:
        continue
    top_themes = theme_counts.most_common(2)
    hasil_akhir.append({
        "pemda": pemda["namapemda"],
        "top_themes": top_themes,
        "matched_issues": matched,
        "scores": scores,
        "unmatched_issues": unmatched
    })

# SIMPAN HASIL
with open("./Output/hasil_topikutama.json", "w", encoding="utf-8") as f:
    json.dump(hasil_akhir, f, ensure_ascii=False, indent=2)

print("✅ Analisis selesai. Hasil ada di './Output/hasil_topikutama.json'")
