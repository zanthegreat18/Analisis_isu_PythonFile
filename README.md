1. Analisis Kemiripan Isu Pemda Berdasarkan Tema




 # Deskripsi

Script ini melakukan analisis kemiripan isu antar pemerintah daerah (Pemda) menggunakan pendekatan semantic similarity (kemiripan makna).
Proses ini memanfaatkan model multilingual-e5-large dari sentence-transformers untuk menghasilkan embedding teks, lalu mengukur kemiripan antar isu berdasarkan cosine similarity.

Selain itu, skrip ini juga menggunakan kamus tema untuk mengelompokkan isu ke dalam topik tertentu, sehingga analisis lebih terarah.

 # Struktur Folder
.
├── Data/
│   ├── data_pemda.json      # Data isu per Pemda
│   ├── kamus_tema.json      # Daftar tema dan kata kunci
├── Output/
│   └── hasil.json           # Hasil analisis (otomatis dibuat)
├── analisis_kemiripan.py    # Script Python ini
└── README.md

 # Kebutuhan
Pastikan Python >= 3.8 sudah terinstall.
Lalu install dependensi berikut:

pip install sentence-transformers scikit-learn

 # Format Data
Data/data_pemda.json
Contoh struktur:

{
  "data": [
    {
      "namapemda": "Kota A",
      "data": [
        "Pembangunan jalan desa",
        "Program pengelolaan sampah"
      ]
    },
    {
      "namapemda": "Kota B",
      "data": [
        "Perbaikan infrastruktur jalan",
        "Pengelolaan limbah plastik"
      ]
    }
  ]
}

Data/kamus_tema.json
Contoh struktur:

{
  "Infrastruktur": ["jalan", "jembatan", "gedung"],
  "Lingkungan": ["sampah", "limbah", "penghijauan"]
}

 # Cara Menjalankan
Pastikan folder Data/ berisi:
data_pemda.json (isu Pemda)
kamus_tema.json (daftar tema & keyword)
Jalankan script:
python analisis_kemiripan.py


 # Alur Script:
Memuat data isu & kamus tema
Membersihkan teks isu
Menghitung embedding menggunakan model multilingual-e5-large
Menghitung kemiripan antar isu
Menyimpan hasil analisis ke Output/hasil.json

 # Hasil Output
File Output/hasil.json berisi daftar hasil analisis.
Contoh isi:

[
  {
    "daerah_asal": "Kota A",
    "tema": "Infrastruktur",
    "isu_asal": "Pembangunan jalan desa",
    "peringkat_kemiripan": [
      {
        "pemda_pembanding": "Kota B",
        "isu_pembanding": "Perbaikan infrastruktur jalan",
        "skor": 0.82,
        "analisis_tema": "Fokus tema umum yang terdeteksi: Infrastruktur."
      }
    ]
  }
]

 # Parameter Penting
relevance_threshold (default: 0.5)
Menentukan batas minimum skor cosine similarity agar dianggap relevan.

Model: intfloat/multilingual-e5-large
Mendukung berbagai bahasa termasuk Bahasa Indonesia.

 # Catatan
Pastikan koneksi internet aktif saat pertama kali menjalankan script (untuk download model).
Jika dataset besar, proses bisa memakan waktu karena perhitungan similarity dilakukan antar semua isu.







2. Analisis Penyebaran Tema Isu Pemda





# Deskripsi
Script ini melakukan analisis penyebaran tema pada data isu pemerintah daerah (Pemda) berdasarkan kamus kata kunci yang sudah ditentukan.
Pengguna bisa memilih salah satu tema, lalu script akan menghitung jumlah isu di setiap Pemda yang mengandung kata kunci tema tersebut.

 # Struktur Folder
.
├── Data/
│   ├── data_pemda.json      # Data isu per Pemda
│   ├── kamus_tema.json      # Daftar tema & kata kunci
├── Output/
│   └── hasil_tema_*.json    # Hasil analisis per tema (otomatis dibuat)
├── analisis_penyebaran.py   # Script Python ini
└── README.md

 # Kebutuhan
Pastikan Python >= 3.8 sudah terinstall.
Lalu install dependensi berikut:

pip install pandas

 # Format Data
Data/data_pemda.json
Contoh struktur:

{
  "data": [
    {
      "namapemda": "Kota A",
      "data": [
        "Pembangunan jalan desa",
        "Program pengelolaan sampah"
      ]
    },
    {
      "namapemda": "Kota B",
      "data": [
        "Perbaikan infrastruktur jalan",
        "Pengelolaan limbah plastik"
      ]
    }
  ]
}

