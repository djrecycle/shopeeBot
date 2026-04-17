import pandas as pd
import random
import os
from playwright.sync_api import sync_playwright

URL_FILE = "shopee_links.csv"
MAX_URLS = 5  # Batasi per run agar terhindar dari pemblokiran akun/rate limit
DEFAULT_MESSAGE = "Halo kak, apakah toko ini menerima dropship dan bisa menggunakan resi otomatis?, jika saya diizinkan menjadi dropshipper bolehkah saya meminta kontak yang bisa dihubungi agar mempermudah komunikasi?,, mohon maaf mengganggu waktunya kak"

def load_urls():
    import re
    if not os.path.exists(URL_FILE):
        print(f"❌ File {URL_FILE} tidak ditemukan!")
        exit()
        
    df = pd.read_csv(URL_FILE, dtype={"Status Chat": str}) if "Status Chat" in pd.read_csv(URL_FILE, nrows=0).columns else pd.read_csv(URL_FILE)
    
    # Tambahkan kolom 'Status Chat' jika belum ada
    if "Status Chat" not in df.columns:
        df["Status Chat"] = ""
    else:
        df["Status Chat"] = df["Status Chat"].fillna("")
        
    def get_shop_id(url):
        # Format dasar Shopee: ...-i.{shop_id}.{item_id}
        match = re.search(r'-i\.(\d+)\.\d+', str(url))
        return match.group(1) if match else None

    # Kumpulkan Shop ID dari toko yang SUDAH dikirimi pesan ("Sent")
    sent_df = df[df["Status Chat"] == "Sent"]
    sent_shop_ids = set()
    for _, row in sent_df.iterrows():
        sid = get_shop_id(row["Link Produk"])
        if sid: sent_shop_ids.add(sid)
        
    # --- OPSI FILTER ---
    print("\n--- Opsi Target Pesan ---")
    print("1. Semua Data (Tanpa Filter)")
    if "Kategori" in df.columns and "Keyword" in df.columns:
        print("2. Berdasarkan Kategori")
        print("3. Berdasarkan Keyword")
        choice = input("Pilih opsi (1/2/3) [default: 1]: ").strip()
    else:
        choice = '1'
        
    filtered_df = df.copy()
    if choice == '2':
        categories = [c for c in df['Kategori'].dropna().unique() if str(c).strip()]
        if categories:
            print("\n--- Daftar Kategori ---")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            cat_choice = input("Pilih nomor Kategori: ").strip()
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                selected_cat = categories[int(cat_choice) - 1]
                filtered_df = df[df['Kategori'] == selected_cat]
                print(f"✅ Filter aktif: Kategori '{selected_cat}'")
            else:
                print("❌ Pilihan tidak valid, menggunakan semua data.")
        else:
            print("⚠️ Tidak ada data Kategori.")
    elif choice == '3':
        keywords = [k for k in df['Keyword'].dropna().unique() if str(k).strip()]
        if keywords:
            print("\n--- Daftar Keyword ---")
            for i, kw in enumerate(keywords, 1):
                print(f"{i}. {kw}")
            kw_choice = input("Pilih nomor Keyword: ").strip()
            if kw_choice.isdigit() and 1 <= int(kw_choice) <= len(keywords):
                selected_kw = keywords[int(kw_choice) - 1]
                filtered_df = df[df['Keyword'] == selected_kw]
                print(f"✅ Filter aktif: Keyword '{selected_kw}'")
            else:
                print("❌ Pilihan tidak valid, menggunakan semua data.")
        else:
            print("⚠️ Tidak ada data Keyword.")

    # Ambil baris yang Status Chat nya masih kosong ATAU berstatus 'Failed' (agar diulang)
    unmessaged_mask = ~filtered_df["Status Chat"].isin(["Sent", "Skip", "Skip (Toko Sama)"])
    unmessaged_df = filtered_df[unmessaged_mask]

    urls_to_process = []
    skipped_count = 0
    
    for _, row in unmessaged_df.iterrows():
        url = row["Link Produk"]
        sid = get_shop_id(url)
        
        # JIKA toko dari produk ini sudah pernah dikirimi pesan di link yg lain
        if sid and sid in sent_shop_ids:
            df.loc[df["Link Produk"] == url, "Status Chat"] = "Skip (Toko Sama)"
            skipped_count += 1
        else:
            urls_to_process.append(url)
            
    # Jika ada yang diskip otomatis karena toko sama, save update ke CSV
    if skipped_count > 0:
        df.to_csv(URL_FILE, index=False)
        print(f"⏩ Melewati {skipped_count} produk karena tokonya sudah pernah dichat sebelumnya.")

    if not urls_to_process:
        print(f"🎉 Semua URL di {URL_FILE} sudah diproses untuk chat!")
        exit()

    urls = urls_to_process[:MAX_URLS]
    print(f"📋 Ditemukan {len(urls_to_process)} toko unik yang belum di-chat.")
    print(f"📋 Akan mengirim pesan ke {len(urls)} toko pada batch ini (max {MAX_URLS})")
    
    # Cetak pesan
    print(f"\n✉️  Pesan yang akan dikirim: '{DEFAULT_MESSAGE}'\n")
    return urls

