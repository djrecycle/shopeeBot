from playwright.sync_api import sync_playwright
import requests
import os
import time
import subprocess
import re

# ========================
# LOAD URL DARI FILE
# ========================
URL_FILE = "shopee_links.csv"
MAX_URLS = 5  # Batasi jumlah URL yang diproses
VARIASI = ["Warna", "Model", "Mode", "Ukuran", "Kapasitas", "Tipe", "Tipe Hp", "Type Hp","Type", "Varian", "Size", "Color","Piano", "Keyboard", "Keyboard", "Piano","Senar","Senar Gitar","Senar Bass","Senar Bass Elektrik","Senar Nomor"
"Nomor Senar","Motif","Jenis","Jenis Barang"]

def load_urls():
    user_url = input("\nMasukkan URL Shopee yang ingin discrape (biarkan kosong untuk mengambil dari shopee_links.csv): ").strip()
    if user_url:
        print(f"📋 Memproses 1 URL dari input manual.")
        cat = get_category()
        return [{"url": user_url, "kategori": cat}]

    import pandas as pd
    try:
        df = pd.read_csv(URL_FILE, dtype={"Status": str}) if "Status" in pd.read_csv(URL_FILE, nrows=0).columns else pd.read_csv(URL_FILE)
    except FileNotFoundError:
        print(f"❌ File {URL_FILE} tidak ditemukan. Silakan jalankan scrape_links.py terlebih dahulu.")
        exit()
    
    # Tambahkan kolom Status jika belum ada
    if "Status" not in df.columns:
        df["Status"] = ""
    else:
        df["Status"] = df["Status"].fillna("")
        
    # Ambil baris yang belum di-"Done" atau di-"Skip"
    # Menambahkan pengecekan status tambahan jika ada format lain
    unscraped_df = df[~df["Status"].isin(["Done", "Skip", "Skip (Toko Sama)", "Failed", "Sent"])]

    if unscraped_df.empty:
        print("🎉 Semua URL di shopee_links.csv sudah selesai discrape!")
        exit()

    # Berikan pilihan Keyword/Toko
    if "Keyword" in df.columns:
        keywords = unscraped_df["Keyword"].value_counts()
        print("\n📂 Pilih kelompok URL yang ingin discrape:")
        print("─" * 30)
        print("  [0] Semua Keyword/Toko (Campur)")
        
        kw_list = list(keywords.items())
        for i, (kw, count) in enumerate(kw_list, 1):
            print(f"  [{i}] {kw} ({count} url belum diproses)")
        print("─" * 30)
        
        while True:
            pilihan = input("Masukkan nomor pilihan (default: 0): ").strip()
            if pilihan == "" or pilihan == "0":
                print("✅ Memilih semua URL yang tersisa.")
                break
            try:
                idx = int(pilihan) - 1
                if 0 <= idx < len(kw_list):
                    selected_kw = kw_list[idx][0]
                    unscraped_df = unscraped_df[unscraped_df["Keyword"] == selected_kw]
                    print(f"✅ Memilih URL dengan target: {selected_kw}")
                    break
                else:
                    print("❌ Nomor tidak valid.")
            except ValueError:
                print("❌ Input harus berupa angka.")

    urls = unscraped_df["Link Produk"].dropna().tolist()

    if not urls:
        print("🎉 Tidak ada URL tersedia pada pilihan tersebut!")
        exit()

    urls = urls[:MAX_URLS]
    print(f"📋 Akan memproses: {len(urls)} URL pada batch ini (max {MAX_URLS})")
    
    result = []
    for link in urls:
        row = unscraped_df[unscraped_df["Link Produk"] == link].iloc[0]
        cat = getattr(row, "Kategori", "Uncategorized") if "Kategori" in df.columns else "Uncategorized"
        import pandas as pd
        if pd.isna(cat) or not str(cat).strip():
            cat = "Uncategorized"
        result.append({"url": link, "kategori": str(cat)})
        
    return result

def update_status(url, status):
    """Update status (Done/Skip) produk di CSV."""
    import pandas as pd
    try:
        df = pd.read_csv(URL_FILE, dtype={"Status": str}) if "Status" in pd.read_csv(URL_FILE, nrows=0).columns else pd.read_csv(URL_FILE)
        if "Status" not in df.columns:
            df["Status"] = ""
        else:
            df["Status"] = df["Status"].fillna("")
            
        df.loc[df["Link Produk"] == url, "Status"] = status
        df.to_csv(URL_FILE, index=False)
    except Exception as e:
        print(f"⚠️ Gagal mengupdate status CSV: {e}")

