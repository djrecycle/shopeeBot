from playwright.sync_api import sync_playwright
import requests
import subprocess
import os
import time
import re
import json
import urllib.parse
import pandas as pd

# Default keywords jika user tidak menginputkan
DEFAULT_KEYWORDS = [
    "Senar Gitar"
]

# ========================
# OPSI PENGURUTAN
# ========================
SORT_OPTIONS = {
    "1": {"label": "Relevan",          "params": ""},
    "2": {"label": "Terbaru",          "params": "sortBy=ctime&order=desc"},
    "3": {"label": "Terlaris",         "params": "sortBy=sales&order=desc"},
    "4": {"label": "Harga Terendah",   "params": "sortBy=price&order=asc"},
    "5": {"label": "Harga Tertinggi",  "params": "sortBy=price&order=desc"},
}

# ========================
# DAFTAR LOKASI (nama sesuai filter resmi Shopee)
# ========================
LOKASI_OPTIONS = {
    "1":  {"label": "Semua Lokasi",        "value": ""},
    "2":  {"label": "Jabodetabek",         "value": "Jabodetabek"},
    "3":  {"label": "Jawa Barat",          "value": "Jawa Barat"},
    "4":  {"label": "Jawa Tengah",         "value": "Jawa Tengah"},
    "5":  {"label": "Jawa Timur",          "value": "Jawa Timur"},
    "6":  {"label": "Banten",              "value": "Banten"},
    "7":  {"label": "DI Yogyakarta",       "value": "DI Yogyakarta"},
    "8":  {"label": "Bali",                "value": "Bali"},
    "9":  {"label": "Sumatera Utara",      "value": "Sumatera Utara"},
    "10": {"label": "Sumatera Selatan",    "value": "Sumatera Selatan"},
    "11": {"label": "Sumatera Barat",      "value": "Sumatera Barat"},
    "12": {"label": "Riau",                "value": "Riau"},
    "13": {"label": "Kepulauan Riau",      "value": "Kepulauan Riau"},
    "14": {"label": "Lampung",             "value": "Lampung"},
    "15": {"label": "Kalimantan Barat",    "value": "Kalimantan Barat"},
    "16": {"label": "Kalimantan Selatan",  "value": "Kalimantan Selatan"},
    "17": {"label": "Kalimantan Timur",    "value": "Kalimantan Timur"},
    "18": {"label": "Sulawesi Selatan",    "value": "Sulawesi Selatan"},
    "19": {"label": "Sulawesi Utara",      "value": "Sulawesi Utara"},
    "20": {"label": "Nusa Tenggara Barat", "value": "Nusa Tenggara Barat"},
    "21": {"label": "Aceh",                "value": "Aceh"},
    "22": {"label": "Jambi",               "value": "Jambi"},
    "23": {"label": "Bengkulu",            "value": "Bengkulu"},
    "24": {"label": "Kalimantan Tengah",   "value": "Kalimantan Tengah"},
    "25": {"label": "Sulawesi Tengah",     "value": "Sulawesi Tengah"},
    "26": {"label": "Sulawesi Tenggara",   "value": "Sulawesi Tenggara"},
    "27": {"label": "Papua",               "value": "Papua"},
    "28": {"label": "Maluku",              "value": "Maluku"},
}

def pilih_mode():
    print("\n🔍 Pilih Mode Scraping:")
    print("─" * 30)
    print("  [1] Berdasarkan Kata Kunci (Keyword) - Biasa")
    print("  [2] Berdasarkan Toko Spesifik (Username/URL)")
    print("─" * 30)
    while True:
        pilihan = input("Masukkan nomor mode (default: 1): ").strip()
        if pilihan == "" or pilihan == "1":
            return "keyword"
        elif pilihan == "2":
            return "toko"
        else:
            print("❌ Pilihan tidak valid, coba lagi.")

