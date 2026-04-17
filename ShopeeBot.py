import os
import sys
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("=======================================================")
    print("███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗███████╗██████╗ ")
    print("██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗")
    print("███████╗███████║██║   ██║██████╔╝█████╗  █████╗  ██████╔╝")
    print("╚════██║██╔══██║██║   ██║██╔═══╝ ██╔══╝  ██╔══╝  ██╔═══╝ ")
    print("███████║██║  ██║╚██████╔╝██║     ███████╗███████╗██║     ")
    print("╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝╚═╝     ")
    print("                               BOT SCRAPER               ")
    print("=======================================================")
    print("        All-in-One Automation Tools for Shopee         ")
    print("=======================================================\n")

def run_script(script_name):
    print(f"\n🚀 Menjalankan {script_name}...\n")
    try:
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print(f"\n[!] Eksekusi {script_name} dibatalkan oleh pengguna.")
    except Exception as e:
        print(f"\n[!] Terjadi kesalahan saat menjalankan {script_name}: {e}")
    
    input("\nTekan ENTER untuk kembali ke menu utama...")

def main():
    while True:
        print_header()
        print("Menu Utama:")
        print("  [1] Scrape Links   - Cari link produk & simpan ke CSV")
        print("  [2] Scrape Produk  - Ambil info produk, variasi, & gambar")
        print("  [3] Send Message   - Kirim pesan promo ke toko")
        print("  [0] Keluar")
        print("─" * 55)
        
        pilihan = input("Masukkan nomor menu (0-3): ").strip()
        
        if pilihan == "1":
            run_script("scrape_links.py")
        elif pilihan == "2":
            run_script("shoppescrap.py")
        elif pilihan == "3":
            run_script("send_message.py")
        elif pilihan == "0":
            print("\nTerima kasih telah menggunakan ShopeeBot Scraper. Sampai jumpa! 👋")
            sys.exit(0)
        else:
            print("\n❌ Pilihan tidak valid, coba lagi.")
            input("\nTekan ENTER untuk melanjutkan...")

if __name__ == "__main__":
    main()
