import os
import json
import webbrowser
import sys

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
    <title>ShopeeBot Premium Preview</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --primary: #FF4D2D;
            --primary-hover: #E03E20;
            --bg: #0A0A0C;
            --card-bg: #16161A;
            --sidebar-bg: rgba(18, 18, 22, 0.8);
            --text: #F0F0F0;
            --text-muted: #94A3B8;
            --border: rgba(255, 255, 255, 0.08);
            --accent-green: #10B981;
            --glass: rgba(255, 255, 255, 0.03);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            scrollbar-width: thin;
            scrollbar-color: var(--primary) transparent;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* --- Sidebar --- */
        .sidebar {{
            width: 340px;
            background: var(--sidebar-bg);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .sidebar-header {{
            padding: 30px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo-box {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary), #FF8C00);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(255, 77, 45, 0.3);
        }}

        .sidebar-header h1 {{
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #fff, #aaa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .btn-export-main {{
            margin: 0 20px 15px;
            background: linear-gradient(135deg, #FF8C00, var(--primary));
            color: white;
            border: none;
            padding: 12px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 4px 15px rgba(255, 77, 45, 0.2);
            transition: transform 0.2s;
        }}

        .btn-export-main:hover {{ transform: translateY(-2px); }}

        .markup-card {{
            margin: 0 20px 20px;
            padding: 20px;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 16px;
        }}

        .markup-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .markup-header span {{ font-size: 0.75rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }}
        .markup-header b {{ font-size: 1.1rem; color: var(--primary); }}

        .slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            background: #222;
            border-radius: 10px;
            outline: none;
        }}

        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            background: var(--primary);
            border-radius: 50%;
            cursor: pointer;
            border: 3px solid #fff;
            box-shadow: 0 0 10px rgba(255, 77, 45, 0.4);
        }}

        .search-box {{
            padding: 0 20px 20px;
        }}

        .search-input {{
            width: 100%;
            background: #1A1A20;
            border: 1px solid var(--border);
            padding: 12px 16px;
            border-radius: 12px;
            color: white;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{ border-color: var(--primary); }}

        .nav-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }}

        .cat-group {{ margin-bottom: 5px; }}
        .cat-label {{
            padding: 12px 24px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.02);
            transition: background 0.2s;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }}

        .cat-label:hover {{ background: rgba(255,255,255,0.05); }}
        .cat-label i {{ transition: transform 0.3s; font-style: normal; display: inline-block; width: 12px; }}
        .cat-label.collapsed i {{ transform: rotate(0deg); }}
        .cat-label i {{ transform: rotate(90deg); }}
        
        .cat-items {{
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        
        .cat-items.collapsed {{
            display: none;
        }}

        .btn-icon-export {{
            background: rgba(255, 77, 45, 0.1);
            color: var(--primary);
            border: none;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.65rem;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-icon-export:hover {{ background: var(--primary); color: white; }}

        .prod-item {{
            padding: 10px 24px;
            font-size: 0.85rem;
            cursor: pointer;
            color: var(--text-muted);
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .prod-item:hover {{ background: rgba(255, 255, 255, 0.03); color: #fff; }}
        .prod-item.active {{
            background: rgba(255, 77, 45, 0.08);
            color: var(--primary);
            font-weight: 600;
            border-left: 3px solid var(--primary);
        }}

        /* --- Main Content --- */
        .main {{
            flex: 1;
            overflow-y: auto;
            background: radial-gradient(circle at top right, #1A1A20, var(--bg));
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .content-card {{
            width: 100%;
            max-width: 850px;
            background: var(--card-bg);
            border-radius: 24px;
            border: 1px solid var(--border);
            padding: 40px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            position: relative;
        }}

        .header-actions {{
            position: sticky;
            top: -40px;
            background: var(--card-bg);
            padding: 20px 0;
            margin-top: -20px;
            margin-bottom: 20px;
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            gap: 10px;
        }}

        .action-group {{ display: flex; gap: 8px; }}

        .btn-action {{
            background: var(--glass);
            color: var(--text);
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .btn-action:hover {{ background: rgba(255,255,255,0.08); border-color: var(--text-muted); }}
        .btn-action.primary {{ background: var(--primary); color: white; border: none; }}
        .btn-action.primary:hover {{ background: var(--primary-hover); }}

        #rendered-content h1 {{ font-size: 1.8rem; line-height: 1.2; margin-bottom: 24px; color: #fff; }}
        #rendered-content h2 {{ 
            font-size: 1rem; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            color: var(--primary); 
            margin-top: 40px; 
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        #rendered-content h2::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: var(--border);
        }}

        .price-box {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 30px;
        }}

        .price-item {{
            background: #1F1F24;
            padding: 20px;
            border-radius: 16px;
            border: 1px solid var(--border);
        }}

        .price-label {{ font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px; display: block; }}
        .price-val {{ font-size: 1.5rem; font-weight: 700; color: #fff; }}
        .price-val.highlight {{ color: var(--accent-green); }}

        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}

        .info-card {{
            background: var(--glass);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        .info-card b {{ display: block; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 5px; }}
        .info-card a {{ color: var(--primary); text-decoration: none; font-size: 0.85rem; word-break: break-all; }}
        .info-card a:hover {{ text-decoration: underline; }}

        .spec-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 10px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        .spec-table tr {{ transition: background 0.2s; }}
        .spec-table tr:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
        .spec-table tr:nth-child(odd) {{ background: rgba(255,255,255,0.04); }}
        .spec-table tr:hover {{ background: rgba(255,255,255,0.08); }}
        
        .spec-table td {{ padding: 14px 20px; font-size: 0.9rem; border-bottom: 1px solid var(--border); }}
        .spec-table td:first-child {{ color: var(--primary); font-weight: 700; width: 35%; background: rgba(255, 77, 45, 0.03); }}
        .spec-table td:last-child {{ color: #fff; }}

        .desc-container {{
            line-height: 1.7;
            color: #D1D5DB;
            font-size: 0.95rem;
            white-space: pre-wrap;
        }}

        .tag-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 20px;
        }}

        .tag {{
            background: var(--glass);
            border: 1px solid var(--border);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .var-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 8px;
        }}

        .var-table tr {{
            background: var(--glass);
            transition: background 0.2s;
        }}

        .var-table tr:hover {{ background: rgba(255,255,255,0.05); }}

        .var-table td {{
            padding: 12px 20px;
            font-size: 0.9rem;
        }}

        .var-table td:first-child {{ border-radius: 12px 0 0 12px; font-weight: 600; }}
        .var-table td:last-child {{ border-radius: 0 12px 12px 0; text-align: right; font-weight: 800; color: var(--accent-green); }}
        .var-old-price {{ font-size: 0.7rem; color: var(--text-muted); text-decoration: line-through; display: block; }}

        .img-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}

        .img-grid img {{
            width: 100%;
            aspect-ratio: 1;
            object-fit: cover;
            border-radius: 12px;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .img-grid img:hover {{ transform: scale(1.03); }}

        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 100px 0;
            color: var(--text-muted);
        }}

        .empty-state svg {{ width: 64px; height: 64px; margin-bottom: 20px; opacity: 0.2; }}

    </style>
</head>
<body>

    <div class="sidebar">
        <div class="sidebar-header">
            <div class="logo-box">🛒</div>
            <h1>ShopeeBot <span>PRO</span></h1>
        </div>

        <button class="btn-export-main" onclick="exportAll()">
            📊 Export Semua ke Excel
        </button>
        
        <div class="markup-card">
            <div class="markup-header">
                <span>Persentase Harga Upload</span>
                <b id="markup-val">20%</b>
            </div>
            <input type="range" min="0" max="100" value="20" class="slider" id="markup-slider">
        </div>

        <div class="search-box">
            <input type="text" id="search-input" class="search-input" placeholder="Cari produk...">
        </div>

        <div class="nav-list" id="nav-list"></div>
    </div>

    <div class="main">
        <div class="content-card" id="content-card" style="display: none;">
            <div class="header-actions">
                <span id="prod-name-sticky" style="font-weight: 700; font-size: 0.9rem; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"></span>
                <div class="action-group">
                    <button class="btn-action" onclick="exportActiveProduct()">📊 Export Barang</button>
                    <button class="btn-action primary" onclick="copyDesc()">📋 Salin Deskripsi</button>
                </div>
            </div>
            <div id="rendered-content"></div>
        </div>

        <div class="empty-state" id="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h2>Pilih produk untuk melihat preview</h2>
            <p>Data diambil dari folder hasil_md</p>
        </div>
    </div>

    <script>
        const appData = {json.dumps(data)};
        const navList = document.getElementById('nav-list');
        const searchInput = document.getElementById('search-input');
        const renderedDiv = document.getElementById('rendered-content');
        const markupSlider = document.getElementById('markup-slider');
        const markupVal = document.getElementById('markup-val');
        const contentCard = document.getElementById('content-card');
        const emptyState = document.getElementById('empty-state');
        const stickyName = document.getElementById('prod-name-sticky');

        let activeProduct = null;
        let activeCategory = "";

        function formatRp(n) {{
            return "Rp" + Math.ceil(n).toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");
        }}

        function parseRp(s) {{
            if (!s) return 0;
            return parseInt(s.replace(/[^0-9]/g, "")) || 0;
        }}

        function calcPrice(s, p) {{
            if (s.includes("-")) {{
                let parts = s.split("-");
                let m1 = parseRp(parts[0]) * (1 + p/100);
                let m2 = parseRp(parts[1]) * (1 + p/100);
                return formatRp(m1) + " - " + formatRp(m2);
            }}
            return formatRp(parseRp(s) * (1 + p/100));
        }}

        function cleanText(text) {{
            return text.replace(/[~_=]{{2,}}/g, '')
                       .replace(/^\\s*[~_=]\\s*/gm, '')
                       .trim();
        }}

        function extractTags(text) {{
            const tags = text.match(/#[\\w\\u00C0-\\u024F]+/g);
            return tags ? [...new Set(tags)] : [];
        }}

        function process(content, p) {{
            let html = marked.parse(content);
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, 'text/html');

            const result = document.createElement('div');

            // 1. Title
            const title = doc.querySelector('h1')?.innerText || "Tanpa Judul";
            const h1 = document.createElement('h1');
            h1.innerText = title;
            result.appendChild(h1);
            stickyName.innerText = title;

            // 2. Harga Utama
            const h2s = Array.from(doc.querySelectorAll('h2'));
            const ph = h2s.find(h => h.innerText.includes("Harga"));
            if (ph && ph.nextElementSibling) {{
                const orig = ph.nextElementSibling.innerText.split('Harga Upload')[0].replace('Harga Asli:', '').trim();
                const pBox = document.createElement('div');
                pBox.className = 'price-box';
                pBox.innerHTML = `
                    <div class="price-item"><span class="price-label">Harga Asli</span><span class="price-val">${{orig}}</span></div>
                    <div class="price-item"><span class="price-label">Harga Jual (+${{p}}%)</span><span class="price-val highlight">${{calcPrice(orig, p)}}</span></div>
                `;
                result.appendChild(pBox);
            }}

            // 3. Link Info
            const shopH = h2s.find(h => h.innerText.includes("Toko"));
            const prodH = h2s.find(h => h.innerText.includes("Produk") && !h.innerText.includes("Variasi") && !h.innerText.includes("Gambar"));
            
            if (shopH || prodH) {{
                const iGrid = document.createElement('div');
                iGrid.className = 'info-grid';
                if (shopH && shopH.nextElementSibling) {{
                    iGrid.innerHTML += `<div class="info-card"><b>Store Link</b><a href="${{shopH.nextElementSibling.innerText.trim()}}" target="_blank">${{shopH.nextElementSibling.innerText.trim()}}</a></div>`;
                }}
                if (prodH && prodH.nextElementSibling) {{
                    iGrid.innerHTML += `<div class="info-card"><b>Product Link</b><a href="${{prodH.nextElementSibling.innerText.trim()}}" target="_blank">${{prodH.nextElementSibling.innerText.trim()}}</a></div>`;
                }}
                result.appendChild(iGrid);
            }}

            // 4. Spesifikasi (Advanced Parsing)
            const specH = h2s.find(h => h.innerText.includes("Spesifikasi"));
            if (specH) {{
                const sTitle = document.createElement('h2');
                sTitle.innerText = "📋 Spesifikasi Produk";
                result.appendChild(sTitle);
                
                const table = document.createElement('table');
                table.className = 'spec-table';
                
                let sBody = "";
                let curr = specH.nextElementSibling;
                while (curr && curr.tagName !== "H2") {{
                    sBody += curr.innerText + "\\n";
                    curr = curr.nextElementSibling;
                }}
                
                const lines = sBody.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                
                for (let i = 0; i < lines.length; i++) {{
                    let line = lines[i];
                    let key = "", val = "";
                    
                    // Header skip
                    if (line.toLowerCase() === "spesifikasi | detail") continue;

                    if (line.includes('|')) {{
                        const parts = line.split('|');
                        key = parts[0].trim();
                        val = parts.slice(1).join('|').trim();
                    }} else if (line.includes(':')) {{
                        const parts = line.split(':');
                        key = parts[0].trim();
                        val = parts.slice(1).join(':').trim();
                    }} else {{
                        // No separator, check if next line is a value
                        if (i + 1 < lines.length && !lines[i+1].includes('|') && !lines[i+1].includes(':')) {{
                            key = line;
                            val = lines[i+1];
                            i++; // skip next
                        }} else {{
                            key = line;
                            val = "-";
                        }}
                    }}
                    
                    if (key && key !== "-") {{
                        // Hapus tulisan Shopee di awal kategori
                        if (key.toLowerCase().includes("kategori") && val.startsWith("Shopee ")) {{
                            val = val.replace(/^Shopee\s+/, "");
                        }}
                        
                        const tr = document.createElement('tr');
                        tr.innerHTML = `<td>${{key}}</td><td>${{val}}</td>`;
                        table.appendChild(tr);
                    }}
                }}
                
                if (table.children.length === 0) {{
                    const sBox = document.createElement('div');
                    sBox.className = 'spec-box';
                    sBox.innerText = sBody.trim() || "Tidak ditemukan";
                    result.appendChild(sBox);
                }} else {{
                    result.appendChild(table);
                }}
            }}

            // 5. Deskripsi & Tags
            const dh = h2s.find(h => h.innerText.includes("Deskripsi"));
            if (dh) {{
                const dTitle = document.createElement('h2');
                dTitle.innerText = "📝 Deskripsi Produk";
                result.appendChild(dTitle);

                let dBody = "";
                let curr = dh.nextElementSibling;
                while (curr && curr.tagName !== "H2") {{
                    dBody += curr.innerText + "\\n";
                    curr = curr.nextElementSibling;
                }}

                const cleaned = cleanText(dBody);
                const tags = extractTags(cleaned);
                const pureDesc = cleaned.replace(/#[\\w\\u00C0-\\u024F]+/g, '').trim();

                const dDiv = document.createElement('div');
                dDiv.className = 'desc-container';
                dDiv.id = 'copy-target';
                dDiv.innerText = pureDesc;
                result.appendChild(dDiv);

                if (tags.length) {{
                    const tDiv = document.createElement('div');
                    tDiv.className = 'tag-container';
                    tags.forEach(t => {{
                        const span = document.createElement('span');
                        span.className = 'tag';
                        span.innerText = t;
                        tDiv.appendChild(span);
                    }});
                    result.appendChild(tDiv);
                }}
            }}

            // 6. Variasi
            const vh = h2s.find(h => h.innerText.includes("Variasi"));
            if (vh && vh.nextElementSibling) {{
                const vTitle = document.createElement('h2');
                vTitle.innerText = "🔧 Variasi & Stok";
                result.appendChild(vTitle);

                const table = document.createElement('table');
                table.className = 'var-table';
                
                const items = vh.nextElementSibling.tagName === "UL" 
                    ? Array.from(vh.nextElementSibling.querySelectorAll('li'))
                    : [];

                items.forEach(li => {{
                    const text = li.innerText.split('|')[0];
                    const parts = text.split(':');
                    if (parts.length >= 2) {{
                        const name = parts.slice(0, -1).join(':').trim();
                        const price = parts[parts.length-1].trim().split('(')[0].trim();
                        
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${{name}}</td>
                            <td><span class="var-old-price">Asli: ${{price}}</span>${{calcPrice(price, p)}}</td>
                        `;
                        table.appendChild(tr);
                    }}
                }});
                result.appendChild(table);
            }}

            // 7. Gambar
            const images = Array.from(doc.querySelectorAll('img')).map(img => img.src);
            if (images.length) {{
                const iTitle = document.createElement('h2');
                iTitle.innerText = "🖼️ Galeri Produk";
                result.appendChild(iTitle);

                const grid = document.createElement('div');
                grid.className = 'img-grid';
                images.forEach(src => {{
                    const img = document.createElement('img');
                    img.src = src;
                    img.onclick = () => window.open(src, '_blank');
                    grid.appendChild(img);
                }});
                result.appendChild(grid);
            }}

            return result.innerHTML;
        }}

        function renderNav(f = '') {{
            navList.innerHTML = '';
            for (let cat in appData) {{
                const prods = appData[cat].filter(p => p.name.toLowerCase().includes(f.toLowerCase()));
                if (!prods.length) continue;

                const group = document.createElement('div');
                group.className = 'cat-group';
                
                const label = document.createElement('div');
                label.className = 'cat-label collapsed';
                label.innerHTML = `
                    <span><i>▶</i> ${{cat}} (${{prods.length}})</span>
                    <button class="btn-icon-export" onclick="event.stopPropagation(); exportCategory('${{cat}}')" title="Export Kategori Ini">📊 Export</button>
                `;
                
                const itemsContainer = document.createElement('div');
                itemsContainer.className = 'cat-items collapsed';
                
                label.onclick = () => {{
                    label.classList.toggle('collapsed');
                    itemsContainer.classList.toggle('collapsed');
                }};
                
                group.appendChild(label);

                prods.forEach(p => {{
                    const item = document.createElement('div');
                    item.className = 'prod-item';
                    item.innerHTML = `<span>📦</span> ${{p.name}}`;
                    item.onclick = () => {{
                        document.querySelectorAll('.prod-item').forEach(el => el.classList.remove('active'));
                        item.classList.add('active');
                        activeProduct = p;
                        activeCategory = cat;
                        emptyState.style.display = 'none';
                        contentCard.style.display = 'block';
                        refresh();
                    }};
                    itemsContainer.appendChild(item);
                }});
                group.appendChild(itemsContainer);
                navList.appendChild(group);
            }}
        }}

        function refresh() {{
            if (!activeProduct) return;
            renderedDiv.innerHTML = process(activeProduct.content, parseInt(markupSlider.value));
        }}

        // --- Export Logic ---
        function downloadCSV(data, filename) {{
            const csv = data.map(row => row.map(v => '"' + (v || '').toString().replace(/"/g, '""') + '"').join(',')).join('\\n');
            const blob = new Blob(["\\ufeff", csv], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        function parseProduct(p, cat, markup) {{
            const temp = document.createElement('div');
            temp.innerHTML = marked.parse(p.content);
            const h2s = Array.from(temp.querySelectorAll('h2'));
            
            const title = temp.querySelector('h1')?.innerText || p.name;
            const ph = h2s.find(h => h.innerText.includes("Harga"));
            const origPrice = ph && ph.nextElementSibling ? ph.nextElementSibling.innerText.split('Harga Upload')[0].replace('Harga Asli:', '').trim() : "0";
            const sellPrice = calcPrice(origPrice, markup);
            
            const shopH = h2s.find(h => h.innerText.includes("Toko"));
            const shopLink = shopH && shopH.nextElementSibling ? shopH.nextElementSibling.innerText.trim() : "";
            
            const prodH = h2s.find(h => h.innerText.includes("Produk") && !h.innerText.includes("Variasi") && !h.innerText.includes("Gambar"));
            const prodLink = prodH && prodH.nextElementSibling ? prodH.nextElementSibling.innerText.trim() : "";
            
            return [title, origPrice, sellPrice, cat, prodLink, shopLink];
        }}

        function exportActiveProduct() {{
            if (!activeProduct) return;
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            const row = parseProduct(activeProduct, activeCategory, parseInt(markupSlider.value));
            downloadCSV([headers, row], `Produk_${{activeProduct.name.substring(0, 20)}}.csv`);
        }}

        function exportCategory(cat) {{
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            const markup = parseInt(markupSlider.value);
            const rows = appData[cat].map(p => parseProduct(p, cat, markup));
            downloadCSV([headers, ...rows], `Kategori_${{cat}}.csv`);
        }}

        function exportAll() {{
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            const markup = parseInt(markupSlider.value);
            let allRows = [];
            for (let cat in appData) {{
                const rows = appData[cat].map(p => parseProduct(p, cat, markup));
                allRows = [...allRows, ...rows];
            }}
            downloadCSV([headers, ...allRows], "Semua_Produk.csv");
        }}

        function copyDesc() {{
            const text = document.getElementById('copy-target').innerText;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.querySelector('.btn-action.primary');
                const old = btn.innerText;
                btn.innerText = "✅ Tersalin!";
                setTimeout(() => btn.innerText = old, 2000);
            }});
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
        if "--no-open" not in sys.argv:
            webbrowser.open(file_url)
    except Exception as e:
        print(f"❌ Gagal: {e}")

if __name__ == "__main__":
    generate_site()
