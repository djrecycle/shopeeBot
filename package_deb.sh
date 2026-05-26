#!/bin/bash
set -e

WORKSPACE="/home/rraangga/shoppe"
BUILD_DIR="${WORKSPACE}/build_deb"

echo "🧹 Cleaning previous build directories..."
rm -rf "$BUILD_DIR"
rm -f "${WORKSPACE}/shopeebot_1.0.1-beta_amd64.deb"

echo "📂 Creating Debian directory structure..."
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/pixmaps"
mkdir -p "${BUILD_DIR}/opt/shopeebot"

# ========================================================
# 1. WRITE DEBIAN CONFIGURATION FILES
# ========================================================

echo "📝 Creating DEBIAN/control file..."
cat << 'EOF' > "${BUILD_DIR}/DEBIAN/control"
Package: shopeebot
Version: 1.0.1-beta
Architecture: amd64
Maintainer: Rangga <rraangga@gmail.com>
Depends: python3, python3-pip, python3-venv, nodejs, npm, libnss3, libnspr4, libatk1.0-0, libatk-bridge2.0-0, libcups2, libdrm2, libdbus-1-3, libxcb1, libxkbcommon0, xdg-desktop-portal
Section: utils
Priority: optional
Description: ShopeeBot Automation Suite and Next.js Professional Web Catalog.
 Contains Python GUI controller, message automator, scraper, and a premium Next.js dashboard with SQLite integration.
EOF

echo "📝 Creating DEBIAN/postinst script..."
cat << 'EOF' > "${BUILD_DIR}/DEBIAN/postinst"
#!/bin/bash
set -e

echo "⚙️ Configuring ShopeeBot system files..."

# ── Resolve Node.js: prefer nvm-managed Node (>= 20) over system Node ──────
resolve_node() {
    # Check if /usr/local/bin/node exists and is >= 20
    if command -v /usr/local/bin/node &>/dev/null; then
        local ver
        ver=$(/usr/local/bin/node -e "process.exit(parseInt(process.versions.node) < 20 ? 1 : 0)" 2>/dev/null && echo "ok" || echo "old")
        if [ "$ver" = "ok" ]; then
            export PATH="/usr/local/bin:$PATH"
            echo "✅ Using Node: $(/usr/local/bin/node --version) via /usr/local/bin"
            return
        fi
    fi
    # Search for nvm-managed node >= 20 in common locations
    for NVM_NODE in $(ls -d /home/*/.nvm/versions/node/v[2-9][0-9]*/bin 2>/dev/null | sort -rV); do
        if [ -x "$NVM_NODE/node" ]; then
            export PATH="$NVM_NODE:$PATH"
            # Create symlinks so sudo always finds the right node
            ln -sf "$NVM_NODE/node" /usr/local/bin/node 2>/dev/null || true
            ln -sf "$NVM_NODE/npm"  /usr/local/bin/npm  2>/dev/null || true
            echo "✅ Using Node: $($NVM_NODE/node --version) via nvm at $NVM_NODE"
            return
        fi
    done
    echo "⚠️  WARNING: Could not find Node >= 20. Using system Node: $(node --version)"
}
resolve_node

# 1. Create shared Python virtual environment
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv /opt/shopeebot/shopee-venv
/opt/shopeebot/shopee-venv/bin/pip install --upgrade pip
/opt/shopeebot/shopee-venv/bin/pip install -r /opt/shopeebot/requirements.txt

# 2. Setup shared Playwright Chromium binaries path
echo "🌐 Downloading Playwright Chromium Web Browser binaries..."
export PLAYWRIGHT_BROWSERS_PATH=/opt/shopeebot/.cache/ms-playwright
mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"
/opt/shopeebot/shopee-venv/bin/playwright install chromium

# 3. Setup Next.js Web Dashboard dependencies
echo "📦 Installing Next.js dashboard dependencies..."
cd /opt/shopeebot/web_dashboard
npm install --legacy-peer-deps

# 4. Create empty data directories and placeholder files (data diisi setelah scraping)
echo "📁 Creating empty data directories..."
mkdir -p /opt/shopeebot/gambar
mkdir -p /opt/shopeebot/hasil_md

# Buat shopee_links.csv kosong dengan header jika belum ada
if [ ! -f /opt/shopeebot/shopee_links.csv ]; then
    echo "Kategori,Keyword,Lokasi,Link Produk,Rating,Status Chat,Status,Toko" > /opt/shopeebot/shopee_links.csv
    echo "📄 Created empty shopee_links.csv with headers"
fi

