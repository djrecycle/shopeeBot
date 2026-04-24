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
   - Mendeteksi dan mencocokkan secara otomatis **Kode Kategori** Shopee (berdasarkan referensi `Kode_Kategori.xlsx`).
   - Mengunduh otomatis **gambar aseli/resolusi tinggi** dari produk (tanpa watermark).
   - Seluruh data diekstrak rapih ke dalam format file Markdown (`.md`).

3. **Preview Hasil & Ekspor Excel (Dashboard Interaktif)** 📊
   - Melihat seluruh hasil scraping Anda dalam bentuk dashboard website yang modern dan interaktif.
   - Mengatur persentase kenaikan **Harga Upload** secara dinamis (contoh: +20%) langsung dari antarmuka web.
   - Mengekspor langsung produk ke dalam format `.xlsx` (menggunakan susunan `Template.xlsx`) yang langsung siap di-upload (Mass Upload) ke Shopee.

4. **Update Produk (Re-scrape)** 🔄
   - Memperbarui data produk yang sebelumnya sudah pernah di-scrape (berguna saat ada perubahan harga di toko sumber atau update fitur scraper).
   - Tanpa harus memisahkan file CSV, bot cerdas memilih ulang produk yang sebelumnya berstatus *Done*.

5. **Send Message (Pengirim Pesan Otomatis)** ✉️
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
        All-in-One Automation Tools for Shopee         
=======================================================

Menu Utama:
  [1] Login Shopee   - Buka browser & login dulu (PENTING)
  [2] Scrape Links   - Cari link produk & simpan ke CSV
  [3] Scrape Produk  - Ambil info produk, variasi, & gambar
  [4] Send Message   - Kirim pesan promo ke toko
  [5] Preview Hasil  - Lihat hasil scrape dalam bentuk website
  [6] Update Produk  - Perbarui/Re-scrape produk yang sudah di-scrape
  [0] Keluar
───────────────────────────────────────────────────────
```

Pilih **Nomor Menu** sesuai dengan apa yang akan Anda jalankan:
- **[1] Login Shopee**: Langkah awal yang sangat disarankan. Buka browser melalui menu ini untuk Login ke akun Shopee Anda secara manual agar sesi/cookie tersimpan.
- **[2] Scrape Links**: Mulailah dari sini untuk mengumpulkan link ke dalam CSV.
- **[3] Scrape Produk**: Jika CSV sudah berisi data link, gunakan menu ini untuk mengekstrak detail produk dan mengunduh foto/gambar produk.
- **[4] Send Message**: Gunakan menu ini untuk mem-broadcast chat ke seller berdasarkan data yang sudah ada di CSV.
- **[5] Preview Hasil**: Gunakan menu ini untuk melihat seluruh hasil scraping Anda dalam bentuk dashboard website yang modern dan interaktif. Anda juga dapat mengubah persentase Harga Upload dan melakukan Ekspor ke file Excel untuk keperluan *Mass Upload*.
- **[6] Update Produk**: Gunakan menu ini untuk men-scrape ulang (memperbarui) data produk yang sudah pernah di-scrape sebelumnya (misal ketika ada perubahan harga dari toko sumber atau update fitur baru pada scraper).

---

## 📂 Struktur File dan Folder

Setelah dijalankan, skrip secara otomatis akan membuat file dan struktur folder berikut:

- `shopee_links.csv` — File inti untuk menyimpan database pencarian Anda. (Termasuk Status Scrape dan Status Chat).
- `Kode_Kategori.xlsx` — (Disediakan) Basis data referensi nama kategori ke kode angka unik kategori Shopee.
- `Template.xlsx` — (Disediakan) Template master Shopee yang menjadi dasar format hasil file ekspor `.xlsx`.
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
