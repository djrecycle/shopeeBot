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
            --sidebar-bg: rgba(25, 25, 30, 0.8);
            --card-bg: #1e1e24;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --accent: #ff6a4d;
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
            transition: all 0.3s ease;
            z-index: 100;
        }}

        .sidebar-header {{
            padding: 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .sidebar-header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--shopee-orange);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .search-container {{
            padding: 15px 25px;
        }}

        .search-input {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 15px;
            border-radius: 8px;
            color: white;
            outline: none;
            transition: border 0.3s;
        }}

        .search-input:focus {{
            border-color: var(--shopee-orange);
        }}

        .nav-content {{
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }}

        .category-group {{
            margin-bottom: 15px;
        }}

        .category-title {{
            padding: 12px 25px;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: white;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.02);
            transition: background 0.2s;
        }}

        .category-title:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}

        .category-title::after {{
            content: '▼';
            font-size: 0.6rem;
            transition: transform 0.3s;
            color: var(--shopee-orange);
        }}

        .category-group.collapsed .category-title::after {{
            transform: rotate(-90deg);
        }}

        .category-items {{
            max-height: 1000px;
            overflow: hidden;
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .category-group.collapsed .category-items {{
            max-height: 0;
        }}

        .file-item {{
            padding: 12px 25px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
            border-left: 3px solid transparent;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .file-item:hover {{
            background: rgba(255, 255, 255, 0.03);
            color: white;
        }}

        .file-item.active {{
            background: rgba(238, 77, 45, 0.1);
            color: var(--shopee-orange);
            border-left-color: var(--shopee-orange);
            font-weight: 600;
        }}

        /* Main Content Style */
        .main-content {{
            flex: 1;
            overflow-y: auto;
            padding: 40px;
            background: radial-gradient(circle at top right, rgba(238, 77, 45, 0.05), transparent);
        }}

        .content-container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 50px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            min-height: 80vh;
        }}

        .welcome-screen {{
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: var(--text-secondary);
        }}

        .welcome-screen h1 {{
            color: var(--shopee-orange);
            margin-bottom: 20px;
            font-size: 2.5rem;
        }}

        /* Markdown Rendering Overrides */
        #rendered-content h1 {{ margin-bottom: 30px; color: var(--shopee-orange); line-height: 1.2; }}
        #rendered-content h2 {{ margin-top: 40px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }}
        #rendered-content p {{ margin-bottom: 15px; line-height: 1.6; }}
        #rendered-content ul, #rendered-content ol {{ margin-bottom: 20px; padding-left: 20px; }}
        #rendered-content li {{ margin-bottom: 8px; }}
        #rendered-content img {{ max-width: 100%; border-radius: 12px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2); transition: transform 0.3s; cursor: zoom-in; }}
        #rendered-content img:hover {{ transform: scale(1.02); }}
        #rendered-content a {{ color: var(--accent); text-decoration: none; }}
        #rendered-content a:hover {{ text-decoration: underline; }}
        #rendered-content blockquote {{ border-left: 4px solid var(--shopee-orange); padding-left: 20px; color: var(--text-secondary); font-style: italic; margin-bottom: 20px; }}
        #rendered-content table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        #rendered-content th, #rendered-content td {{ border: 1px solid rgba(255,255,255,0.1); padding: 12px; text-align: left; }}
        #rendered-content th {{ background: rgba(255,255,255,0.05); }}

        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.2); }}

        @media (max-width: 768px) {{
            body {{ flex-direction: column; }}
            .sidebar {{ width: 100%; height: auto; max-height: 40vh; }}
            .main-content {{ padding: 20px; }}
            .content-container {{ padding: 25px; }}
        }}
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="sidebar-header">
            <h1>🛍️ ShopeeBot</h1>
            <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 5px;">Product Preview Dashboard</p>
        </div>
        
        <div class="search-container">
            <input type="text" id="search-input" class="search-input" placeholder="Cari nama produk...">
        </div>

        <div class="nav-content" id="nav-content">
            <!-- Navigasi akan diisi JS -->
        </div>
    </div>

    <div class="main-content">
        <div class="content-container" id="content-container">
            <div id="welcome-screen" class="welcome-screen">
                <h1>Selamat Datang!</h1>
                <p>Silakan pilih kategori dan produk di sebelah kiri untuk melihat detail hasil scraping.</p>
                <div style="margin-top: 40px; font-size: 3rem; opacity: 0.5;">📦</div>
            </div>
            <div id="rendered-content" style="display: none;"></div>
        </div>
    </div>

    <script>
        const appData = {json.dumps(data)};
        const navContent = document.getElementById('nav-content');
        const searchInput = document.getElementById('search-input');
        const renderedDiv = document.getElementById('rendered-content');
        const welcomeScreen = document.getElementById('welcome-screen');

        function renderNav(filter = '') {{
            navContent.innerHTML = '';
            
            for (const category in appData) {{
                const filteredProducts = appData[category].filter(p => 
                    p.name.toLowerCase().includes(filter.toLowerCase())
                );

                if (filteredProducts.length === 0) continue;

                const group = document.createElement('div');
                group.className = 'category-group';
                if (filter === '') group.classList.add('collapsed'); // Buka semua jika ada filter search
                
                const title = document.createElement('div');
                title.className = 'category-title';
                title.innerText = category;
                title.onclick = () => group.classList.toggle('collapsed');
                group.appendChild(title);

                const itemsContainer = document.createElement('div');
                itemsContainer.className = 'category-items';

                filteredProducts.forEach(product => {{
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.innerText = product.name;
                    item.title = product.name;
                    item.onclick = (e) => {{
                        e.stopPropagation();
                        showContent(category, product.name, item);
                    }};
                    itemsContainer.appendChild(item);
                }});

                if (filter !== '') group.classList.remove('collapsed');

                group.appendChild(itemsContainer);
                navContent.appendChild(group);
            }}
        }}

        function showContent(category, name, element) {{
            // Update UI Sidebar
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
            element.classList.add('active');

            // Find data
            const product = appData[category].find(p => p.name === name);
            if (!product) return;

            // Render MD
            welcomeScreen.style.display = 'none';
            renderedDiv.style.display = 'block';
            renderedDiv.innerHTML = marked.parse(product.content);
            
            // Scroll to top
            document.querySelector('.main-content').scrollTop = 0;
        }}

        searchInput.oninput = (e) => renderNav(e.target.value);

        // Initial Render
        renderNav();
    </script>
</body>
</html>
    """

    output_file = "preview.html"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_template)
        print(f"✅ Website preview Berhasil dibuat: {output_file}")
        
        # Buka di browser
        file_url = "file://" + os.path.abspath(output_file)
        print(f"🚀 Membuka {output_file} di browser...")
        webbrowser.open(file_url)
    except Exception as e:
        print(f"❌ Gagal menyimpan file preview: {e}")

if __name__ == "__main__":
    generate_site()
