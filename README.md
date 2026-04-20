# 🛍️ ShopeeBot Scraper

ShopeeBot Scraper adalah sebuah alat otomatisasi (Automation Tool) berbasis Python untuk melakukan scraping produk, mengumpulkan data spesifikasi, serta mengirimkan pesan massal (broadcast) kepada penjual (seller) di platform Shopee.

Bot ini dilengkapi dengan antarmuka terminal interaktif yang sangat mudah digunakan, serta memiliki kemampuan anti-bot/stealth melalui pengontrolan browser secara *real-time* (menggunakan Playwright).

---

## 🌟 Fitur Utama

1. **Scrape Links (Pencari Link Produk)** 🔍
   - Pencarian berdasarkan **Keyword** (kata kunci) atau spesifik **Toko** (username/URL toko).
   - Pengurutan hasil berdasarkan Relevansi, Terbaru, Terlaris, atau Harga.
   - Filter **Lokasi Penjual** secara presisi.
   - Filter **Minimum Rating** produk.
   - Manajemen kategori penyimpanan tabel data (otomatis tersimpan ke `shopee_links.csv`).

2. **Scrape Produk (Pengambil Detail Produk)** 📦
   - Otomatis membuka URL produk yang belum diproses dari file CSV.
   - Menyimpan seluruh informasi penting seperti Judul, Harga, Deskripsi, dan Spesifikasi lengkap.
   - Mampu mengekstrak **semua variasi** beserta harga masing-masing.
   - Mengunduh otomatis **gambar aseli/resolusi tinggi** dari produk (tanpa watermark).
   - Seluruh data diekstrak rapih ke dalam format file Markdown (`.md`).

3. **Send Message (Pengirim Pesan Otomatis)** ✉️
   - Kirim *Automated Chat* kepada penjual dari daftar link produk (misal: penawaran afiliasi/dropship).
   - Smart Filtering: Hanya mengirim 1 kali pesan untuk penjual yang sama (menggunakan ID Toko).
   - Support seleksi data berdasarkan Keyword atau Kategori.
   - Jeda interaksi cerdas (*randomized delay*) untuk meminimalisasi deteksi spamming oleh Shopee.

---

## 🛠️ Persyaratan Sistem

- Sistem Operasi: Windows, macOS, atau Linux
- [Python 3.8+](https://www.python.org/downloads/)
- Google Chrome terinstal di perangkat.

---

## ⚙️ Instalasi

1. **Clone repositori ini (opsional jika mendownload ZIP):**
   ```bash
   git clone https://github.com/username/ShopeeBot.git
   cd ShopeeBot
   ```

2. **Buat dan aktifkan virtual environment (Disarankan):**
   ```bash
   # Di Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Di Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependensi library yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Browser bawaan Playwright:**
   ```bash
   playwright install
   ```

---

## 🚀 Cara Penggunaan

Penggunaan bot ini sangat gampang karena telah disatukan ke dalam satu menu. Cukup jalankan perintah ini pada terminal/command prompt:

```bash
python ShopeeBot.py
```

Anda akan melihat tampilan Header Menu:
```
=======================================================
███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗███████╗
██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
███████╗███████║██║   ██║██████╔╝█████╗  █████╗  
╚════██║██╔══██║██║   ██║██╔═══╝ ██╔══╝  ██╔══╝  
███████║██║  ██║╚██████╔╝██║     ███████╗███████╗
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝
                               BOT SCRAPER               
=======================================================
```

Pilih **Nomor Menu** sesuai dengan apa yang akan Anda jalankan:
- **[1] Login Shopee**: Langkah awal yang sangat disarankan. Buka browser melalui menu ini untuk Login ke akun Shopee Anda secara manual agar sesi/cookie tersimpan.
- **[2] Scrape Links**: Mulailah dari sini untuk mengumpulkan link ke dalam CSV.
- **[3] Scrape Produk**: Jika CSV sudah berisi data link, gunakan menu ini untuk mengekstrak detail produk dan mengunduh foto/gambar produk.
- **[4] Send Message**: Gunakan menu ini untuk mem-broadcast chat ke seller berdasarkan data yang sudah ada di CSV.
- **[5] Preview Hasil**: Gunakan menu ini untuk melihat seluruh hasil scraping Anda dalam bentuk dashboard website yang modern dan interaktif.

---

## 📂 Struktur File dan Folder

Setelah dijalankan, skrip secara otomatis akan membuat file dan struktur folder berikut:

- `shopee_links.csv` — File inti untuk menyimpan database pencarian Anda. (Termasuk Status Scrape dan Status Chat).
- `hasil_md/` — Folder tempat di mana hasil kompilasi detail setiap produk (dalam format Markdown/MD) akan disimpan.
- `gambar/` — Folder unduhan galeri serta variasi foto alat produk Anda.
- `shopee_debug_profile/` — Ini akan dibuat secara independen oleh Google Chrome untuk menyimpan cookie session Anda *(Ini diabaikan di .gitignore agar tidak ter-upload tanpa disengaja)*.

---

## ⚠️ Peringatan Penting & Troubleshooting!

1. **Pemblokiran / Captcha**: Antivirus bawaan Shopee (Datadome/Traffic Error) kemungkinan besar akan muncul mendeteksi bot Anda.
   - **Solusi**: Biarkan jendela Chromium terbuka, selesaikan slide verifikasi (Captcha) atau Log-in di jendela tersebut secara manual, lalu tekan `ENTER` pada terminal untuk mengizinkan bot melanjutkan pekerjaannya kembali. Poses *session* ini akan otomatis selalu disimpan oleh bot.

2. **Deteksi Spam / Ratelimit**: Jangan menjalankan bot terlalu barbar / kencang dengan mematikan randomized delay di dalam source code, ini akan membahayakan akun Shopee Anda (Shadow-banned). Gunakan jeda secukupnya yang sudah tertulis di dalam `send_message.py` dan biasakan memproses dalam beberapa iterasi data saja contohnya per 5 batch.

---

## 📜 Lisensi
Sistem scraper ini dikembangkan sebagai alat bantu pribadi/edukasional semata. Harap mematuhi aturan dan pedoman interaksi Term of Service (TOS) yang diatur oleh Shopee Indonesia. Tanggung jawab penggunaan kembali sepenuhnya ditanggung oleh pengguna yang memodifikasi sistem ini.
