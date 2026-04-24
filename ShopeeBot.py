import os
import sys
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("=======================================================")
    print("███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗███████╗")
    print("██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝")
    print("███████╗███████║██║   ██║██████╔╝█████╗  █████╗  ")
    print("╚════██║██╔══██║██║   ██║██╔═══╝ ██╔══╝  ██╔══╝  ")
    print("███████║██║  ██║╚██████╔╝██║     ███████╗███████╗")
    print("╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝")
    print("                               BOT SCRAPER               ")
    print("=======================================================")
    print("        All-in-One Automation Tools for Shopee         ")
    print("=======================================================\n")

def run_script(script_name, args=None):
    if args is None:
        args = []
    print(f"\n🚀 Menjalankan {script_name} {' '.join(args)}...\n")
    try:
        subprocess.run([sys.executable, script_name] + args)
    except KeyboardInterrupt:
        print(f"\n[!] Eksekusi {script_name} dibatalkan oleh pengguna.")
    except Exception as e:
        print(f"\n[!] Terjadi kesalahan saat menjalankan {script_name}: {e}")
    
    input("\nTekan ENTER untuk kembali ke menu utama...")

def main():
    while True:
        print_header()
        print("Menu Utama:")
        print("  [1] Login Shopee   - Buka browser & login dulu (PENTING)")
        print("  [2] Scrape Links   - Cari link produk & simpan ke CSV")
        print("  [3] Scrape Produk  - Ambil info produk, variasi, & gambar")
        print("  [4] Send Message   - Kirim pesan promo ke toko")
        print("  [5] Preview Hasil  - Lihat hasil scrape dalam bentuk website")
        print("  [6] Update Produk  - Perbarui/Re-scrape produk yang sudah di-scrape")
        print("  [0] Keluar")
        print("─" * 55)
        
        pilihan = input("Masukkan nomor menu (0-6): ").strip()
        
        if pilihan == "1":
            run_script("open_browser.py")
        elif pilihan == "2":
            run_script("scrape_links.py")
        elif pilihan == "3":
            run_script("shoppescrap.py")
        elif pilihan == "4":
            run_script("send_message.py")
        elif pilihan == "5":
            run_script("generate_site.py")
        elif pilihan == "6":
            run_script("shoppescrap.py", args=["--update"])
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan ShopeeBot Scraper. Sampai jumpa! 👋")
            sys.exit(0)
        else:
            print("\n❌ Pilihan tidak valid, coba lagi.")
            input("\nTekan ENTER untuk melanjutkan...")

if __name__ == "__main__":
    main()