# Buat shopee_state.json kosong jika belum ada
if [ ! -f /opt/shopeebot/shopee_state.json ]; then
    echo '{}' > /opt/shopeebot/shopee_state.json
    echo "📄 Created empty shopee_state.json"
fi

# Sinkronisasi database hanya jika sudah ada data hasil scraping
LINK_COUNT=$(tail -n +2 /opt/shopeebot/shopee_links.csv 2>/dev/null | grep -c '.' || echo 0)
PRODUK_COUNT=$(ls /opt/shopeebot/hasil_md/*.md 2>/dev/null | wc -l || echo 0)
if [ "$LINK_COUNT" -gt 0 ] || [ "$PRODUK_COUNT" -gt 0 ]; then
    echo "⚡ Data ditemukan, menyinkronisasi ke SQLite database..."
    /opt/shopeebot/shopee-venv/bin/python3 /opt/shopeebot/modules/generate_nextjs_site.py sync
else
    echo "ℹ️  Database kosong — jalankan scraper terlebih dahulu untuk mengisi data."
fi

# 5. Open all file permissions so local user accounts can execute and modify the database
echo "🔒 Adjusting folder permissions for multi-user read/write access..."
chmod -R 777 /opt/shopeebot

echo "✅ ShopeeBot package setup successfully completed!"
exit 0
EOF

echo "📝 Creating DEBIAN/prerm script..."
cat << 'EOF' > "${BUILD_DIR}/DEBIAN/prerm"
#!/bin/bash
set -e

echo "🧹 Cleaning up ShopeeBot installation caches and dependencies..."
rm -rf /opt/shopeebot/shopee-venv
rm -rf /opt/shopeebot/.cache
rm -rf /opt/shopeebot/web_dashboard/node_modules
rm -rf /opt/shopeebot/web_dashboard/.next
rm -f /opt/shopeebot/web_dashboard/database.sqlite

exit 0
EOF

# ========================================================
# 2. WRITE SYSTEM INTEGRATION FILES
# ========================================================

echo "📝 Creating /usr/bin/shopeebot system launcher..."
cat << 'EOF' > "${BUILD_DIR}/usr/bin/shopeebot"
#!/bin/bash
export PLAYWRIGHT_BROWSERS_PATH=/opt/shopeebot/.cache/ms-playwright
cd /opt/shopeebot
exec /opt/shopeebot/shopee-venv/bin/python3 /opt/shopeebot/gui_main.py
EOF

echo "📝 Creating /usr/share/applications/shopeebot.desktop launcher..."
cat << 'EOF' > "${BUILD_DIR}/usr/share/applications/shopeebot.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=ShopeeBot Pro
Comment=Shopee Scraper, Messenger, and Catalog Dashboard
Exec=shopeebot
Icon=shopeebot
Terminal=false
Categories=Utility;Automation;
EOF

# Copy Icon
if [ -f "${WORKSPACE}/assets/logo.png" ]; then
    echo "🎨 Copying desktop launcher icon..."
    cp "${WORKSPACE}/assets/logo.png" "${BUILD_DIR}/usr/share/pixmaps/shopeebot.png"
fi

# ========================================================
# 3. COPY APPLICATION FILES
# ========================================================

echo "📂 Copying application files to /opt/shopeebot..."
# Copy specific folders/files to keep the package light and neat
rsync -av --exclude="shopee-venv" \
          --exclude=".git" \
          --exclude=".next" \
          --exclude="node_modules" \
          --exclude="build_deb" \
          --exclude="*.deb" \
          --exclude="shopeebot_*" \
          --exclude="package_deb.sh" \
          --exclude="shopee_debug_profile" \
          --exclude="shopee_profile" \
          --exclude="test_profile_2" \
          --exclude="test_profile_3" \
          --exclude="gambar" \
          --exclude="hasil_md" \
          --exclude="shopee_links.csv" \
          --exclude="shopee_state.json" \
          --exclude="web_dashboard/database.sqlite" \
          "${WORKSPACE}/" "${BUILD_DIR}/opt/shopeebot/"

# ========================================================
# 4. SET DIRECTORY PERMISSIONS & COMPILE
# ========================================================

echo "🔒 Setting executable permissions on system scripts..."
chmod 755 "${BUILD_DIR}/DEBIAN/postinst"
chmod 755 "${BUILD_DIR}/DEBIAN/prerm"
chmod 755 "${BUILD_DIR}/usr/bin/shopeebot"

echo "📦 Building Debian package..."
dpkg-deb --build "$BUILD_DIR" "${WORKSPACE}/shopeebot_1.0.1-beta_amd64.deb"

echo "🎉 Debian package successfully generated at ${WORKSPACE}/shopeebot_1.0.1-beta_amd64.deb"
