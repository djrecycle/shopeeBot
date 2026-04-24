"""
Script untuk mengubah Harga Upload menjadi berwarna hijau (HTML span)
di semua file markdown yang sudah ada di hasil_md.
"""
import os
import re
import glob

def update_md_file(filepath):
    """Update satu file markdown: buat Harga Upload berwarna hijau."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Sudah pake span hijau? skip
    if 'style="color: green' in content or "style='color: green" in content:
        return False
    
    # 1. Update bagian harga utama:
    #    "Harga Upload: RpXXX" -> "<span style=...>Harga Upload: RpXXX</span>"
    content = re.sub(
        r'^(Harga Upload: .+)$',
        r'<span style="color: green; font-weight: bold;">\1</span>',
        content,
        flags=re.MULTILINE
    )
    
    # 2. Update bagian variasi:
    #    "(Upload: RpXXX)" -> "<span style=...>(Upload: RpXXX)</span>"
    content = re.sub(
        r'\(Upload: ([^)]+)\)',
        r"<span style='color: green; font-weight: bold;'>(Upload: \1)</span>",
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    md_dir = "hasil_md"
    md_files = glob.glob(os.path.join(md_dir, "**", "*.md"), recursive=True)
    
    print(f"📂 Ditemukan {len(md_files)} file markdown")
    print("=" * 50)
    
    updated = 0
    skipped = 0
    
    for filepath in sorted(md_files):
        rel = os.path.relpath(filepath, md_dir)
        if update_md_file(filepath):
            print(f"  ✅ {rel}")
            updated += 1
        else:
            print(f"  ⏩ {rel} (sudah hijau)")
            skipped += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Selesai! {updated} diupdate, {skipped} diskip.")

if __name__ == "__main__":
    main()
