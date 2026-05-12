import os
import re
import pandas as pd
from difflib import SequenceMatcher
import glob

print("Memuat data dari Kode_Kategori.xlsx...")
try:
    df = pd.read_excel("Kode_Kategori.xlsx")
except Exception as e:
    print(f"Gagal memuat Excel: {e}")
    exit(1)

def normalize(s):
    # Buang awalan Shopee
    s = re.sub(r"^Shopee\s+", "", s, flags=re.IGNORECASE)
    # Buang kode id di awal excel
    s = re.sub(r"^\d+-", "", s)
    # Hapus semua karakter non-alfanumerik
    s = re.sub(r"[^a-z0-9]", "", s.lower())
    return s

excel_cats = []
for index, row in df.iterrows():
    if pd.isna(row.get("Nama Kategori")) or pd.isna(row.get("Kode Kategori")):
        continue
    norm = normalize(str(row["Nama Kategori"]))
    excel_cats.append((norm, str(row["Kode Kategori"]), str(row["Nama Kategori"])))

def find_best_match(md_cat):
    if not md_cat or md_cat == "-":
        return None
        
    norm_md = normalize(md_cat)
    
    # 1. Exact match
    for norm_exc, code, name in excel_cats:
        if norm_exc == norm_md:
            return code
            
    # 2. Excel starts with MD
    matches = [exc for exc in excel_cats if exc[0].startswith(norm_md)]
    if matches:
        for exc in matches:
            if exc[0].endswith("lainnya"):
                return exc[1]
        return matches[0][1]
        
    # 3. MD starts with Excel
    matches = [exc for exc in excel_cats if norm_md.startswith(exc[0])]
    if matches:
        matches.sort(key=lambda x: len(x[0]), reverse=True)
        return matches[0][1]
        
    # 4. Fuzzy match fallback
    best_ratio = 0
    best_match = None
    for norm_exc, code, name in excel_cats:
        ratio = SequenceMatcher(None, norm_md, norm_exc).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = code
            
    if best_ratio > 0.8:
        return best_match
        
    return None

md_files = glob.glob(os.path.join("hasil_md", "**", "*.md"), recursive=True)
print(f"Memproses {len(md_files)} file markdown...")

updated = 0
for filepath in md_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Jika sudah ada Kode Kategori, skip
    if "| **Kode Kategori** |" in content:
        continue
        
    # Cari Kategori
    match = re.search(r"\|\s*\*\*Kategori\*\*\s*\|\s*(.*?)\s*\|", content)
    if match:
        kategori_text = match.group(1).strip()
        kode = find_best_match(kategori_text)
        
        if kode:
            # Insert row Kode Kategori di bawah Kategori
            new_row = f"| **Kategori** | {kategori_text} |\n| **Kode Kategori** | {kode} |"
            new_content = content.replace(match.group(0), new_row)
            
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ Ditambahkan Kode {kode} ke: {os.path.basename(filepath)}")
                updated += 1
        else:
            print(f"⚠️ Gagal mencari kode untuk: {kategori_text} (di {os.path.basename(filepath)})")

print(f"\nSelesai! {updated} file berhasil diupdate.")
