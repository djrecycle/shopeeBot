#!/bin/bash

# =======================================================
# ShopeeBot Launcher Script
# Version: 1.0.1-beta
# Status: BETA
# =======================================================

echo "======================================================="
echo "███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗███████╗"
echo "██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝"
echo "███████╗███████║██║   ██║██████╔╝█████╗  █████╗  "
echo "╚════██║██╔══██║██║   ██║██╔═══╝ ██╔══╝  ██╔══╝  "
echo "███████║██║  ██║╚██████╔╝██║     ███████╗███████╗"
echo "╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝"
echo "                LAUNCHER v1.0.1-beta              "
echo "======================================================="

# Tentukan direktori script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Cek Virtual Environment
if [ ! -d "shopee-venv" ]; then
    echo "⚠️  Virtual Environment (shopee-venv) tidak ditemukan."
    echo "📦 Memulai instalasi dependensi secara otomatis..."
    
    # Cek apakah python3 tersedia
    if ! command -v python3 &> /dev/null; then
        echo "❌ Error: Python3 tidak ditemukan di sistem Anda."
        exit 1
    fi

    python3 -m venv shopee-venv
    source shopee-venv/bin/activate
    
    echo "📥 Mengunduh paket yang dibutuhkan (pip)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "🌐 Menginstal browser Playwright..."
    playwright install chromium
    
    echo "✅ Instalasi selesai!"
else
    source shopee-venv/bin/activate
fi

# Jalankan Aplikasi
echo "⚙️  Menjalankan ShopeeBot GUI..."
python3 gui_main.py

# Deactivate venv on exit
deactivate
