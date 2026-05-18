import os
import json
import webbrowser
import sys
import csv

HTML_CONTENT = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopeeBot Pro Dashboard</title>
    
    <!-- Fonts & Libraries -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    
    <!-- Tailwind Custom Configuration -->
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              shopee: '#FF4D2D',
              shopeeHover: '#E03E20',
              darkBg: '#0A0A0C',
              darkCard: '#16161A',
              darkBorder: 'rgba(255, 255, 255, 0.08)',
              glassBg: 'rgba(255, 255, 255, 0.03)'
            },
            fontFamily: {
              sans: ['Outfit', 'sans-serif']
            }
          }
        }
      }
    </script>
    
    <!-- Global CSS Styles -->
    <style>
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 77, 45, 0.3);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 77, 45, 0.6);
        }
        body {
            background-color: #0A0A0C;
            color: #F0F0F0;
        }
        .glass-card {
            background: rgba(22, 22, 26, 0.65);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .shopee-gradient {
            background: linear-gradient(135deg, #FF8C00, #FF4D2D);
        }
        .text-glow {
            text-shadow: 0 0 15px rgba(255, 77, 45, 0.35);
        }
    </style>
</head>
<body class="overflow-x-hidden">
    <div id="root"></div>

    <!-- React App JSX Code Block -->
    <script type="text/babel">
        // Inject data from placeholders
        const appData = /*__APP_DATA_PLACEHOLDER__*/ || {};
        const dbData = /*__DB_DATA_PLACEHOLDER__*/ || [];

        // --- Custom SVG Icons ---
        const HomeIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
        );

        const PreviewIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
        );

        const DatabaseIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
        );

        const SearchIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        );

        const CopyIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
            </svg>
        );

        const CheckIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
        );

        const ExternalLinkIcon = ({ className = "w-4 h-4" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
        );

        const FolderIcon = ({ className = "w-5 h-5" }) => (
            <svg className={className} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
        );

        const ChevronIcon = ({ className = "w-4 h-4", direction = "right" }) => {
            const rot = direction === "down" ? "rotate-90" : direction === "left" ? "rotate-180" : "";
            return (
                <svg className={`${className} transform transition-transform duration-200 ${rot}`} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
            );
        };

        const StarIcon = ({ className = "w-4 h-4" }) => (
            <svg className={className} fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
        );

        // --- Global Helpers ---
        const formatRp = (n) => {
            return "Rp" + Math.ceil(n).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
        };

        const parseRp = (s) => {
            if (!s) return 0;
            return parseInt(s.replace(/[^0-9]/g, "")) || 0;
        };

        const calcPriceVal = (priceStr, markupPct) => {
            if (!priceStr) return "Rp0";
            if (priceStr.includes("-")) {
                let parts = priceStr.split("-");
                let m1 = parseRp(parts[0]) * (1 + markupPct / 100);
                let m2 = parseRp(parts[1]) * (1 + markupPct / 100);
                return formatRp(m1) + " - " + formatRp(m2);
            }
            return formatRp(parseRp(priceStr) * (1 + markupPct / 100));
        };

        const cleanText = (text) => {
            return text.replace(/[~_=]{2,}/g, '').replace(/^\\s*[~_=]\\s*/gm, '').trim();
        };

        const extractTags = (text) => {
            const tags = text.match(/#[\\w\\u00C0-\\u024F]+/g);
            return tags ? [...new Set(tags)] : [];
        };

        // Custom parser to split markdown contents into clean React-renderable objects
        const parseMarkdownProduct = (content) => {
            const parser = new DOMParser();
            const html = marked.parse(content);
            const doc = parser.parseFromString(html, 'text/html');

            const title = doc.querySelector('h1')?.innerText || "Tanpa Judul";
            const h2s = Array.from(doc.querySelectorAll('h2'));

            // 1. Price
            let originalPrice = "0";
            const ph = h2s.find(h => h.innerText.includes("Harga"));
            if (ph && ph.nextElementSibling) {
                originalPrice = ph.nextElementSibling.innerText.split('Harga Upload')[0].replace('Harga Asli:', '').trim();
            }

            // 2. Links
            let storeLink = "";
            const shopH = h2s.find(h => h.innerText.includes("Toko"));
            if (shopH && shopH.nextElementSibling) {
                storeLink = shopH.nextElementSibling.innerText.trim();
            }

            let productLink = "";
            const prodH = h2s.find(h => h.innerText.includes("Produk") && !h.innerText.includes("Variasi") && !h.innerText.includes("Gambar"));
            if (prodH && prodH.nextElementSibling) {
                productLink = prodH.nextElementSibling.innerText.trim();
            }

            // 3. Specs
            const specs = [];
            const specH = h2s.find(h => h.innerText.includes("Spesifikasi"));
            if (specH) {
                let sBody = "";
                let curr = specH.nextElementSibling;
                while (curr && curr.tagName !== "H2") {
                    sBody += curr.innerText + "\\n";
                    curr = curr.nextElementSibling;
                }
                const lines = sBody.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                lines.forEach((line, idx) => {
                    if (line.toLowerCase() === "spesifikasi | detail") return;
                    let key = "", val = "";
                    if (line.includes('|')) {
                        const parts = line.split('|');
                        key = parts[0].trim();
                        val = parts.slice(1).join('|').trim();
                    } else if (line.includes(':')) {
                        const parts = line.split(':');
                        key = parts[0].trim();
                        val = parts.slice(1).join(':').trim();
                    } else {
                        if (idx + 1 < lines.length && !lines[idx+1].includes('|') && !lines[idx+1].includes(':')) {
                            key = line;
                            val = lines[idx+1];
                        } else {
                            key = line;
                            val = "-";
                        }
                    }
                    if (key && key !== "-") {
                        if (key.toLowerCase().includes("kategori") && val.startsWith("Shopee ")) {
                            val = val.replace(/^Shopee\\s+/, "");
                        }
                        specs.push({ key, val });
                    }
                });
            }

            // 4. Description & Tags
            let description = "";
            let tags = [];
            const dh = h2s.find(h => h.innerText.includes("Deskripsi"));
            if (dh) {
                let dBody = "";
                let curr = dh.nextElementSibling;
                while (curr && curr.tagName !== "H2") {
                    dBody += curr.innerText + "\\n";
                    curr = curr.nextElementSibling;
                }
                const cleaned = cleanText(dBody);
                const matchedTags = extractTags(cleaned);
                tags = matchedTags ? [...new Set(matchedTags)] : [];
                description = cleaned.replace(/#[\\w\\u00C0-\\u024F]+/g, '').trim();
            }

            // 5. Variations
            const variations = [];
            const vh = h2s.find(h => h.innerText.includes("Variasi"));
            if (vh && vh.nextElementSibling) {
                const items = vh.nextElementSibling.tagName === "UL" 
                  ? Array.from(vh.nextElementSibling.querySelectorAll('li'))
                  : [];
                items.forEach(li => {
                    const aTag = li.querySelector('a');
                    const imgUrl = aTag ? aTag.getAttribute('href') : null;
                    const text = li.innerText.split('|')[0];
                    const parts = text.split(':');
                    if (parts.length >= 2) {
                        const name = parts.slice(0, -1).join(':').trim();
                        const price = parts[parts.length-1].trim().split('(')[0].trim();
                        variations.push({ name, price, imgUrl });
                    }
                });
            }

            // 6. Gallery Images
            const images = Array.from(doc.querySelectorAll('img')).map(img => img.src);

            return { title, originalPrice, storeLink, productLink, specs, description, tags, variations, images };
        };

        const downloadCSV = (rows, filename) => {
            const csvContent = "\\ufeff" + rows.map(row => 
                row.map(v => '"' + (v || '').toString().replace(/"/g, '""') + '"').join(',')
            ).join('\\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };

        const handleExportProduct = (product, cat, markup) => {
            const parsed = parseMarkdownProduct(product.content);
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            const row = [
                parsed.title,
                parsed.originalPrice,
                calcPriceVal(parsed.originalPrice, markup),
                cat,
                parsed.productLink,
                parsed.storeLink
            ];
            downloadCSV([headers, row], `Produk_${product.name.substring(0, 20)}.csv`);
        };

        const handleExportCategory = (cat, catItems, markup) => {
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            const rows = catItems.map(p => {
                const parsed = parseMarkdownProduct(p.content);
                return [
                    parsed.title,
                    parsed.originalPrice,
                    calcPriceVal(parsed.originalPrice, markup),
                    cat,
                    parsed.productLink,
                    parsed.storeLink
                ];
            });
            downloadCSV([headers, ...rows], `Kategori_${cat}.csv`);
        };

        const handleExportAll = (markup) => {
            const headers = ["Judul Produk", "Harga Asli", "Harga Jual", "Kategori", "Link Produk", "Link Toko"];
            let allRows = [];
            for (let cat in appData) {
                const rows = appData[cat].map(p => {
                    const parsed = parseMarkdownProduct(p.content);
                    return [
                        parsed.title,
                        parsed.originalPrice,
                        calcPriceVal(parsed.originalPrice, markup),
                        cat,
                        parsed.productLink,
                        parsed.storeLink
                    ];
                });
                allRows = [...allRows, ...rows];
            }
            downloadCSV([headers, ...allRows], "Semua_Produk.csv");
        };

        // --- Main App React Component ---
        function App() {
            const [activeTab, setActiveTab] = React.useState('dashboard');
            const [selectedProduct, setSelectedProduct] = React.useState(null);
            const [selectedCategory, setSelectedCategory] = React.useState("");
            const [markup, setMarkup] = React.useState(20);
            
            // Search & Accordions
            const [searchQuery, setSearchQuery] = React.useState("");
            const [expandedCategories, setExpandedCategories] = React.useState({});
            
            // Database Tab filters
            const [dbSearch, setDbSearch] = React.useState("");
            const [dbCatFilter, setDbCatFilter] = React.useState("");
            const [dbStatusFilter, setDbStatusFilter] = React.useState("");
            const [dbChatFilter, setDbChatFilter] = React.useState("");
            const [dbPage, setDbPage] = React.useState(1);
            
            // Copy state & image zoom modal
            const [copied, setCopied] = React.useState(false);
            const [lightboxImg, setLightboxImg] = React.useState(null);
            const [activeProdTab, setActiveProdTab] = React.useState('overview');

            // Quick reset scroll on product change
            React.useEffect(() => {
                setActiveProdTab('overview');
            }, [selectedProduct]);

            // Escape listener for Modal Zoom
            React.useEffect(() => {
                const handleEsc = (e) => {
                    if (e.key === "Escape") setLightboxImg(null);
                };
                window.addEventListener("keydown", handleEsc);
                return () => window.removeEventListener("keydown", handleEsc);
            }, []);

            // Accordion toggle helpers
            const toggleCategory = (cat) => {
                setExpandedCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
            };

            // Copy to clipboard description
            const triggerCopy = (text) => {
                navigator.clipboard.writeText(text).then(() => {
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                });
            };

            // Calculate dbData statistics
            const totalTargets = dbData.length;
            const scrapedTargets = dbData.filter(x => x.status === 'Done' || x.status === 'Sent').length;
            const pendingTargets = totalTargets - scrapedTargets;
            const chatSentTargets = dbData.filter(x => x.chat_status === 'Sent').length;
            const chatSkippedTargets = dbData.filter(x => x.chat_status && x.chat_status.includes('Skip')).length;
            const chatFailedTargets = dbData.filter(x => x.chat_status === 'Failed').length;
            const chatPendingTargets = totalTargets - chatSentTargets - chatSkippedTargets;

            const scrapePct = totalTargets > 0 ? Math.round((scrapedTargets / totalTargets) * 100) : 0;
            const chatPct = totalTargets > 0 ? Math.round((chatSentTargets / totalTargets) * 100) : 0;

            // Extract unique categories from dbData for filter
            const dbCategories = React.useMemo(() => {
                const cats = dbData.map(d => d.category).filter(Boolean);
                return [...new Set(cats)].sort();
            }, []);

            // Filter targets list (for Database view)
            const filteredDbData = React.useMemo(() => {
                return dbData.filter(row => {
                    const matchesSearch = 
                        (row.shop || "").toLowerCase().includes(dbSearch.toLowerCase()) ||
                        (row.link || "").toLowerCase().includes(dbSearch.toLowerCase()) ||
                        (row.keyword || "").toLowerCase().includes(dbSearch.toLowerCase()) ||
                        (row.category || "").toLowerCase().includes(dbSearch.toLowerCase());
                    
                    const matchesCat = !dbCatFilter || row.category === dbCatFilter;
                    
                    const matchesStatus = !dbStatusFilter || 
                        (dbStatusFilter === "Done" && (row.status === "Done" || row.status === "Sent")) ||
                        (dbStatusFilter === "Pending" && (row.status !== "Done" && row.status !== "Sent"));
                    
                    const matchesChat = !dbChatFilter ||
                        (dbChatFilter === "Sent" && row.chat_status === "Sent") ||
                        (dbChatFilter === "Skip" && row.chat_status && row.chat_status.includes("Skip")) ||
                        (dbChatFilter === "Failed" && row.chat_status === "Failed") ||
                        (dbChatFilter === "Pending" && (!row.chat_status || row.chat_status === "nan" || row.chat_status === "-"));

                    return matchesSearch && matchesCat && matchesStatus && matchesChat;
                });
            }, [dbSearch, dbCatFilter, dbStatusFilter, dbChatFilter]);

            // Database pagination variables
            const pageSize = 25;
            const totalPages = Math.ceil(filteredDbData.length / pageSize);
            const paginatedDbData = React.useMemo(() => {
                const startIdx = (dbPage - 1) * pageSize;
                return filteredDbData.slice(startIdx, startIdx + pageSize);
            }, [filteredDbData, dbPage]);

            // DB stats per category
            const dbCategoryStats = React.useMemo(() => {
                const stats = {};
                dbData.forEach(item => {
                    const c = item.category || "Uncategorized";
                    if (!stats[c]) stats[c] = { total: 0, scraped: 0, chatSent: 0 };
                    stats[c].total += 1;
                    if (item.status === 'Done' || item.status === 'Sent') stats[c].scraped += 1;
                    if (item.chat_status === 'Sent') stats[c].chatSent += 1;
                });
                return stats;
            }, []);

            // Active product parsed details
            const parsedProductDetails = React.useMemo(() => {
                if (!selectedProduct) return null;
                return parseMarkdownProduct(selectedProduct.content);
            }, [selectedProduct]);

            return (
                <div class="min-h-screen flex flex-col bg-[#0A0A0C]">
                    
                    {/* --- Top Header Navigation Bar --- */}
                    <header class="h-20 bg-darkCard/90 backdrop-blur-md border-b border-darkBorder flex items-center justify-between px-8 sticky top-0 z-40">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 shopee-gradient rounded-xl flex items-center justify-center shadow-lg shadow-shopee/20 font-bold text-lg">🛒</div>
                            <div>
                                <h1 class="text-lg font-extrabold tracking-tight">ShopeeBot <span class="text-shopee text-glow">PRO</span></h1>
                                <p class="text-[10px] text-gray-500 font-medium uppercase tracking-wider">Premium Automation Console</p>
                            </div>
                        </div>

                        {/* Navigation Tabs */}
                        <div class="flex items-center gap-2 bg-black/40 border border-darkBorder rounded-xl p-1">
                            <button 
                                onClick={() => setActiveTab('dashboard')} 
                                class={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2 ${activeTab === 'dashboard' ? 'bg-shopee text-white shadow-md shadow-shopee/15' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                            >
                                <HomeIcon className="w-4 h-4" /> Overview
                            </button>
                            <button 
                                onClick={() => {
                                    setActiveTab('preview');
                                    // Expand first category if nothing is chosen
                                    if (!selectedProduct) {
                                        const firstCat = Object.keys(appData)[0];
                                        if (firstCat) setExpandedCategories({ [firstCat]: true });
                                    }
                                }} 
                                class={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2 ${activeTab === 'preview' ? 'bg-shopee text-white shadow-md shadow-shopee/15' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                            >
                                <PreviewIcon className="w-4 h-4" /> Web Preview
                            </button>
                            <button 
                                onClick={() => setActiveTab('database')} 
                                class={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2 ${activeTab === 'database' ? 'bg-shopee text-white shadow-md shadow-shopee/15' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                            >
                                <DatabaseIcon className="w-4 h-4" /> Database Links
                            </button>
                        </div>

                        {/* Secondary utility action */}
                        <div class="flex items-center gap-3">
                            <button 
                                onClick={() => handleExportAll(markup)} 
                                class="bg-glassBg hover:bg-shopee/10 hover:border-shopee border border-darkBorder text-gray-300 hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                            >
                                📊 Export Semua CSV
                            </button>
                        </div>
                    </header>

                    {/* --- Main Dashboard Body Viewports --- */}
                    <main class="flex-1 w-full max-w-[1700px] mx-auto p-8">
                        
                        {/* =========================================================================
                            TAB 1: 🏠 OVERVIEW DASHBOARD VIEW
                            ========================================================================= */}
                        {activeTab === 'dashboard' && (
                            <div class="space-y-8 animate-[fadeIn_0.2s_ease-out]">
                                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                    <div>
                                        <h2 class="text-2xl font-extrabold text-white">Dashboard Ringkasan Kampanye</h2>
                                        <p class="text-sm text-gray-400 mt-1">Status dan metrik performa bot real-time dari hasil crawling shopee_links.csv.</p>
                                    </div>
                                    <div class="flex items-center gap-2 bg-darkCard/60 border border-darkBorder px-4 py-2 rounded-xl text-xs font-semibold text-gray-400">
                                        ⏱️ Terakhir Diupdate: <span class="text-white ml-1">{new Date().toLocaleDateString('id-ID', {day: 'numeric', month: 'long', year: 'numeric'})}</span>
                                    </div>
                                </div>

                                {/* --- Analytics Numeric Stat Cards --- */}
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                    
                                    {/* Card 1: Total Links in CSV */}
                                    <div class="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[140px]">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Total Database Link</span>
                                            <div class="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400"><DatabaseIcon className="w-4 h-4" /></div>
                                        </div>
                                        <div class="mt-4">
                                            <div class="text-3xl font-extrabold text-white tracking-tight">{totalTargets}</div>
                                            <p class="text-[10px] text-gray-500 mt-1">Link Target Terkumpul di CSV</p>
                                        </div>
                                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-blue-500"></div>
                                    </div>

                                    {/* Card 2: Scrape Completed */}
                                    <div class="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[140px]">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Sukses Di-scrape</span>
                                            <div class="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400"><CheckIcon className="w-4 h-4" /></div>
                                        </div>
                                        <div class="mt-3">
                                            <div class="text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-2">
                                                {scrapedTargets}
                                                <span class="text-xs text-emerald-400 font-semibold">({scrapePct}%)</span>
                                            </div>
                                            {/* Progress meter */}
                                            <div class="w-full bg-white/5 h-1.5 rounded-full overflow-hidden mt-2">
                                                <div class="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${scrapePct}%` }}></div>
                                            </div>
                                        </div>
                                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
                                    </div>

                                    {/* Card 3: Broadcast Messenger Sent */}
                                    <div class="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[140px]">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Broadcast Pesan</span>
                                            <div class="w-8 h-8 rounded-lg bg-shopee/10 border border-shopee/20 flex items-center justify-center text-shopee"><svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg></div>
                                        </div>
                                        <div class="mt-3">
                                            <div class="text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-2">
                                                {chatSentTargets}
                                                <span class="text-xs text-shopee font-semibold">({chatPct}%)</span>
                                            </div>
                                            {/* Progress meter */}
                                            <div class="w-full bg-white/5 h-1.5 rounded-full overflow-hidden mt-2">
                                                <div class="bg-shopee h-full rounded-full transition-all duration-500" style={{ width: `${chatPct}%` }}></div>
                                            </div>
                                        </div>
                                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-shopee"></div>
                                    </div>

                                    {/* Card 4: Categories */}
                                    <div class="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[140px]">
                                        <div class="flex items-center justify-between">
                                            <span class="text-xs font-bold uppercase tracking-wider text-gray-400">Kategori Aktif</span>
                                            <div class="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400"><FolderIcon className="w-4 h-4" /></div>
                                        </div>
                                        <div class="mt-4">
                                            <div class="text-3xl font-extrabold text-white tracking-tight">{Object.keys(appData).length}</div>
                                            <p class="text-[10px] text-gray-500 mt-1">Folder Hasil MD Dibuat</p>
                                        </div>
                                        <div class="absolute bottom-0 left-0 right-0 h-1 bg-purple-500"></div>
                                    </div>

                                </div>

                                {/* --- Campaign Category Analytics Breakdown --- */}
                                <div class="glass-card rounded-2xl p-8 space-y-6">
                                    <div class="flex items-center justify-between">
                                        <div>
                                            <h3 class="text-lg font-bold text-white">Status Lengkap Per Kategori</h3>
                                            <p class="text-xs text-gray-400 mt-0.5">Analisis kemajuan detail crawling dan chatting dari setiap kategori produk.</p>
                                        </div>
                                    </div>

                                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {Object.keys(dbCategoryStats).map(cat => {
                                            const stat = dbCategoryStats[cat];
                                            const pct = Math.round((stat.scraped / stat.total) * 100) || 0;
                                            return (
                                                <div 
                                                    key={cat} 
                                                    onClick={() => {
                                                        setActiveTab('preview');
                                                        setSelectedCategory(cat);
                                                        setExpandedCategories({ [cat]: true });
                                                        // Select first item if available
                                                        if (appData[cat] && appData[cat][0]) {
                                                            setSelectedProduct(appData[cat][0]);
                                                        }
                                                    }}
                                                    class="p-5 bg-black/35 hover:bg-white/5 border border-darkBorder hover:border-shopee/40 rounded-xl space-y-4 cursor-pointer transition-all duration-300 group"
                                                >
                                                    <div class="flex items-center justify-between">
                                                        <span class="text-sm font-bold text-gray-200 group-hover:text-shopee transition-colors">{cat}</span>
                                                        <span class="text-[10px] px-2 py-0.5 rounded bg-white/5 font-semibold text-gray-400 group-hover:bg-shopee/10 group-hover:text-shopee transition-colors">{stat.total} Target</span>
                                                    </div>
                                                    
                                                    {/* Stat lines */}
                                                    <div class="grid grid-cols-2 gap-4 text-xs">
                                                        <div>
                                                            <span class="text-gray-500 block text-[10px] uppercase font-bold tracking-wider">Crawl Selesai</span>
                                                            <b class="text-gray-200 text-sm mt-0.5 block">{stat.scraped} / {stat.total}</b>
                                                        </div>
                                                        <div>
                                                            <span class="text-gray-500 block text-[10px] uppercase font-bold tracking-wider">Chat Terkirim</span>
                                                            <b class="text-gray-200 text-sm mt-0.5 block">{stat.chatSent} / {stat.total}</b>
                                                        </div>
                                                    </div>

                                                    {/* Progress bar */}
                                                    <div class="space-y-1">
                                                        <div class="flex items-center justify-between text-[10px] text-gray-500 font-semibold">
                                                            <span>Persentase Crawl</span>
                                                            <span class="text-emerald-400">{pct}%</span>
                                                        </div>
                                                        <div class="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                                                            <div class="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${pct}%` }}></div>
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* =========================================================================
                            TAB 2: 🌐 WEB PREVIEW INSPECTOR VIEW
                            ========================================================================= */}
                        {activeTab === 'preview' && (
                            <div class="flex flex-col lg:flex-row gap-8 min-h-[calc(100vh-14rem)] animate-[fadeIn_0.2s_ease-out]">
                                
                                {/* --- Left Sidebar Selector Panel --- */}
                                <div class="w-full lg:w-[350px] shrink-0 space-y-6">
                                    
                                    {/* Price markup adjustment slider card */}
                                    <div class="glass-card rounded-2xl p-5 space-y-4">
                                        <div class="flex items-center justify-between text-xs uppercase font-bold tracking-wider text-gray-400">
                                            <span>Persentase Harga Jual</span>
                                            <span class="text-shopee text-sm font-extrabold">+{markup}%</span>
                                        </div>
                                        <input 
                                            type="range" 
                                            min="0" 
                                            max="100" 
                                            value={markup}
                                            onChange={(e) => setMarkup(parseInt(e.target.value))}
                                            class="w-full accent-shopee h-1.5 bg-black/50 rounded-lg cursor-pointer"
                                        />
                                        {/* Slider Quick presets */}
                                        <div class="grid grid-cols-4 gap-1.5">
                                            {[0, 10, 20, 35, 50, 100].map(pct => (
                                                <button 
                                                    key={pct}
                                                    onClick={() => setMarkup(pct)}
                                                    class={`py-1 rounded text-[10px] font-bold border transition-all ${markup === pct ? 'border-shopee bg-shopee/10 text-shopee' : 'border-darkBorder text-gray-500 hover:text-white hover:border-gray-600 bg-white/[0.01]'}`}
                                                >
                                                    +{pct}%
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Sidebar category list browser */}
                                    <div class="glass-card rounded-2xl overflow-hidden flex flex-col max-h-[600px]">
                                        <div class="p-4 border-b border-darkBorder space-y-3">
                                            <h3 class="text-sm font-bold text-white">Browser File Markdown</h3>
                                            <div class="relative flex items-center">
                                                <input 
                                                    type="text" 
                                                    placeholder="Cari produk..." 
                                                    value={searchQuery}
                                                    onChange={(e) => setSearchQuery(e.target.value)}
                                                    class="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee focus:ring-1 focus:ring-shopee/25 rounded-xl pl-10 pr-4 py-2 text-xs text-white outline-none transition-all"
                                                />
                                                <div class="absolute left-3.5 text-gray-500"><SearchIcon className="w-3.5 h-3.5" /></div>
                                            </div>
                                        </div>

                                        {/* Accordion Categories */}
                                        <div class="flex-1 overflow-y-auto p-2 space-y-1">
                                            {Object.keys(appData).map(cat => {
                                                const filteredProds = appData[cat].filter(p => 
                                                    p.name.toLowerCase().includes(searchQuery.toLowerCase())
                                                );
                                                if (filteredProds.length === 0) return null;

                                                const isExpanded = expandedCategories[cat];

                                                return (
                                                    <div key={cat} class="rounded-lg overflow-hidden border border-transparent">
                                                        {/* Category Accordion Header */}
                                                        <div 
                                                            onClick={() => toggleCategory(cat)}
                                                            class={`flex items-center justify-between p-3 rounded-lg cursor-pointer text-xs font-bold transition-all ${isExpanded ? 'bg-shopee/5 text-shopee' : 'text-gray-300 hover:bg-white/5'}`}
                                                        >
                                                            <div class="flex items-center gap-2">
                                                                <ChevronIcon direction={isExpanded ? "down" : "right"} className="w-3 h-3 text-gray-500" />
                                                                <FolderIcon className="w-3.5 h-3.5" />
                                                                <span>{cat}</span>
                                                            </div>
                                                            <span class="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400 font-semibold">{filteredProds.length}</span>
                                                        </div>

                                                        {/* Category Child Items */}
                                                        {isExpanded && (
                                                            <div class="pl-5 pr-2 py-1 space-y-0.5">
                                                                {filteredProds.map(p => (
                                                                    <div 
                                                                        key={p.name}
                                                                        onClick={() => {
                                                                            setSelectedProduct(p);
                                                                            setSelectedCategory(cat);
                                                                        }}
                                                                        class={`px-3 py-2 rounded-md text-[11px] font-medium cursor-pointer transition-all flex items-center gap-2 ${selectedProduct?.name === p.name ? 'bg-shopee/10 border border-shopee/20 text-shopee font-semibold' : 'text-gray-400 hover:text-white hover:bg-white/[0.02]'}`}
                                                                    >
                                                                        <span>📦</span>
                                                                        <span class="truncate">{p.name}</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>

                                </div>

                                {/* --- Right Product Detailed Preview Inspector --- */}
                                <div class="flex-1 min-w-0">
                                    
                                    {/* Empty state: If no product is selected yet */}
                                    {!selectedProduct ? (
                                        <div class="glass-card rounded-3xl p-16 flex flex-col items-center justify-center text-center space-y-6 min-h-[500px]">
                                            <div class="w-20 h-20 rounded-full bg-glassBg flex items-center justify-center text-gray-500 border border-darkBorder animate-pulse">
                                                <svg className="w-10 h-10" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                                </svg>
                                            </div>
                                            <div class="space-y-2">
                                                <h3 class="text-xl font-bold text-white">Buka Preview Produk</h3>
                                                <p class="text-xs text-gray-400 max-w-sm leading-relaxed">Silakan pilih salah satu file produk markdown di sidebar untuk melihat preview dashboard detail yang profesional.</p>
                                            </div>
                                        </div>
                                    ) : (
                                        // Product Details Panel
                                        <div class="glass-card rounded-3xl p-8 space-y-6">
                                            
                                            {/* Details Header (Breadcrumbs, title, main quick actions) */}
                                            <div class="border-b border-darkBorder pb-6 space-y-4">
                                                <div class="text-[10px] uppercase font-bold tracking-widest text-gray-500 flex items-center gap-1.5">
                                                    <span>Browser</span>
                                                    <ChevronIcon className="w-2.5 h-2.5" />
                                                    <span>{selectedCategory}</span>
                                                    <ChevronIcon className="w-2.5 h-2.5" />
                                                    <span class="text-shopee">{selectedProduct.name}</span>
                                                </div>
                                                
                                                <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
                                                    <h2 class="text-xl font-extrabold text-white leading-snug max-w-2xl">{parsedProductDetails.title}</h2>
                                                    <div class="flex items-center gap-2 shrink-0">
                                                        <button 
                                                            onClick={() => handleExportProduct(selectedProduct, selectedCategory, markup)}
                                                            class="bg-glassBg hover:bg-white/5 border border-darkBorder text-gray-300 hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                                                        >
                                                            📊 Export
                                                        </button>
                                                        <button 
                                                            onClick={() => triggerCopy(parsedProductDetails.description)}
                                                            class={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 border ${copied ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-shopee border-shopee hover:bg-shopeeHover text-white'}`}
                                                        >
                                                            {copied ? <CheckIcon className="w-3.5 h-3.5" /> : <CopyIcon className="w-3.5 h-3.5" />}
                                                            {copied ? 'Tersalin!' : 'Salin Deskripsi'}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* --- Inspector Navigation Tabs --- */}
                                            <div class="flex items-center gap-6 border-b border-darkBorder/40">
                                                {[
                                                    { id: 'overview', label: 'Ringkasan Harga' },
                                                    { id: 'specs', label: 'Spesifikasi Kategori' },
                                                    { id: 'desc', label: 'Deskripsi Detail' },
                                                    { id: 'vars', label: `Variasi (${parsedProductDetails.variations.length})` },
                                                    { id: 'gallery', label: `Galeri (${parsedProductDetails.images.length})` }
                                                ].map(tab => (
                                                    <button 
                                                        key={tab.id}
                                                        onClick={() => setActiveProdTab(tab.id)}
                                                        class={`pb-3 text-xs font-bold uppercase tracking-wider relative transition-all ${activeProdTab === tab.id ? 'text-shopee' : 'text-gray-500 hover:text-gray-300'}`}
                                                    >
                                                        {tab.label}
                                                        {activeProdTab === tab.id && (
                                                            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-shopee rounded-full"></div>
                                                        )}
                                                    </button>
                                                ))}
                                            </div>

                                            {/* --- Sub-Tab Contents --- */}
                                            <div class="mt-4 min-h-[300px]">
                                                
                                                {/* SUBTAB 1: Overview */}
                                                {activeProdTab === 'overview' && (
                                                    <div class="space-y-6">
                                                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                            {/* Price asli card */}
                                                            <div class="p-6 bg-black/45 border border-darkBorder rounded-2xl flex flex-col justify-between">
                                                                <span class="text-[10px] uppercase font-bold tracking-widest text-gray-500">Harga Asli</span>
                                                                <b class="text-2xl font-extrabold text-white mt-4 block">{parsedProductDetails.originalPrice}</b>
                                                            </div>
                                                            {/* Price markup card */}
                                                            <div class="p-6 bg-black/45 border border-shopee/25 rounded-2xl flex flex-col justify-between relative overflow-hidden">
                                                                <span class="text-[10px] uppercase font-bold tracking-widest text-gray-500">Harga Jual (+{markup}%)</span>
                                                                <b class="text-2xl font-extrabold text-emerald-400 mt-4 block text-glow">
                                                                    {calcPriceVal(parsedProductDetails.originalPrice, markup)}
                                                                </b>
                                                            </div>
                                                        </div>

                                                        {/* Outbound Link Cards */}
                                                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                            {/* Store link card */}
                                                            <div class="p-5 bg-glassBg border border-darkBorder rounded-xl space-y-2">
                                                                <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500 block">Link Toko Penjual</span>
                                                                <a 
                                                                    href={parsedProductDetails.storeLink} 
                                                                    target="_blank" 
                                                                    rel="noopener noreferrer" 
                                                                    class="text-xs font-semibold text-shopee hover:underline flex items-center gap-1 break-all"
                                                                >
                                                                    {parsedProductDetails.storeLink || "-"} <ExternalLinkIcon className="w-3.5 h-3.5 shrink-0" />
                                                                </a>
                                                            </div>
                                                            {/* Product original link card */}
                                                            <div class="p-5 bg-glassBg border border-darkBorder rounded-xl space-y-2">
                                                                <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500 block">Link Produk Asli</span>
                                                                <a 
                                                                    href={parsedProductDetails.productLink} 
                                                                    target="_blank" 
                                                                    rel="noopener noreferrer" 
                                                                    class="text-xs font-semibold text-shopee hover:underline flex items-center gap-1 break-all"
                                                                >
                                                                    {parsedProductDetails.productLink || "-"} <ExternalLinkIcon className="w-3.5 h-3.5 shrink-0" />
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}

                                                {/* SUBTAB 2: Specs */}
                                                {activeProdTab === 'specs' && (
                                                    <div class="overflow-x-auto border border-darkBorder rounded-xl">
                                                        <table class="w-full text-left border-collapse">
                                                            <thead>
                                                                <tr class="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                                                                    <th class="p-4 pl-6">Spesifikasi Kunci</th>
                                                                    <th class="p-4 pr-6">Detail Atribut</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody class="divide-y divide-darkBorder/40 text-xs">
                                                                {parsedProductDetails.specs.length === 0 ? (
                                                                    <tr>
                                                                        <td colSpan="2" class="p-8 text-center text-gray-500 font-medium">Tidak ada spesifikasi produk yang terperinci.</td>
                                                                    </tr>
                                                                ) : (
                                                                    parsedProductDetails.specs.map((spec, i) => (
                                                                        <tr key={i} class="hover:bg-white/[0.01]">
                                                                            <td class="p-4 pl-6 font-bold text-shopee w-1/3">{spec.key}</td>
                                                                            <td class="p-4 pr-6 text-gray-200">{spec.val}</td>
                                                                        </tr>
                                                                    ))
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                )}

                                                {/* SUBTAB 3: Description */}
                                                {activeProdTab === 'desc' && (
                                                    <div class="p-6 bg-black/45 border border-darkBorder rounded-2xl space-y-4">
                                                        <div class="desc-container text-xs text-gray-300 leading-relaxed font-medium whitespace-pre-wrap">
                                                            {parsedProductDetails.description}
                                                        </div>
                                                        {/* Tags list */}
                                                        {parsedProductDetails.tags.length > 0 && (
                                                            <div class="flex flex-wrap gap-2 pt-4 border-t border-darkBorder/40">
                                                                {parsedProductDetails.tags.map(t => (
                                                                    <span key={t} class="text-[10px] px-2.5 py-1 rounded-full bg-white/5 text-gray-400 font-semibold border border-darkBorder">
                                                                        {t}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                                {/* SUBTAB 4: Variations */}
                                                {activeProdTab === 'vars' && (
                                                    <div class="overflow-x-auto border border-darkBorder rounded-xl">
                                                        <table class="w-full text-left border-collapse">
                                                            <thead>
                                                                <tr class="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                                                                    <th class="p-4 pl-6">Gambar</th>
                                                                    <th class="p-4">Nama Variasi</th>
                                                                    <th class="p-4">Harga Asli</th>
                                                                    <th class="p-4 pr-6 text-right">Harga Jual Baru</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody class="divide-y divide-darkBorder/40 text-xs">
                                                                {parsedProductDetails.variations.length === 0 ? (
                                                                    <tr>
                                                                        <td colSpan="4" class="p-8 text-center text-gray-500 font-medium">Tidak ada data variasi dan stok.</td>
                                                                    </tr>
                                                                ) : (
                                                                    parsedProductDetails.variations.map((v, i) => (
                                                                        <tr key={i} class="hover:bg-white/[0.01]">
                                                                            <td class="p-4 pl-6">
                                                                                {v.imgUrl ? (
                                                                                    <img 
                                                                                        src={v.imgUrl} 
                                                                                        alt={v.name}
                                                                                        onClick={() => setLightboxImg(v.imgUrl)}
                                                                                        class="w-12 h-12 object-cover rounded-lg border border-darkBorder cursor-zoom-in hover:scale-105 transition-transform duration-200" 
                                                                                    />
                                                                                ) : (
                                                                                    <div class="w-12 h-12 rounded-lg bg-glassBg border border-dashed border-darkBorder flex items-center justify-center opacity-40 text-lg">📦</div>
                                                                                )}
                                                                            </td>
                                                                            <td class="p-4 font-bold text-gray-100">{v.name}</td>
                                                                            <td class="p-4 text-gray-400 line-through text-[11px]">{v.price}</td>
                                                                            <td class="p-4 pr-6 text-right font-extrabold text-emerald-400">{calcPriceVal(v.price, markup)}</td>
                                                                        </tr>
                                                                    ))
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                )}

                                                {/* SUBTAB 5: Gallery */}
                                                {activeProdTab === 'gallery' && (
                                                    <div>
                                                        {parsedProductDetails.images.length === 0 ? (
                                                            <div class="p-12 text-center text-gray-500 font-medium border border-darkBorder border-dashed rounded-2xl">Tidak ada gambar untuk produk ini.</div>
                                                        ) : (
                                                            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                                                {parsedProductDetails.images.map((src, i) => (
                                                                    <div key={i} class="aspect-square rounded-2xl overflow-hidden border border-darkBorder bg-glassBg relative group">
                                                                        <img 
                                                                            src={src} 
                                                                            alt={`Produk ${i+1}`}
                                                                            onClick={() => setLightboxImg(src)}
                                                                            class="w-full h-full object-cover cursor-zoom-in group-hover:scale-105 transition-transform duration-300"
                                                                        />
                                                                        <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs font-bold tracking-wider pointer-events-none transition-opacity duration-200">🔍 ZOOM</div>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                            </div>

                                        </div>
                                    )}

                                </div>

                            </div>
                        )}

                        {/* =========================================================================
                            TAB 3: 📊 DATABASE TARGET LINKS VIEW
                            ========================================================================= */}
                        {activeTab === 'database' && (
                            <div class="space-y-8 animate-[fadeIn_0.2s_ease-out]">
                                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                    <div>
                                        <h2 class="text-2xl font-extrabold text-white">Database Target Crawling</h2>
                                        <p class="text-sm text-gray-400 mt-1">Mengelola dan meninjau seluruh target link scraping dari file database shopee_links.csv.</p>
                                    </div>
                                    <button 
                                        onClick={() => {
                                            const headers = ["Kategori", "Keyword", "Lokasi", "Link Produk", "Rating", "Status Chat", "Status", "Toko"];
                                            const rows = filteredDbData.map(r => [r.category, r.keyword, r.location, r.link, r.rating, r.chat_status, r.status, r.shop]);
                                            downloadCSV([headers, ...rows], "Database_Target_Shopee.csv");
                                        }}
                                        class="bg-shopee hover:bg-shopeeHover border border-shopee text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 self-start shrink-0"
                                    >
                                        💾 Download Filtered CSV
                                    </button>
                                </div>

                                {/* --- Interactive Database Filtering Panel --- */}
                                <div class="glass-card rounded-2xl p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                    {/* Search input */}
                                    <div class="space-y-1.5">
                                        <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500">Cari Database</span>
                                        <div class="relative flex items-center">
                                            <input 
                                                type="text" 
                                                placeholder="Toko, link, keyword..." 
                                                value={dbSearch}
                                                onChange={(e) => { setDbSearch(e.target.value); setDbPage(1); }}
                                                class="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee focus:ring-1 focus:ring-shopee/25 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white outline-none transition-all"
                                            />
                                            <div class="absolute left-3 text-gray-500"><SearchIcon className="w-3.5 h-3.5" /></div>
                                        </div>
                                    </div>

                                    {/* Category Filter */}
                                    <div class="space-y-1.5">
                                        <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500">Filter Kategori</span>
                                        <select 
                                            value={dbCatFilter}
                                            onChange={(e) => { setDbCatFilter(e.target.value); setDbPage(1); }}
                                            class="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                                        >
                                            <option value="">Semua Kategori</option>
                                            {dbCategories.map(cat => (
                                                <option key={cat} value={cat}>{cat}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Scrape Status Filter */}
                                    <div class="space-y-1.5">
                                        <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500">Status Scrape</span>
                                        <select 
                                            value={dbStatusFilter}
                                            onChange={(e) => { setDbStatusFilter(e.target.value); setDbPage(1); }}
                                            class="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                                        >
                                            <option value="">Semua Status Scrape</option>
                                            <option value="Done">Selesai (Done)</option>
                                            <option value="Pending">Pending / Kosong</option>
                                        </select>
                                    </div>

                                    {/* Chat Status Filter */}
                                    <div class="space-y-1.5">
                                        <span class="text-[10px] uppercase font-bold tracking-wider text-gray-500">Status Chat Broadcast</span>
                                        <select 
                                            value={dbChatFilter}
                                            onChange={(e) => { setDbChatFilter(e.target.value); setDbPage(1); }}
                                            class="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                                        >
                                            <option value="">Semua Status Chat</option>
                                            <option value="Sent">Terkirim (Sent)</option>
                                            <option value="Skip">Lewati (Skip)</option>
                                            <option value="Failed">Gagal (Failed)</option>
                                            <option value="Pending">Belum Dikirim</option>
                                        </select>
                                    </div>
                                </div>

                                {/* --- Spreadsheet Grid Datatable --- */}
                                <div class="glass-card rounded-3xl overflow-hidden flex flex-col">
                                    <div class="overflow-x-auto">
                                        <table class="w-full text-left border-collapse text-xs">
                                            <thead>
                                                <tr class="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                                                    <th class="p-4 pl-6 text-center w-12">#</th>
                                                    <th class="p-4">Nama Toko</th>
                                                    <th class="p-4">Kategori</th>
                                                    <th class="p-4">Keyword</th>
                                                    <th class="p-4">Link Shopee</th>
                                                    <th class="p-4 text-center">Rating</th>
                                                    <th class="p-4 text-center">Scrape</th>
                                                    <th class="p-4 pr-6 text-center">Chat Broadcast</th>
                                                </tr>
                                            </thead>
                                            <tbody class="divide-y divide-darkBorder/40">
                                                {paginatedDbData.length === 0 ? (
                                                    <tr>
                                                        <td colSpan="8" class="p-12 text-center text-gray-500 font-medium">Tidak ada target database yang cocok dengan kriteria filter.</td>
                                                    </tr>
                                                ) : (
                                                    paginatedDbData.map((row, idx) => {
                                                        const globalIdx = (dbPage - 1) * pageSize + idx + 1;
                                                        
                                                        // Render badges status scrape
                                                        const isDone = row.status === "Done" || row.status === "Sent";
                                                        const scrapeBadge = isDone 
                                                            ? <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">Done</span>
                                                            : <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400">Pending</span>;

                                                        // Render badges status chat
                                                        let chatBadge = <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-500/10 border border-slate-500/20 text-gray-400">-</span>;
                                                        if (row.chat_status === "Sent") {
                                                            chatBadge = <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">Sent</span>;
                                                        } else if (row.chat_status && row.chat_status.includes("Skip")) {
                                                            chatBadge = <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400">Skip</span>;
                                                        } else if (row.chat_status === "Failed") {
                                                            chatBadge = <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 border border-rose-500/30 text-rose-400">Failed</span>;
                                                        }

                                                        return (
                                                            <tr key={globalIdx} class="hover:bg-white/[0.01]">
                                                                <td class="p-4 pl-6 text-center text-gray-500 font-bold">{globalIdx}</td>
                                                                <td class="p-4 font-bold text-white max-w-[150px] truncate">{row.shop && row.shop !== "nan" ? row.shop : "Toko Tidak Diketahui"}</td>
                                                                <td class="p-4 text-gray-400 font-medium">{row.category || "-"}</td>
                                                                <td class="p-4 text-gray-400 font-medium">{row.keyword || "-"}</td>
                                                                <td class="p-4 max-w-[250px] truncate">
                                                                    <a href={row.link} target="_blank" rel="noopener noreferrer" class="text-shopee hover:underline font-semibold flex items-center gap-1 truncate">
                                                                        {row.link} <ExternalLinkIcon className="w-3 h-3 shrink-0" />
                                                                    </a>
                                                                </td>
                                                                <td class="p-4 text-center">
                                                                    <div class="flex items-center justify-center gap-1 text-amber-400 font-bold">
                                                                        <StarIcon className="w-3.5 h-3.5" />
                                                                        <span>{row.rating || "-"}</span>
                                                                    </div>
                                                                </td>
                                                                <td class="p-4 text-center">{scrapeBadge}</td>
                                                                <td class="p-4 pr-6 text-center">{chatBadge}</td>
                                                            </tr>
                                                        );
                                                    })
                                                )}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* --- Spreadsheet Pagination Panel --- */}
                                    {totalPages > 1 && (
                                        <div class="px-6 py-4 border-t border-darkBorder flex items-center justify-between gap-4 text-xs font-semibold text-gray-400 bg-black/15">
                                            <span>
                                                Menampilkan <span class="text-white">{(dbPage - 1) * pageSize + 1}</span> hingga <span class="text-white">{Math.min(dbPage * pageSize, filteredDbData.length)}</span> dari <span class="text-white">{filteredDbData.length}</span> target
                                            </span>
                                            <div class="flex items-center gap-1.5">
                                                <button 
                                                    disabled={dbPage === 1}
                                                    onClick={() => setDbPage(p => Math.max(1, p - 1))}
                                                    class="px-3 py-1.5 rounded-lg border border-darkBorder text-gray-400 hover:text-white hover:border-gray-600 disabled:opacity-40 disabled:pointer-events-none transition-all flex items-center"
                                                >
                                                    Prev
                                                </button>
                                                
                                                {/* Page numbers */}
                                                {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                                                    // Dynamic pagination window
                                                    let pageNum = i + 1;
                                                    if (dbPage > 3 && totalPages > 5) {
                                                        if (dbPage + 2 > totalPages) {
                                                            pageNum = totalPages - 4 + i;
                                                        } else {
                                                            pageNum = dbPage - 2 + i;
                                                        }
                                                    }
                                                    return (
                                                        <button 
                                                            key={pageNum}
                                                            onClick={() => setDbPage(pageNum)}
                                                            class={`w-8 h-8 rounded-lg font-bold transition-all ${dbPage === pageNum ? 'bg-shopee text-white shadow shadow-shopee/20' : 'hover:bg-white/5 text-gray-400'}`}
                                                        >
                                                            {pageNum}
                                                        </button>
                                                    );
                                                })}

                                                <button 
                                                    disabled={dbPage === totalPages}
                                                    onClick={() => setDbPage(p => Math.min(totalPages, p + 1))}
                                                    class="px-3 py-1.5 rounded-lg border border-darkBorder text-gray-400 hover:text-white hover:border-gray-600 disabled:opacity-40 disabled:pointer-events-none transition-all flex items-center"
                                                >
                                                    Next
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                    </main>

                    {/* --- Bottom Footer Info --- */}
                    <footer class="py-6 border-t border-darkBorder text-center text-xs text-gray-600 font-semibold bg-darkCard/30 mt-8">
                        ⚡ ShopeeBot Dashboard Console © {new Date().getFullYear()} — Made for Premium Dropship Management
                    </footer>

                    {/* =========================================================================
                        POPUP LIGHTBOX ELEMENT MODAL
                        ========================================================================= */}
                    {lightboxImg && (
                        <div 
                            onClick={() => setLightboxImg(null)}
                            class="fixed inset-0 bg-black/95 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-[fadeIn_0.15s_ease-out]"
                        >
                            <span 
                                onClick={() => setLightboxImg(null)}
                                class="absolute top-6 right-8 text-gray-400 hover:text-white text-3xl cursor-pointer w-12 h-12 flex items-center justify-center rounded-full bg-white/5 border border-white/10 hover:bg-shopee/20 hover:border-shopee hover:rotate-90 transition-all duration-300"
                            >
                                &times;
                            </span>
                            <img 
                                src={lightboxImg} 
                                alt="Zoomed view"
                                onClick={(e) => e.stopPropagation()}
                                class="max-w-full max-h-[90vh] object-contain rounded-2xl border border-darkBorder shadow-2xl scale-95 animate-[zoomIn_0.2s_cubic-bezier(0.34,1.56,0.64,1)_forwards]"
                            />
                        </div>
                    )}

                </div>
            );
        }

        // Render React components in React 18 syntax
        const container = document.getElementById('root');
        const root = ReactDOM.createRoot(container);
        root.render(<App />);
    </script>
</body>
</html>
"""

def generate_site():
    print("🌐 Memulai pembuatan website preview...")
    
    hasil_md_dir = "hasil_md"
    if not os.path.exists(hasil_md_dir):
        print(f"❌ Folder '{hasil_md_dir}' tidak ditemukan. Silakan jalankan scraper terlebih dahulu.")
        return

    # 1. Scan Markdown Data
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

    # 2. Scan CSV Database
    db_data = []
    csv_file = "shopee_links.csv"
    if os.path.exists(csv_file):
        try:
            with open(csv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db_data.append({
                        "category": row.get("Kategori", ""),
                        "keyword": row.get("Keyword", ""),
                        "location": row.get("Lokasi", ""),
                        "link": row.get("Link Produk", ""),
                        "rating": row.get("Rating", ""),
                        "chat_status": row.get("Status Chat", ""),
                        "status": row.get("Status", ""),
                        "shop": row.get("Toko", "")
                    })
        except Exception as e:
            print(f"⚠️ Gagal membaca {csv_file} database: {e}")
    else:
        print(f"⚠️ File database '{csv_file}' tidak ditemukan.")

    # 3. Replace Placeholders with JSON dumps
    json_data = json.dumps(data)
    json_db_data = json.dumps(db_data)

    final_html = HTML_CONTENT.replace("/*__APP_DATA_PLACEHOLDER__*/", json_data).replace("/*__DB_DATA_PLACEHOLDER__*/", json_db_data)

    # 4. Write Output HTML Preview
    output_file = "preview.html"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"✅ Website preview Berhasil diperbarui: {output_file}")
        
        file_url = "file://" + os.path.abspath(output_file)
        if "--no-open" not in sys.argv:
            webbrowser.open(file_url)
    except Exception as e:
        print(f"❌ Gagal menulis website preview: {e}")

if __name__ == "__main__":
    generate_site()