def get_category():
    os.makedirs("hasil_md", exist_ok=True)
    categories = [d for d in os.listdir("hasil_md") if os.path.isdir(os.path.join("hasil_md", d))]
    
    print("\n📂 Pilih Kategori Penyimpanan:")
    print("─" * 30)
    if not categories:
        print("  Belum ada kategori.")
    else:
        for i, cat in enumerate(categories, 1):
            print(f"  [{i}] {cat}")
    print(f"  [{len(categories) + 1}] ➕ Buat Kategori Baru")
    print("─" * 30)
    
    while True:
        pilihan = input("Masukkan nomor pilihan: ").strip()
        try:
            idx = int(pilihan) - 1
            if 0 <= idx < len(categories):
                return categories[idx]
            elif idx == len(categories):
                new_cat = input("Masukkan nama kategori baru: ").strip()
                if new_cat:
                    clean_cat = re.sub(r'[\\/*?:"<>|]', "", new_cat).strip()
                    if clean_cat:
                        return clean_cat
                    else:
                        print("❌ Nama tidak valid.")
                else:
                    print("❌ Nama kategori tidak boleh kosong.")
            else:
                print("❌ Nomor tidak valid.")
        except ValueError:
            print("❌ Input harus berupa angka.")

def scrape_shopee():

    with sync_playwright() as p:
        print("Menggunakan metode Murni Chrome Executable untuk menipu Datadome...")
        
        try:
            requests.get("http://localhost:9222/json/version", timeout=1)
            print("Chrome Debugging sudah berjalan di latar belakang.")
        except Exception:
            print("Membuka instansi Google Chrome murni yang baru...")
            chrome_profile = os.path.abspath("shopee_debug_profile")
            subprocess.Popen([
                "google-chrome",
                "--remote-debugging-port=9222",
                f"--user-data-dir={chrome_profile}",
                "--no-first-run"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(4)
            
        print("Menyambungkan script Python ke Jendela Chrome tadi...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            print("Gagal menyambung!")
            return
            
        context = browser.contexts[0] if len(browser.contexts) > 0 else browser.new_context()
        page = context.pages[0] if len(context.pages) > 0 else context.new_page()

        try:
            try:
                from playwright_stealth import stealth_sync
                stealth_sync(page)
            except ImportError:
                from playwright_stealth import stealth
                stealth(page)
        except Exception:
            pass
            
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['id-ID', 'id', 'en-US', 'en']})")

        # ========================
        # PEMANASAN: Buka homepage dulu
        # ========================
        import random

        print("\n🏠 Membuka Shopee homepage sebagai pemanasan...")
        page.goto("https://shopee.co.id", timeout=60000)
        page.wait_for_timeout(4000)

        homepage_url = page.url.lower()
        if "verify" in homepage_url or "traffic/error" in homepage_url:
            print("⚠️  Homepage juga terblokir!")
            print("   Buka shopee.co.id manual di address bar browser.")
            input("   Tekan ENTER setelah homepage Shopee terbuka normal...")
            page.wait_for_timeout(2000)

        print("✅ Homepage OK, mulai scraping...\n")

        # ========================
        # HELPER: Cek apakah halaman blocked
        # ========================
        def is_page_blocked(p):
            """Cek apakah halaman saat ini terblokir."""
            try:
                cur = p.url.lower()
                title_text = (p.title() or "").lower()
                return (
                    "login" in cur
                    or "verify" in cur
                    or "captcha" in cur
                    or "traffic/error" in cur
                    or "halaman tidak tersedia" in title_text
                )
            except:
                return True

        # ========================
        # LOOP SEMUA URL
        # ========================
        urls_data = load_urls()

        for idx, item in enumerate(urls_data, 1):
            url = item["url"]
            category = item["kategori"]
            
            save_dir = os.path.join("hasil_md", category)
            os.makedirs(save_dir, exist_ok=True)

            print(f"\n==============================")
            print(f"[{idx}/{len(urls_data)}] Membuka di New Tab: {url[:80]}...")

            # Delay acak antar produk untuk menghindari rate-limit
            if idx > 1:
                delay = random.uniform(3, 7)
                print(f"⏳ Menunggu {delay:.1f} detik...")
                page.wait_for_timeout(int(delay * 1000))

            # ========================
            # BUKA DI NEW TAB via window.open()
            # ========================
            tabs_before = len(context.pages)

            # Gunakan JavaScript window.open() — terlihat seperti user klik link
            page.evaluate(f'window.open("{url}", "_blank")')
            page.wait_for_timeout(3000)

            # Ambil tab baru
            if len(context.pages) <= tabs_before:
                print("❌ Gagal membuka tab baru, skip.")
                update_status(url, "Skip")
                continue

            new_page = context.pages[-1]  # Tab terakhir = yang baru dibuka
            new_page.wait_for_timeout(4000)

            # ========================
            # DETEKSI BLOCK
            # ========================
            if is_page_blocked(new_page):
                print(f"\n⚠️  Halaman terblokir oleh Shopee!")
                print(f"   Jenis: {'Traffic Error' if 'traffic/error' in new_page.url.lower() else 'Login/Captcha'}")
                print(f"\n   📋 INSTRUKSI:")
                print(f"   1. Di browser, buka tab yang baru terbuka")
                print(f"   2. Copy-paste URL ini di address bar:")
                print(f"      {url}")
                print(f"   3. Tunggu halaman produk terbuka normal")
                input("\n   ➡️  Tekan ENTER setelah halaman produk terbuka...")
                new_page.wait_for_timeout(3000)

                if is_page_blocked(new_page):
                    print("❌ Masih terblokir, skip produk ini.")
                    update_status(url, "Skip")
                    try:
                        new_page.close()
                    except:
                        pass
                    continue

            print("✅ Halaman produk terbuka")
            print("Scrolling...")
            for _ in range(8):
                new_page.mouse.wheel(0, 600)
                new_page.wait_for_timeout(800)

            new_page.wait_for_timeout(2000)

            # ========================
            # AMBIL DATA (dari new_page)
            # ========================
            title = None
            try:
                h1 = new_page.locator("h1")
                if h1.count() > 0:
                    h1_text = h1.first.inner_text().strip()
                    if h1_text and "tidak tersedia" not in h1_text.lower():
                        title = h1_text

                if not title:
                    for sel in ['span[class*="title"]', 'div[class*="title"]', '[data-sqe="name"]']:
                        el = new_page.locator(sel)
                        if el.count() > 0:
                            t = el.first.inner_text().strip()
                            if t and len(t) > 5:
                                title = t
                                break
            except:
                pass

            if not title:
                try:
                    slug = url.split("/")[-1].split("-i.")[0]
                    title = slug.replace("-", " ").strip()
                except:
                    title = None

            if not title:
                print("⚠️  Judul produk tidak ditemukan, skip.")
                update_status(url, "Skip")
                try:
                    new_page.close()
                except:
                    pass
                continue

            try:
                price_element = new_page.locator('text=/Rp[\\d\\.,]+/')
                price = price_element.first.inner_text() if price_element.count() > 0 else "Tidak ditemukan"
            except:
                price = "Tidak ditemukan"

            try:
                desc_locator = new_page.locator('section:has-text("Deskripsi Produk"), .e8lZp3, [class*="product-description"]')
                if desc_locator.count() > 0:
                    description = desc_locator.first.inner_text().replace("Deskripsi Produk", "").strip()
                else:
                    description = "Tidak ditemukan"
            except Exception:
                description = "Tidak ditemukan"

            try:
                spec_locator = new_page.locator('section:has-text("Spesifikasi Produk")')
                if spec_locator.count() > 0:
                    spec_section = spec_locator.first
                    rows = spec_section.locator('div:has(> h3)').all()
                    
                    if len(rows) > 0:
                        spec_table_md = "| Spesifikasi | Detail |\n| :--- | :--- |\n"
                        for row in rows:
                            try:
                                key = row.locator('h3').first.inner_text().strip()
                                full_text = row.inner_text().strip()
                                val_text = full_text[len(key):].strip() if full_text.startswith(key) else full_text.replace(key, "", 1).strip()
                                val_text = val_text.replace("\n", " ").replace("|", "&#124;").strip()
                                if key:
                                    spec_table_md += f"| **{key}** | {val_text} |\n"
                            except Exception:
                                pass
                        
                        if spec_table_md.count("\n") > 2:
                            specification = spec_table_md
                        else:
                            specification = spec_section.inner_text().replace("Spesifikasi Produk", "").strip()
                    else:
                        specification = spec_section.inner_text().replace("Spesifikasi Produk", "").strip()
                else:
                    specification = "Tidak ditemukan"
            except Exception:
                specification = "Tidak ditemukan"

            # ========================
            # VARIASI (CLICK + AMBIL HARGA)
            # ========================
            variant_results = []

            try:
                for var_name in VARIASI:
                    # Case-insensitive: ambil semua h2, bandingkan dengan .lower()
                    all_h2 = new_page.locator('h2').all()
                    h2 = None
                    for h in all_h2:
                        try:
                            if h.inner_text().strip().lower() == var_name.lower():
                                h2 = h
                                break
                        except:
                            continue

                    if not h2:
                        continue

                    print(f"🔧 Variasi ditemukan: {var_name}")

                    parent_section = h2.locator('xpath=ancestor::section[1]')
                    if parent_section.count() == 0:
                        parent_section = h2.locator('xpath=..')

                    buttons = parent_section.locator('button').all()
                    print(f"   Button ditemukan: {len(buttons)}")

                    for i, btn in enumerate(buttons):
                        try:
                            if btn.get_attribute("aria-disabled") == "true":
                                continue

                            label = btn.inner_text().strip()
                            if not label:
                                label = btn.get_attribute("aria-label") or f"Var {i+1}"

                            if len(label) > 100 or label.lower() in ["", "chat"]:
                                continue

                            # Cek gambar variasi
                            var_img_url = ""
                            try:
                                img_el = btn.locator('img')
                                if img_el.count() > 0:
                                    src = img_el.first.get_attribute('src')
                                    if src:
                                        var_img_url = re.sub(r'_tn$', '', src)
                            except:
                                pass

                            btn.click()
                            new_page.wait_for_timeout(1000)

                            try:
                                price_var = new_page.locator('text=/Rp[\\d\\.,]+/').first.inner_text()
                            except:
                                price_var = "-"

                            variant_results.append({
                                "variasi": f"{var_name}: {label}",
                                "harga": price_var,
                                "gambar": var_img_url
                            })
                        except:
                            pass

            except Exception as e:
                print("Gagal ambil variasi:", e)

            # ========================
            # GAMBAR
            # ========================
            print("Mengambil gambar produk...")

            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title)[:30]
            folder = f"gambar/{category}/{safe_title}"
            os.makedirs(folder, exist_ok=True)

            img_urls = []

            try:
                html = new_page.content()

                matches = re.findall(r'"images":\[(.*?)\]', html)

                for m in matches:
                    hashes = re.findall(r'"(.*?)"', m)
                    for h in hashes:
                        if len(h) > 20:
                            img_urls.append(f"https://down-id.img.susercontent.com/file/{h}")

            except:
                pass

            img_urls = list(set([re.sub(r'_tn$', '', u) for u in img_urls]))
            img_urls.sort()  # Wajib di-sort agar urutan tetap sama dan md_content konsisten!
            print(f"Total gambar unik: {len(img_urls)}")

            for i, url_img in enumerate(img_urls[:10]):
                try:
                    img_data = requests.get(url_img, timeout=10).content
                    with open(f"{folder}/img_{i}.jpg", "wb") as f:
                        f.write(img_data)
                except:
                    pass

            # ========================
            # TUTUP TAB PRODUK
            # ========================
            try:
                new_page.close()
                print("🗂️  Tab produk ditutup")
            except:
                pass

            # ========================
            # SIMPAN KE MARKDOWN
            # ========================
            print(f"\n📋 Hasil scraping:")
            print(f"   Judul  : {title[:60]}..." if len(title) > 60 else f"   Judul  : {title}")
            print(f"   Harga  : {price}")
            print(f"   Spesifikasi: {'Ditemukan' if specification != 'Tidak ditemukan' else 'Tidak ditemukan'}")
            print(f"   Variasi: {len(variant_results)} item")
            print(f"   Gambar : {len(img_urls)} file")

            clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
            clean_title = re.sub(r'[^\x00-\x7f]', r'', clean_title)
            filename = clean_title.strip()[:50].strip() or "produk"

            # Ambil shop id dari URL
            shop_link = "Tidak ditemukan"
            try:
                shop_id = url.split("-i.")[-1].split(".")[0]
                if shop_id.isdigit():
                    shop_link = f"https://shopee.co.id/shop/{shop_id}"
            except:
                pass

            md_content = f"""# {title}

## 💰 Harga
{price}

## 🏪 Link Toko
{shop_link}

## 🔗 Link Produk
{url}

## 📋 Spesifikasi
{specification}

## 📝 Deskripsi
{description}
"""

            md_content += "\n## 🔧 Variasi Produk\n"

            if variant_results:
                for v in variant_results:
                    if v.get("gambar"):
                        md_content += f"- {v['variasi']} : {v['harga']} | [Lihat Gambar Variasi]({v['gambar']})\n"
                    else:
                        md_content += f"- {v['variasi']} : {v['harga']}\n"
            else:
                md_content += "- Tidak ada variasi\n"

            md_content += "\n## 🖼️ Gambar Produk\n"

            for i, img in enumerate(img_urls):
                md_content += f"\n![Gambar {i+1}]({img})\n"

            file_path = os.path.join(save_dir, f"{filename}.md")

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_content = f.read()
                    if existing_content == md_content:
                        print(f"⏩ Skip: {filename}.md sudah ada & konten tidak berubah")
                        update_status(url, "Done")
                        continue
                except:
                    pass
                
                # Kalau eksis tapi beda isi, maka OVERWRITE
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print(f"🔄 Diupdate: {filename}.md (ditimpa dengan data baru)")
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print(f"✔ Disimpan: {filename}.md")
                
            # Tandai selesai di CSV
            update_status(url, "Done")

        # Bersihkan
        print(f"\n{'='*50}")
        print("🏁 Selesai scraping semua produk!")

if __name__ == "__main__":
    scrape_shopee()