Data/kamus_tema.json
Contoh struktur:

{
  "Infrastruktur": ["jalan", "jembatan", "gedung"],
  "Lingkungan": ["sampah", "limbah", "penghijauan"]
}

 # Cara Menjalankan
Pastikan folder Data/ berisi:
data_pemda.json (isu Pemda)
kamus_tema.json (daftar tema & keyword)
Jalankan script:
python analisis_penyebaran.py


Pilih nomor tema yang ingin dianalisis (misal 1 untuk Infrastruktur).
Script akan:
Menghitung jumlah isu terkait tema tersebut di setiap Pemda
Mengurutkan Pemda berdasarkan skor tertinggi
Menyimpan hasil ke file Output/hasil_tema_<nama_tema>.json

 # Hasil Output
File JSON hasil analisis berisi daftar skor per Pemda, misalnya:

[
  {
    "Nama_Pemda": "Kota A",
    "Skor_Tema": 5
  },
  {
    "Nama_Pemda": "Kota B",
    "Skor_Tema": 3
  }
]


Selain itu, hasil juga langsung ditampilkan di terminal dalam bentuk tabel.

 # Catatan
Jika input tema tidak valid, script akan langsung berhenti.
File output otomatis tersimpan di folder Output/ dengan nama sesuai tema yang dipilih.
Semua pencarian kata kunci tidak case sensitive (huruf besar/kecil tidak berpengaruh).









3. Analisis Topik Utama Pemda (TF-IDF + Cosine Similarity)





# Deskripsi
Script ini digunakan untuk menganalisis **isu-isu program pemerintah daerah** berdasarkan *tema utama* yang didefinisikan di `kamus_tema.json`.  
Pendekatan yang digunakan adalah **TF-IDF Vectorization** dan **Cosine Similarity** untuk menentukan kesamaan antara teks isu dengan daftar kata kunci tema.

# Struktur Folder
.
├── Data
│ ├── kamus_tema.json # Kamus tema berisi daftar keyword per tema
│ └── data_pemda.json # Data program per Pemda
├── Output
│ └── hasil_topikutama.json # Hasil analisis (akan dibuat otomatis)
├── analisis_topikutama.py # Script utama
└── README.md

markdown
Copy
Edit

# Cara Kerja
1. **Load Kamus Tema**  
   - File `kamus_tema.json` berisi mapping `{tema: [list keyword]}`.
2. **Load Data Pemda**  
   - File `data_pemda.json` berisi daftar pemda & isu program.
3. **Analisis per Isu**  
   - Setiap isu dibandingkan dengan semua tema menggunakan **TF-IDF**.
   - Dihitung skor kemiripan (*cosine similarity*).
4. **Klasifikasi**  
   - Isu dimasukkan ke tema dengan skor tertinggi jika `score >= threshold`.
   - Isu yang tidak cocok masuk ke `unmatched_issues`.
5. **Output**  
   - Disimpan ke `./Output/hasil_topikutama.json`.

# Instalasi & Persiapan
Pastikan Python 3.8+ sudah terpasang.  
Install dependensi:
```bash
pip install scikit-learn pandas
Siapkan folder & file:

bash
Copy
Edit
mkdir Data Output
# Letakkan kamus_tema.json & data_pemda.json di folder Data
 Menjalankan Script
bash
Copy
Edit
python analisis_topikutama.py
Setelah selesai, hasil analisis akan tersimpan di:

bash
Copy
Edit
./Output/hasil_topikutama.json
📊 Contoh Output
json
Copy
Edit
[
  {
    "pemda": "Kabupaten Contoh",
    "top_themes": [["Infrastruktur", 5], ["Pendidikan", 3]],
    "matched_issues": {
      "Infrastruktur": ["Pembangunan jalan desa", "Perbaikan jembatan"],
      "Pendidikan": ["Penyediaan beasiswa mahasiswa miskin"]
    },
    "scores": {
      "Infrastruktur": [87.4, 92.1],
      "Pendidikan": [78.6]
    },
    "unmatched_issues": ["Festival tahunan daerah"]
  }
]





 # Catatan
Ubah threshold di fungsi analyze_single_region_issues_tfidf() untuk mengatur sensitivitas kemiripan tema.
Semakin kecil threshold, semakin banyak isu yang masuk ke kategori tema (tapi bisa kurang akurat).
Untuk dataset besar, pertimbangkan optimasi batch TF-IDF atau parallel processing.