def input_target(mode):
    if mode == "keyword":
        print("\n🔑 Masukkan Keyword (pisahkan dengan koma jika lebih dari satu):")
        print("Biarkan kosong untuk menggunakan keyword default.")
        raw = input("Keyword: ").strip()
        if not raw:
            return DEFAULT_KEYWORDS
        return [k.strip() for k in raw.split(",") if k.strip()]
    else:
        print("\n🏪 Masukkan Username atau Link Toko (pisahkan dengan koma):")
        print("Contoh: hugo.store ATAU https://shopee.co.id/hugo.store")
        raw = input("Toko: ").strip()
        while not raw:
             print("❌ Harus diisi untuk mode toko!")
             raw = input("Toko: ").strip()
        
        targets = [t.strip() for t in raw.split(",") if t.strip()]
        cleaned_targets = []
        for t in targets:
             if "shopee.co.id/" in t:
                 username = t.split("shopee.co.id/")[-1].split("?")[0].strip("/")
             else:
                 username = t.strip("/")
             cleaned_targets.append(username)
        return cleaned_targets

def input_max_page():
    print("\n📄 Mengambil berapa halaman? (default: 1)")
    raw = input("Max Page: ").strip()
    if not raw:
        return 1
    try:
        val = int(raw)
        return val if val > 0 else 1
    except:
         return 1


def pilih_urutan():
    """Tampilkan menu pemilihan urutan dan kembalikan query string-nya."""
    print("\n📊 Pilih Urutan Pencarian:")
    print("─" * 30)
    for key, opt in SORT_OPTIONS.items():
        print(f"  [{key}] {opt['label']}")
    print("─" * 30)

    while True:
        pilihan = input("Masukkan nomor (default: 3 - Terlaris): ").strip()
        if pilihan == "":
            pilihan = "3"  # Default: Terlaris
        if pilihan in SORT_OPTIONS:
            selected = SORT_OPTIONS[pilihan]
            print(f"✅ Urutan dipilih: {selected['label']}")
            return selected["params"]
        else:
            print("❌ Pilihan tidak valid, coba lagi.")


def pilih_lokasi():
    """Tampilkan menu pemilihan lokasi/kota penjual."""
    print("\n📍 Pilih Lokasi Penjual:")
    print("─" * 40)
    # Tampilkan dalam 2 kolom agar lebih rapi
    keys = list(LOKASI_OPTIONS.keys())
    mid = (len(keys) + 1) // 2
    left_keys  = keys[:mid]
    right_keys = keys[mid:]
    for l, r in zip(left_keys, right_keys + [""]):
        left_text  = f"  [{l:>2}] {LOKASI_OPTIONS[l]['label']}"
        right_text = f"  [{r:>2}] {LOKASI_OPTIONS[r]['label']}" if r else ""
        print(f"{left_text:<35}{right_text}")
    print("─" * 40)
    print("  Pisahkan dengan koma untuk memilih lebih dari satu.")
    print("  Contoh: 2,3  → DKI Jakarta & Jawa Barat")
    print("─" * 40)

    while True:
        raw = input("Masukkan nomor lokasi (default: 1 - Semua): ").strip()
        if raw == "":
            raw = "1"

        pilihan_list = [p.strip() for p in raw.split(",") if p.strip()]

        # Jika salah satu pilih '1' (Semua), abaikan pilihan lain
        if "1" in pilihan_list:
            print("✅ Lokasi dipilih: Semua Lokasi")
            return [], "Semua Lokasi"

        if all(p in LOKASI_OPTIONS for p in pilihan_list):
            lokasi_values = [LOKASI_OPTIONS[p]["value"] for p in pilihan_list]
            lokasi_labels = [LOKASI_OPTIONS[p]["label"] for p in pilihan_list]
            print(f"✅ Lokasi dipilih: {', '.join(lokasi_labels)}")
            return lokasi_values, ', '.join(lokasi_labels)
        else:
            invalid = [p for p in pilihan_list if p not in LOKASI_OPTIONS]
            print(f"❌ Nomor tidak valid: {', '.join(invalid)}. Coba lagi.")


