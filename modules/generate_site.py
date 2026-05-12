import os
import json
import webbrowser

def generate_site():
    print("🌐 Memulai pembuatan website preview...")
    
    hasil_md_dir = "hasil_md"
    if not os.path.exists(hasil_md_dir):
        print(f"❌ Folder '{hasil_md_dir}' tidak ditemukan. Silakan jalankan scraper terlebih dahulu.")
        return

    # Scan data
    data = {}
    if not os.path.exists(hasil_md_dir):
        os.makedirs(hasil_md_dir)
        
    categories = sorted([d for d in os.listdir(hasil_md_dir) if os.path.isdir(os.path.join(hasil_md_dir, d))])
    
    for cat in categories:
        data[cat] = []
        cat_path = os.path.join(hasil_md_dir, cat)
        files = sorted([f for f in os.listdir(cat_path) if f.endswith(".md")])
        
        for f in files:
            file_path = os.path.join(cat_path, f)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                data[cat].append({
                    "name": f.replace(".md", ""),
                    "content": content
                })
            except Exception as e:
                print(f"⚠️ Gagal membaca {f}: {e}")

    # Template HTML dengan CSS & JS terintegrasi
    html_template = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopeeBot Preview Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --shopee-orange: #EE4D2D;
            --bg-dark: #0f0f12;
            --sidebar-bg: rgba(25, 25, 30, 0.95);
            --card-bg: #1e1e24;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --accent: #ff6a4d;
            --green-upload: #2ecc71;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* Sidebar Style */
        .sidebar {{
            width: 320px;
            background: var(--sidebar-bg);
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            flex-direction: column;
            z-index: 100;
        }}

        .sidebar-header {{
            padding: 25px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .sidebar-header h1 {{
            font-size: 1.4rem;
            color: var(--shopee-orange);
            font-weight: 800;
        }}

        /* Markup Tool */
        .markup-tool {{
            padding: 20px;
            background: rgba(255, 255, 255, 0.03);
            margin: 15px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .markup-tool h3 {{
            font-size: 0.85rem;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }}

        .markup-tool h3 span {{ color: var(--shopee-orange); }}

        .slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 4px;
            background: #333;
            border-radius: 5px;
            outline: none;
        }}

        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: var(--shopee-orange);
            border-radius: 50%;
            cursor: pointer;
        }}

        .search-container {{ padding: 0 20px; }}
        .search-input {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 8px;
            color: white;
            font-size: 0.85rem;
        }}

        .nav-content {{
            flex: 1;
            overflow-y: auto;
            padding: 15px 0;
        }}

        .category-title {{
            padding: 10px 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-secondary);
            cursor: pointer;
            background: rgba(255,255,255,0.02);
            display: flex;
            justify-content: space-between;
        }}

        .file-item {{
            padding: 8px 30px;
            font-size: 0.85rem;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            transition: all 0.2s;
        }}

        .file-item:hover {{ background: rgba(255,255,255,0.05); }}
        .file-item.active {{ color: var(--shopee-orange); background: rgba(238, 77, 45, 0.1); border-left: 3px solid var(--shopee-orange); }}

        /* Main Content */
        .main-content {{
            flex: 1;
            overflow-y: auto;
            padding: 40px;
        }}

        .content-container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 40px;
            border-radius: 16px;
            word-break: break-word; /* FIX UNTUK TEKS PANJANG */
            overflow-wrap: break-word;
        }}

        /* Styles for specific MD elements */
        #rendered-content h1 {{ font-size: 1.6rem; margin-bottom: 20px; line-height: 1.3; }}
        #rendered-content h2 {{ font-size: 1.1rem; margin-top: 30px; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; }}
        
        .price-card {{
            display: flex;
            gap: 20px;
            background: rgba(255,255,255,0.02);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.05);
        }}

        .price-sub {{ flex: 1; }}
        .price-sub .label {{ font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; }}
        .price-sub .val {{ font-size: 1.3rem; font-weight: 700; display: block; margin-top: 5px; }}
        .price-sub .val.promo {{ color: var(--green-upload); }}

        .variation-grid {{
            display: grid;
            gap: 10px;
        }}

        .var-row {{
            background: rgba(255,255,255,0.02);
            padding: 12px 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .var-info {{ display: flex; flex-direction: column; gap: 2px; }}
        .var-name {{ font-size: 0.9rem; font-weight: 600; }}
        .var-price-old {{ font-size: 0.75rem; color: var(--text-secondary); text-decoration: line-through; }}
        .var-price-new {{ font-size: 1rem; font-weight: 700; color: var(--green-upload); }}

    </style>
</head>
<body>

    <div class="sidebar">
        <div class="sidebar-header">
            <h1>🛍️ ShopeeBot</h1>
        </div>
        
        <div class="markup-tool">
            <h3>Markup <span id="markup-val">20%</span></h3>
            <input type="range" min="0" max="100" value="20" class="slider" id="markup-slider">
        </div>

        <div class="search-container">
            <input type="text" id="search-input" class="search-input" placeholder="Cari produk...">
        </div>

        <div class="nav-content" id="nav-content"></div>
    </div>

    <div class="main-content">
        <div class="content-container">
            <div id="rendered-content">
                <div style="text-align: center; padding: 100px 0; color: #555;">
                    <h2>Pilih produk di sidebar</h2>
                </div>
            </div>
        </div>
    </div>

    <script>
        const appData = {json.dumps(data)};
        const navContent = document.getElementById('nav-content');
        const searchInput = document.getElementById('search-input');
        const renderedDiv = document.getElementById('rendered-content');
        const markupSlider = document.getElementById('markup-slider');
        const markupVal = document.getElementById('markup-val');

        let activeProduct = null;

        function formatRp(n) {{
            return "Rp" + n.toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");
        }}

        function parseRp(s) {{
            return parseInt(s.split(",")[0].replace(/[^0-9]/g, "")) || 0;
        }}

        function calcPrice(s, p) {{
            if (s.includes("-")) {{
                let parts = s.split("-");
                let m1 = Math.ceil(parseRp(parts[0]) * (1 + p/100));
                let m2 = Math.ceil(parseRp(parts[1]) * (1 + p/100));
                return formatRp(m1) + " - " + formatRp(m2);
            }}
            return formatRp(Math.ceil(parseRp(s) * (1 + p/100)));
        }}

        function process(content, p) {{
            let html = marked.parse(content);
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, 'text/html');

            // 1. Harga Utama
            let h2s = Array.from(doc.querySelectorAll('h2'));
            let ph = h2s.find(h => h.innerText.includes("Harga"));
            if (ph && ph.nextElementSibling) {{
                let orig = ph.nextElementSibling.innerText.trim();
                let card = document.createElement('div');
                card.className = 'price-card';
                card.innerHTML = `
                    <div class="price-sub"><span class="label">Asli</span><span class="val">${{orig}}</span></div>
                    <div class="price-sub"><span class="label">Upload (+${{p}}%)</span><span class="val promo">${{calcPrice(orig, p)}}</span></div>
                `;
                ph.nextElementSibling.replaceWith(card);
            }}

            // 2. Variasi
            let vh = h2s.find(h => h.innerText.includes("Variasi"));
            if (vh && vh.nextElementSibling && vh.nextElementSibling.tagName === "UL") {{
                let ul = vh.nextElementSibling;
                let grid = document.createElement('div');
                grid.className = 'variation-grid';
                Array.from(ul.querySelectorAll('li')).forEach(li => {{
                    let parts = li.innerHTML.split("|");
                    let np = parts[0].split(":");
                    if (np.length >= 2) {{
                        let name = np.slice(0, -1).join(":").trim();
                        let price = np[np.length-1].trim();
                        let row = document.createElement('div');
                        row.className = 'var-row';
                        row.innerHTML = `
                            <div class="var-info">
                                <span class="var-name">${{name}}</span>
                                <span class="var-price-old">Asli: ${{price}}</span>
                            </div>
                            <div class="var-price-new">${{calcPrice(price, p)}}</div>
                        `;
                        grid.appendChild(row);
                    }}
                }});
                ul.replaceWith(grid);
            }}

            return doc.body.innerHTML;
        }}

        function renderNav(f = '') {{
            navContent.innerHTML = '';
            for (let cat in appData) {{
                let prods = appData[cat].filter(p => p.name.toLowerCase().includes(f.toLowerCase()));
                if (!prods.length) continue;
                let title = document.createElement('div');
                title.className = 'category-title';
                title.innerText = cat;
                navContent.appendChild(title);
                prods.forEach(p => {{
                    let item = document.createElement('div');
                    item.className = 'file-item';
                    item.innerText = p.name;
                    item.onclick = () => {{
                        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                        item.classList.add('active');
                        activeProduct = p;
                        refresh();
                    }};
                    navContent.appendChild(item);
                }});
            }}
        }}

        function refresh() {{
            if (!activeProduct) return;
            renderedDiv.innerHTML = process(activeProduct.content, parseInt(markupSlider.value));
        }}

        markupSlider.oninput = (e) => {{
            markupVal.innerText = e.target.value + "%";
            refresh();
        }};
        searchInput.oninput = (e) => renderNav(e.target.value);
        renderNav();
    </script>
</body>
</html>
    """

    output_file = "preview.html"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)
        print(f"✅ Website preview Berhasil diperbaiki: {output_file}")
        file_url = "file://" + os.path.abspath(output_file)
        webbrowser.open(file_url)
    except Exception as e:
        print(f"❌ Gagal: {e}")

if __name__ == "__main__":
    generate_site()
