import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Path file input/output
input_path = Path("Data/data_pemda.json")
output_path = Path("Output/tabel_pemda.html")

# Load JSON
with open(input_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

# Ambil bagian data aja
data = raw.get("data", raw)

rows = []
for item in data:
    kodepemda = item.get("kodepemda")
    namapemda = item.get("namapemda")
    isu = item.get("data", [])  

    if isinstance(isu, list):
        isu_gabung = "<br>".join(isu) 
    else:
        isu_gabung = str(isu)

    rows.append({
        "Kode Pemda": kodepemda,
        "Nama Pemda": namapemda,
        "Isu Strategis": isu_gabung
    })

# Convert ke DataFrame
df = pd.DataFrame(rows)

# Generate tabel HTML
table_html = df.to_html(index=False, escape=False)

# Bungkus dengan template HTML + styling
html = f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Tabel Isu Strategis per Pemda</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    background: #0b1220;
    color: #e5e7eb;
    padding: 32px;
  }}
  h1 {{
    margin-bottom: 10px;
    font-size: 24px;
  }}
  .sub {{
    color: #9ca3af;
    margin-bottom: 20px;
    font-size: 14px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    background: #111827;
    border-radius: 12px;
    overflow: hidden;
  }}
  th, td {{
    border: 1px solid #1f2937;
    padding: 10px 14px;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background: #1e293b;
    color: #93c5fd;
    position: sticky;
    top: 0;
  }}
  tr:nth-child(odd) {{
    background: rgba(255,255,255,0.02);
  }}
</style>
</head>
<body>
  <h1>Isu Strategis per Pemda</h1>
  <div class="sub">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • Rows: {len(df)}</div>
  {table_html}
</body>
</html>"""

# Simpan ke file
output_path.write_text(html, encoding="utf-8")
print(f"Tabel HTML berhasil diekspor ke: {output_path}")