def input_rating_filter():
    """Minta input minimum rating dari user. Default 4.9."""
    print("\n⭐ Filter Rating Minimum:")
    print("─" * 30)
    print("  Masukkan rating minimum (0.0 - 5.0)")
    print("  Produk di bawah rating ini akan dilewati.")
    print("─" * 30)

    while True:
        raw = input("Rating minimum (default: 4.9): ").strip()
        if raw == "":
            print("✅ Filter rating: ≥ 4.9 ⭐")
            return 4.9
        try:
            val = float(raw)
            if 0.0 <= val <= 5.0:
                print(f"✅ Filter rating: ≥ {val} ⭐")
                return val
            else:
                print("❌ Harus antara 0.0 dan 5.0")
        except ValueError:
            print("❌ Input tidak valid, masukkan angka.")


def pilih_kategori():
    print("\n📂 Pilih Kategori untuk Data Ini:")
    print("─" * 30)
    
    os.makedirs("hasil_md", exist_ok=True)
    categories_set = set([d for d in os.listdir("hasil_md") if os.path.isdir(os.path.join("hasil_md", d))])
    
    csv_file = "shopee_links.csv"
    if os.path.exists(csv_file):
        try:
            df_temp = pd.read_csv(csv_file)
            if "Kategori" in df_temp.columns:
                csv_cats = df_temp["Kategori"].dropna().unique().tolist()
                for c in csv_cats:
                    if str(c).strip():
                        categories_set.add(str(c).strip())
        except Exception:
            pass
            
    categories = sorted(list(categories_set))
    
    if not categories:
        print("  Belum ada kategori.")
    else:
        for i, cat in enumerate(categories, 1):
            print(f"  [{i}] {cat}")
    print(f"  [{len(categories) + 1}] ➕ Buat / Masukkan Kategori Baru")
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