def update_chat_status(url, status):
    """Update status chat di CSV."""
    try:
        # Baca dengan dtype string untuk Status Chat agar terhindar error float64
        df = pd.read_csv(URL_FILE, dtype={"Status Chat": str}) if "Status Chat" in pd.read_csv(URL_FILE, nrows=0).columns else pd.read_csv(URL_FILE)
        
        if "Status Chat" not in df.columns:
            df["Status Chat"] = ""
        else:
            df["Status Chat"] = df["Status Chat"].fillna("")
            
        df.loc[df["Link Produk"] == url, "Status Chat"] = status
        df.to_csv(URL_FILE, index=False)
    except Exception as e:
        print(f"⚠️ Gagal mengupdate status chat CSV: {e}")

def send_messages():
    with sync_playwright() as p:
        print("Menyambungkan script Python ke Jendela Chrome murni...")
        
        try:
            # Mengkoneksikan ke remote Chrome
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            print("✅ Berhasil tersambung ke Chrome!\n")
        except Exception as e:
            print("❌ Gagal menyambung ke Chrome!")
            print("   Pastikan Chrome dijalankan dengan script launcher atau:")
            print("   google-chrome --remote-debugging-port=9222 --user-data-dir=\"/home/rraangga/shoppe/shopee_debug_profile\"")
            exit()

        print("🏠 Membuka Shopee homepage sebagai pemanasan...")
        page.goto("https://shopee.co.id", timeout=60000)
        page.wait_for_timeout(4000)

        try:
            homepage_url = page.url.lower()
            if "verify" in homepage_url or "traffic/error" in homepage_url:
                print("⚠️  Homepage terblokir!")
                print("   Buka shopee.co.id manual di address bar browser.")
                input("   Tekan ENTER setelah homepage Shopee terbuka normal...")
                page.wait_for_timeout(2000)
        except:
            pass
            
        print("✅ Homepage OK, siap mulai kirim pesan...\n")

        urls = load_urls()

        for idx, url in enumerate(urls, 1):
            print(f"\n==============================")
            print(f"[{idx}/{len(urls)}] Membuka produk untuk chat...")
            
            try:
                new_page = context.new_page()
            except Exception as e:
                print(f"❌ Gagal membuat tab baru: {e}")
                continue

            if idx > 1:
                # JEDA PENTING UNTUK MENCEGAH AKUN DI-BAN/SPAM
                delay = random.uniform(10, 20)
                print(f"⏳ Jeda anti-spam: Menunggu {delay:.1f} detik sebelum toko selanjutnya...")
                new_page.wait_for_timeout(int(delay * 1000))

            try:
                new_page.goto(url, timeout=60000)
                new_page.wait_for_timeout(4000)
            except Exception as e:
                print(f"❌ Gagal membuka halaman produk: {e}")
                update_chat_status(url, "Failed")
                try:
                    new_page.close()
                except:
                    pass
                continue

            # Cek block
            try:
                cur = new_page.url.lower()
                title_text = (new_page.title() or "").lower()
                is_blocked = ("login" in cur or "verify" in cur or "captcha" in cur or "traffic/error" in cur or "halaman tidak tersedia" in title_text)
            except:
                is_blocked = True

            if is_blocked:
                print("⚠️ Halaman terblokir! Menunggu manual input...")
                print(f"   1. Buka di tab tersebut URL ini secara manual.")
                print("   2. Selesaikan verifikasi.")
                input("   ➡️ Tekan ENTER jika produk sudah tampil normal...")
                new_page.wait_for_timeout(2000)
                
            # Tunggu halaman muat dengan sempurna dan scroll sedikit ke bawah
            print("   [+] Scrolling agar halaman toko termuat sempurna...")
            for _ in range(4):
                new_page.mouse.wheel(0, 500)
                new_page.wait_for_timeout(800)
                
            print("Mencoba chat dengan penjual...")
            
            chat_success = False
            try:
                chat_btn = new_page.locator('button:has-text("Chat Sekarang")')
                if chat_btn.count() == 0:
                    chat_btn = new_page.locator('button:has-text("chat sekarang")')
                if chat_btn.count() == 0:
                    # Fallback ke text sederhana yang case insensitive match untuk Chat
                    # Shopee terkadang menggunakan inner div untuk text tersebut
                    chat_btn = new_page.locator('button', has_text="Chat Sekarang")

                if chat_btn.count() > 0:
                    # Terdapat kejadian di mana klik pada chat button tertutup elemen popup promosi
                    try:
                        chat_btn.first.click(timeout=5000)
                    except:
                        # Force click via evaluate as fallback
                        chat_btn.first.evaluate("node => node.click()")

                    print("   [+] Tombol 'Chat Sekarang' diklik.")
                    
                    try:
                        # Tunggu textarea bener-bener muncul dan kelihatan di layar
                        # Gunakan selector yang lebih spesifik yang mengincar placeholder
                        textfield = new_page.locator('textarea[placeholder*="pesan"], textarea[placeholder*="message"]')
                        textfield.wait_for(state="visible", timeout=60000)
                        
                        # Typing efek seperti manusia
                        textfield.fill("") # Pastikan kosong dari karakter bawaan jika ada
                        textfield.type(DEFAULT_MESSAGE, delay=50)
                        new_page.wait_for_timeout(1000)
                        
                        textfield.press("Enter")
                        print(f"   [+] Pesan terkirim: '{DEFAULT_MESSAGE}'")
                        
                        # JEDA SANGAT PENTING: Tunggu beberapa saat agar pesan benar-benar terkirim via jaringan
                        # sebelum tab ditutup, agar request tidak terputus.
                        new_page.wait_for_timeout(5000)
                        
                        chat_success = True
                    except Exception as e:
                        print("   [-] Pop up chat tidak muncul atau gagal menemukan kotak pesan dalam 60 detik.")
                else:
                    print("   [-] Tidak menemukan tombol 'Chat Sekarang' pada halaman ini.")
                    
            except Exception as e:
                print(f"   [!] Gagal karena suatu alasan teknis: {e}")
                
            if chat_success:
                update_chat_status(url, "Sent")
                print("✔ Status di CSV: Sent")
            else:
                update_chat_status(url, "Failed")
                print("❌ Status di CSV: Failed")
                
            try:
                new_page.close()
            except:
                pass
                
        print(f"\n{'='*50}")
        print("🏁 Selesai memproses pengiriman pesan batch ini!")

if __name__ == "__main__":
    send_messages()
