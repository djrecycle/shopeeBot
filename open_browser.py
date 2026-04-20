import os
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

def start_chrome():
    print("\n🔍 Memeriksa apakah Chrome sudah berjalan...")
    
    # URL debugging Chrome
    debug_url = "http://localhost:9222/json/version"
    
    try:
        requests.get(debug_url, timeout=2)
        print("✅ Chrome sudah berjalan dalam mode debugging.")
    except (requests.ConnectionError, requests.Timeout):
        print("🚀 Membuka Chrome baru dengan profil Shopee...")
        
        # Path absolute untuk profile
        chrome_profile = os.path.abspath("shopee_debug_profile")
        
        # Pastikan folder profile ada
        if not os.path.exists(chrome_profile):
            os.makedirs(chrome_profile)
            print(f"📁 Membuat folder profil baru: {chrome_profile}")

        # Jalankan Chrome
        subprocess.Popen([
            "google-chrome",
            "--remote-debugging-port=9222",
            f"--user-data-dir={chrome_profile}",
            "--no-first-run",
            "--no-default-browser-check"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Tunggu Chrome siap
        time.sleep(5)

def login_shopee():
    start_chrome()
    
    print("🔗 Menyambungkan ke browser...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            
            print("🌐 Mengarahkan ke halaman Login Shopee...")
            page.goto("https://shopee.co.id/buyer/login", wait_until="networkidle")
            
            print("\n" + "="*50)
            print("📝 INSTRUKSI:")
            print("1. Silakan Login secara manual di jendela Chrome yang terbuka.")
            print("2. Jika muncul Captcha, silakan selesaikan secara manual.")
            print("3. Pastikan sudah masuk ke Dashboard/Beranda Shopee.")
            print("4. JANGAN TUTUP script ini atau browser sebelum selesai.")
            print("="*50)
            
            print("\nSesi tersimpan di: shopee_debug_profile")
            input("\nTekan ENTER di sini jika sudah selesai login dan ingin menutup script...")
            
            print("✅ Selesai. Browser akan tetap berjalan di background.")
            
        except Exception as e:
            print(f"❌ Terjadi kesalahan: {e}")
            print("\nTips: Jika browser tidak terbuka, pastikan Google Chrome sudah terinstall.")

if __name__ == "__main__":
    login_shopee()