def start_chrome():
    print("🔍 Cek Chrome debugging...")

    try:
        requests.get("http://localhost:9222/json/version", timeout=2)
        print("✅ Chrome sudah berjalan")
    except:
        print("🚀 Membuka Chrome baru...")

        # Pakai profile yang sama dengan shoppescrap.py supaya session/cookie konsisten
        chrome_profile = os.path.abspath("shopee_debug_profile")

        subprocess.Popen([
            "google-chrome",
            "--remote-debugging-port=9222",
            f"--user-data-dir={chrome_profile}",
            "--no-first-run"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(5)


def scrape_links():
    print("🔥 Mulai scraping...")

    # Pilih mode
    mode = pilih_mode()
    
    # Pilih target
    targets = input_target(mode)

    # Pilih jumlah halaman
    max_page = input_max_page()

    # Pilih urutan sebelum mulai
    sort_params = pilih_urutan()

    # Pilih lokasi penjual
    lokasi_values, lokasi_label = pilih_lokasi()

    # Pilih filter rating
    min_rating = input_rating_filter()

    # Pilih kategori untuk disimpan
    kategori_pilihan = pilih_kategori()

    start_chrome()

    with sync_playwright() as p:
        print("🔗 Connect ke Chrome...")

        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Berhasil connect")
        except Exception as e:
            print("❌ Gagal connect:", e)
            return

        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        all_links = []  # Kumpulan semua link dari semua target

        for target_index, target in enumerate(targets):
            print(f"\n{'='*50}")
            if mode == "keyword":
                print(f"🔑 Target [{target_index+1}/{len(targets)}] (Keyword): {target}")
                base_url = f"https://shopee.co.id/search?keyword={target}"
                url = f"{base_url}&{sort_params}" if sort_params else base_url
                # Tambahkan filter lokasi menggunakan format resmi Shopee: fe_filter_options
                if lokasi_values:
                    filter_obj = [{"group_name": "LOCATIONS", "values": lokasi_values}]
                    filter_json = json.dumps(filter_obj, separators=(",", ":"))
                    url += f"&fe_filter_options={urllib.parse.quote(filter_json)}"
            else:
                print(f"🏪 Target [{target_index+1}/{len(targets)}] (Toko): {target}")
                base_url = f"https://shopee.co.id/{target}?page=0"
                url = f"{base_url}&{sort_params}" if sort_params else base_url
                if lokasi_values:
                    print("ℹ️  Filter lokasi tidak berlaku untuk mode Toko dan akan diabaikan.")
            print(f"{'='*50}")
            if lokasi_label != "Semua Lokasi":
                print(f"📍 Filter Lokasi: {lokasi_label}")

            print(f"🌐 Buka URL: {url}...")
            page.goto(url, timeout=60000)

            page.wait_for_timeout(7000)

            # ========================
            # CEK CAPTCHA / LOGIN
            # ========================
            current_url = page.url.lower()
            is_blocked = "login" in current_url or "verify" in current_url or "captcha" in current_url

            if is_blocked:
                print("\n⚠️ Login / captcha diperlukan!")
                input("Selesaikan di browser lalu tekan ENTER...")
                page.wait_for_timeout(3000)

            # ========================
            # TUNGGU PRODUK MUNCUL
            # ========================
            selectors_to_try = [
                'a[href*="-i."]',
                'a[data-sqe="link"]',
                'div[data-sqe="item"]',
                'div.shopee-search-item-result__item',
            ]

            product_found = False
            for sel in selectors_to_try:
                try:
                    page.wait_for_selector(sel, timeout=10000)
                    count = page.locator(sel).count()
                    if count > 0:
                        print(f"✅ Produk ditemukan dengan selector: {sel} ({count} elemen)")
                        product_found = True
                        break
                except:
                    continue

            if not product_found:
                print(f"❌ Produk tidak ditemukan untuk target '{target}'!")
                page.screenshot(path=f"debug_search_{target_index}.png")
                print(f"📸 Screenshot: debug_search_{target_index}.png")
                print("⏭️ Lanjut ke target berikutnya...")
                continue  # Lanjut ke target berikutnya, bukan berhenti total

            keyword_links = []

            for page_num in range(max_page):
                print(f"\n📄 Halaman {page_num+1}")

                # Scroll supaya load semua produk
                for i in range(8):
                    page.mouse.wheel(0, 3000)
                    page.wait_for_timeout(1500)

                # Scroll balik ke atas sedikit untuk memicu lazy load
                page.mouse.wheel(0, -2000)
                page.wait_for_timeout(1000)

                # ========================
                # AMBIL LINK PRODUK + RATING
                # ========================
                link_elements = page.locator('a[href*="-i."]').all()

                if not link_elements:
                    link_elements = page.locator('a[href]').all()

                page_links = []
                skipped_rating = 0
                for el in link_elements:
                    try:
                        href = el.get_attribute("href")
                        if href and "-i." in href:
                            if href.startswith("/"):
                                full_link = "https://shopee.co.id" + href
                            elif href.startswith("http"):
                                full_link = href
                            else:
                                continue

                            full_link = full_link.split("?")[0]

                            # Ekstrak rating dari product card
                            rating = 0.0
                            try:
                                # Ambil teks lengkap dari card produk
                                card_text = el.inner_text()
                                # Cari pola rating (angka desimal biasanya 4.9, 5.0, dll)
                                rating_matches = re.findall(r'(\d\.\d)\b', card_text)
                                for r in rating_matches:
                                    val = float(r)
                                    if 0.0 <= val <= 5.0:
                                        rating = val
                                        break
                            except:
                                pass

                            # Filter berdasarkan rating minimum
                            if rating < min_rating:
                                skipped_rating += 1
                                continue

                            page_links.append({"link": full_link, "rating": rating})
                    except:
                        continue

                print(f"🔎 Link produk di halaman ini: {len(page_links)}")
                if skipped_rating > 0:
                    print(f"⏩ Dilewati karena rating < {min_rating}: {skipped_rating} produk")
                keyword_links.extend(page_links)
                print(f"📦 Total link keyword ini: {len(set(p['link'] for p in keyword_links))}")

                # ========================
                # PINDAH KE HALAMAN BERIKUTNYA
                # ========================
                if page_num < max_page - 1:
                    try:
                        next_selectors = [
                            'button.shopee-icon-button--right',
                            'button[aria-label="next"]',
                            'a[aria-label="next"]',
                            'button:has(svg[viewbox*="chevron-right"])',
                        ]

                        clicked = False
                        for sel in next_selectors:
                            next_btn = page.locator(sel)
                            if next_btn.count() > 0:
                                is_disabled = next_btn.first.get_attribute("disabled")
                                if is_disabled is not None:
                                    print("⛔ Tombol next disabled, ini halaman terakhir")
                                    break

                                print("➡️ Pindah ke halaman berikutnya...")
                                next_btn.first.click()
                                page.wait_for_timeout(6000)
                                clicked = True
                                break

                        if not clicked:
                            next_page = page_num + 2
                            page_btn = page.locator(f'button:text-is("{next_page}")')
                            if page_btn.count() > 0:
                                print(f"➡️ Klik halaman {next_page}...")
                                page_btn.first.click()
                                page.wait_for_timeout(6000)
                            else:
                                print("⛔ Tidak ada tombol next")
                                break

                    except Exception as e:
                        print("❌ Gagal klik next:", e)
                        break

            # Simpan hasil target ini
            seen = set()
            for item in keyword_links:
                if item["link"] not in seen:
                    seen.add(item["link"])
                    keyword_label = target if mode == "keyword" else f"Toko: {target}"
                    all_links.append({
                        "Kategori": kategori_pilihan,
                        "Keyword": keyword_label,
                        "Lokasi": lokasi_label,
                        "Link Produk": item["link"],
                        "Rating": item["rating"],
                        "Status Chat": "",
                        "Status": ""
                    })

            print(f"\n✅ Target '{target}' selesai: {len(seen)} link unik (rating ≥ {min_rating})")

        # Simpan semua hasil
        print(f"\n{'='*50}")
        print("💾 Menyimpan ke CSV...")

        df = pd.DataFrame(all_links)
        
        # Gabungkan dengan CSV sebelumnya jika ada, agar tidak tertumpuk (overwrite total)
        csv_file = "shopee_links.csv"
        if os.path.exists(csv_file):
            try:
                old_df = pd.read_csv(csv_file)
                df = pd.concat([old_df, df], ignore_index=True)
            except Exception as e:
                print(f"⚠️ Gagal membaca CSV yang sudah ada: {e}")

        df = df.drop_duplicates(subset="Link Produk", keep="last")
        
        # Pastikan urutan kolom sesuai yang diinginkan
        desired_columns = ["Kategori", "Keyword", "Lokasi", "Link Produk", "Rating", "Status Chat", "Status"]
        # Jika ada kolom tambahan dari dataframe lama, tambahkan ke belakang
        for col in df.columns:
            if col not in desired_columns:
                desired_columns.append(col)
        df = df.reindex(columns=desired_columns)
        
        df.to_csv(csv_file, index=False)

        print(f"✅ SELESAI! Total link unik di database: {len(df)}")
        print(f"📁 File: {csv_file}")

        # Tampilkan ringkasan per keyword
        if not df.empty:
            print("\n📊 Ringkasan:")
            summary = df.groupby("Keyword").size()
            for kw, count in summary.items():
                print(f"   • {kw}: {count} link")


if __name__ == "__main__":
    scrape_links()