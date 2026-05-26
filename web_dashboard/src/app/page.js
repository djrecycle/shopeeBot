'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { 
  Search, ShoppingBag, Folder, Star, ArrowUpRight, 
  Copy, Check, LogIn, ExternalLink, X, Tag
} from 'lucide-react';

// Price helpers
const stripHtml = (html) => {
  if (!html) return '';
  let text = String(html).replace(/<[^>]*>?/gm, '');
  text = text.replace(/^Harga Upload:\s*/i, '');
  return text.trim();
};

const formatRp = (n) => {
  return "Rp" + Math.ceil(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
};

const parseRp = (s) => {
  if (!s) return 0;
  return parseInt(s.replace(/[^0-9]/g, "")) || 0;
};

const calcPriceVal = (priceStr, markupPct) => {
  if (!priceStr) return "Rp0";
  const cleanStr = stripHtml(priceStr);
  if (cleanStr.includes("-")) {
    let parts = cleanStr.split("-");
    let m1 = parseRp(parts[0]) * (1 + markupPct / 100);
    let m2 = parseRp(parts[1]) * (1 + markupPct / 100);
    return formatRp(m1) + " - " + formatRp(m2);
  }
  return formatRp(parseRp(cleanStr) * (1 + markupPct / 100));
};

export default function PublicPage() {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Search & Categories filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [markup, setMarkup] = useState(20);
  const [isAdmin, setIsAdmin] = useState(false);
  
  // Modals & Details
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview | specs | variations
  const [lightboxImg, setLightboxImg] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const prodRes = await fetch('/api/products');
        const prodData = await prodRes.json();
        setProducts(prodData);
        
        const statsRes = await fetch('/api/stats');
        const statsData = await statsRes.json();
        setStats(statsData);
      } catch (err) {
        console.error('Error fetching public data:', err);
      } finally {
        setLoading(false);
      }
    }
    
    async function checkAuth() {
      try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (res.ok && data.authenticated) {
          setIsAdmin(true);
        }
      } catch (err) {}
    }
    
    fetchData();
    checkAuth();
  }, []);

  // Filter products locally for instantaneous user interaction!
  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const matchesSearch = 
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCat = !selectedCategory || p.category === selectedCategory;
      return matchesSearch && matchesCat;
    });
  }, [products, searchQuery, selectedCategory]);

  const categories = useMemo(() => {
    const cats = products.map(p => p.category).filter(Boolean);
    return [...new Set(cats)].sort();
  }, [products]);

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="min-h-screen bg-[#0A0A0C] flex flex-col">
      {/* Top Navigation */}
      <header className="h-20 bg-darkCard/90 backdrop-blur-md border-b border-darkBorder flex items-center justify-between px-8 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 shopee-gradient rounded-xl flex items-center justify-center shadow-lg shadow-shopee/20 font-bold text-lg">🛒</div>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight text-white">ShopeeBot <span className="text-shopee text-glow">PRO</span></h1>
            <p className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">Premium Web Catalog</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isAdmin ? (
            <Link href="/admin" className="bg-shopee/10 hover:bg-shopee/20 border border-shopee/30 hover:border-shopee/60 text-shopee hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5">
              <LogIn className="w-3.5 h-3.5" /> Dashboard Admin
            </Link>
          ) : (
            <Link href="/login" className="bg-glassBg hover:bg-shopee/10 border border-darkBorder hover:border-shopee/30 text-gray-300 hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5">
              <LogIn className="w-3.5 h-3.5" /> Login
            </Link>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-16 px-8 border-b border-darkBorder bg-gradient-to-b from-darkCard/30 to-transparent">
        <div className="max-w-6xl mx-auto text-center space-y-6">
          <span className="px-3 py-1 rounded-full bg-shopee/10 border border-shopee/30 text-shopee text-[10px] font-bold uppercase tracking-widest">
            Katalog Premium Dropship
          </span>
          <h2 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Cari & Review Produk Terlaris Shopee
          </h2>
          <p className="text-sm text-gray-400 max-w-xl mx-auto leading-relaxed">
            Temukan barang impian dengan deskripsi lengkap, variasi harga ter-update, dan kalkulasi profit instan untuk bisnis dropship Anda.
          </p>
        </div>
      </section>

      {/* Main Catalog View */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Filters Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Price Markup Slider (Admin Only) */}
          {isAdmin && (
            <div className="glass-card rounded-2xl p-5 space-y-4 animate-fade-in border border-shopee/30">
              <div className="flex items-center justify-between text-xs uppercase font-bold tracking-wider text-gray-400">
                <span>Markup Harga Jual</span>
                <span className="text-shopee text-sm font-extrabold">+{markup}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={markup}
                onChange={(e) => setMarkup(parseInt(e.target.value))}
                className="w-full accent-shopee h-1.5 bg-black/50 rounded-lg cursor-pointer"
              />
              {/* Slider Presets */}
              <div className="grid grid-cols-3 gap-1.5">
                {[0, 15, 30, 50, 75, 100].map(pct => (
                  <button 
                    key={pct}
                    onClick={() => setMarkup(pct)}
                    className={`py-1 rounded text-[10px] font-bold border transition-all ${markup === pct ? 'border-shopee bg-shopee/10 text-shopee' : 'border-darkBorder text-gray-500 hover:text-white hover:border-gray-600 bg-white/[0.01]'}`}
                  >
                    +{pct}%
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Categories list */}
          <div className="glass-card rounded-2xl p-5 space-y-4">
            <h3 className="text-xs uppercase font-bold tracking-wider text-gray-400 flex items-center gap-1.5">
              <Folder className="w-3.5 h-3.5" /> Kategori Produk
            </h3>
            <div className="space-y-1 max-h-[400px] overflow-y-auto pr-1">
              <button 
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-between ${!selectedCategory ? 'bg-shopee/10 text-shopee border border-shopee/20' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
              >
                <span>Semua Kategori</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">{products.length}</span>
              </button>
              
              {categories.map(cat => {
                const count = products.filter(p => p.category === cat).length;
                return (
                  <button 
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-between ${selectedCategory === cat ? 'bg-shopee/10 text-shopee border border-shopee/20' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
                  >
                    <span className="truncate">{cat}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">{count}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Catalog Grid */}
        <div className="lg:col-span-3 space-y-6">
          {/* Search Bar */}
          <div className="relative flex items-center">
            <input 
              type="text" 
              placeholder="Cari nama produk atau deskripsi di katalog..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-darkCard/50 border border-darkBorder hover:border-gray-700 focus:border-shopee focus:ring-1 focus:ring-shopee/25 rounded-2xl pl-12 pr-4 py-3.5 text-sm text-white outline-none transition-all"
            />
            <div className="absolute left-4.5 text-gray-500"><Search className="w-5 h-5 ml-1" /></div>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center p-20 space-y-4">
              <div className="w-12 h-12 rounded-full border-2 border-shopee/20 border-t-shopee animate-spin"></div>
              <p className="text-xs text-gray-500">Memuat katalog premium...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="glass-card rounded-3xl p-16 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-glassBg flex items-center justify-center text-gray-500 border border-darkBorder mx-auto">
                <ShoppingBag className="w-8 h-8" />
              </div>
              <h4 className="text-lg font-bold text-white">Produk Tidak Ditemukan</h4>
              <p className="text-xs text-gray-400 max-w-sm mx-auto leading-relaxed">
                Maaf, tidak ada produk di katalog yang cocok dengan kata kunci atau kategori yang Anda pilih saat ini.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map(p => {
                const coverImg = p.images && p.images[0] ? p.images[0] : 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop';
                const hasSpecs = p.specs && p.specs.length > 0;
                const merk = hasSpecs ? p.specs.find(s => s.key.toLowerCase() === 'merek')?.val : null;
                
                return (
                  <div 
                    key={p.id}
                    onClick={() => { setSelectedProduct(p); setActiveTab('overview'); }}
                    className="glass-card rounded-2xl overflow-hidden flex flex-col group hover:border-shopee/40 cursor-pointer transition-all duration-300 hover:-translate-y-1.5"
                  >
                    {/* Cover image wrapper */}
                    <div className="aspect-[4/3] relative overflow-hidden bg-black/40 border-b border-darkBorder">
                      <img 
                        src={coverImg} 
                        alt={p.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop'; }}
                      />
                      <span className="absolute top-3 left-3 px-2 py-0.5 rounded bg-black/60 border border-white/10 text-[9px] font-bold text-gray-300">
                        {p.category}
                      </span>
                    </div>

                    {/* Card details */}
                    <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                      <div className="space-y-1">
                        {merk && <span className="text-[9px] uppercase tracking-widest text-shopee font-bold">{merk}</span>}
                        <h4 className="text-sm font-bold text-white line-clamp-2 leading-snug group-hover:text-shopee transition-colors">
                          {p.name}
                        </h4>
                      </div>
                      
                      <div className="pt-2 border-t border-darkBorder/40 flex items-center justify-between">
                        <div>
                          <span className="text-[9px] text-gray-500 font-semibold block uppercase">Harga Jual (+{markup}%)</span>
                          <b className="text-sm font-extrabold text-white text-glow">
                            {calcPriceVal(p.original_price, markup)}
                          </b>
                        </div>
                        <div className="w-8 h-8 rounded-lg bg-shopee/10 border border-shopee/20 flex items-center justify-center text-shopee opacity-80 group-hover:opacity-100 group-hover:bg-shopee group-hover:text-white transition-all">
                          <ArrowUpRight className="w-4 h-4" />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="w-full max-w-4xl bg-darkCard border border-darkBorder rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh]">
            
            {/* Close Button */}
            <button 
              onClick={() => setSelectedProduct(null)}
              className="absolute top-6 right-6 text-gray-400 hover:text-white bg-white/5 hover:bg-shopee/20 border border-white/10 hover:border-shopee w-10 h-10 flex items-center justify-center rounded-full hover:rotate-90 transition-all z-10"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Left Media Column */}
            <div className="w-full md:w-5/12 bg-black/50 border-r border-darkBorder flex flex-col">
              <div className="flex-1 min-h-[300px] relative flex items-center justify-center p-6 bg-black/40">
                <img 
                  src={selectedProduct.images[0]} 
                  alt={selectedProduct.name}
                  onClick={() => setLightboxImg(selectedProduct.images[0])}
                  className="max-h-[350px] object-contain rounded-xl cursor-zoom-in hover:scale-102 transition-transform shadow-lg"
                  onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop'; }}
                />
              </div>
              
              {/* Media Thumbnails list */}
              {selectedProduct.images.length > 1 && (
                <div className="p-4 border-t border-darkBorder bg-black/20 overflow-x-auto flex gap-2">
                  {selectedProduct.images.map((img, idx) => (
                    <img 
                      key={idx}
                      src={img}
                      alt="Thumbnail"
                      onClick={() => setLightboxImg(img)}
                      className="w-12 h-12 object-cover rounded-lg border border-darkBorder hover:border-shopee cursor-zoom-in shrink-0 bg-darkCard transition-all"
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Right Information Column */}
            <div className="w-full md:w-7/12 p-8 flex flex-col justify-between overflow-y-auto">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-bold text-gray-400 uppercase">
                    {selectedProduct.category}
                  </span>
                </div>
                
                <h3 className="text-xl font-extrabold text-white leading-tight mb-4">
                  {selectedProduct.name}
                </h3>
                
                {/* Markup Pricing Cards */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="p-4 bg-black/40 border border-darkBorder rounded-2xl">
                    <span className="text-[9px] uppercase tracking-wider text-gray-500 font-bold block">Harga Asli (Shopee)</span>
                    <b className="text-base text-gray-300 font-extrabold">{stripHtml(selectedProduct.original_price)}</b>
                  </div>
                  <div className="p-4 shopee-gradient/10 border border-shopee/30 rounded-2xl">
                    <span className="text-[9px] uppercase tracking-wider text-shopee font-bold block">Harga Jual (+{markup}%)</span>
                    <b className="text-lg text-shopee font-extrabold text-glow">{calcPriceVal(selectedProduct.original_price, markup)}</b>
                  </div>
                </div>

                {/* Tabs selection */}
                <div className="flex gap-2 border-b border-darkBorder/60 pb-2 mb-4">
                  {[
                    { id: 'overview', label: 'Deskripsi' },
                    { id: 'specs', label: 'Spesifikasi' },
                    { id: 'variations', label: 'Variasi' }
                  ].map(t => (
                    <button 
                      key={t.id}
                      onClick={() => setActiveTab(t.id)}
                      className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === t.id ? 'bg-shopee/10 border border-shopee/25 text-shopee' : 'text-gray-400 hover:text-white'}`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {/* Tab contents */}
                <div className="max-h-[220px] overflow-y-auto text-xs text-gray-300 leading-relaxed pr-2">
                  {activeTab === 'overview' && (
                    <div className="space-y-4">
                      <p className="whitespace-pre-line">{selectedProduct.description || 'Tidak ada deskripsi produk.'}</p>
                      {selectedProduct.tags && selectedProduct.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-2">
                          {selectedProduct.tags.map(t => (
                            <span key={t} className="px-2 py-0.5 rounded bg-white/5 border border-darkBorder text-[9px] font-semibold text-gray-400 flex items-center gap-1">
                              <Tag className="w-2.5 h-2.5 text-shopee" /> {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'specs' && (
                    <div className="space-y-2">
                      {selectedProduct.specs.length === 0 ? (
                        <p className="text-gray-500 italic">Tidak ada spesifikasi khusus.</p>
                      ) : (
                        <div className="border border-darkBorder/40 rounded-xl overflow-hidden">
                          {selectedProduct.specs.map((s, idx) => (
                            <div key={idx} className={`grid grid-cols-3 p-2.5 text-[11px] border-b border-darkBorder/30 last:border-0 ${idx % 2 === 0 ? 'bg-black/25' : ''}`}>
                              <span className="col-span-1 font-bold text-gray-400">{s.key}</span>
                              <span className="col-span-2 text-white font-medium">{s.val}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'variations' && (
                    <div className="space-y-2">
                      {selectedProduct.variations.length === 0 ? (
                        <p className="text-gray-500 italic">Tidak ada variasi produk.</p>
                      ) : (
                        <div className="space-y-2">
                          {selectedProduct.variations.map((v, idx) => (
                            <div key={idx} className="p-3 bg-black/30 border border-darkBorder/30 hover:border-shopee/20 rounded-xl flex items-center justify-between transition-colors">
                              <div className="flex items-center gap-2">
                                {v.imgUrl && (
                                  <img 
                                    src={v.imgUrl} 
                                    alt="Variation Thumbnail" 
                                    onClick={() => setLightboxImg(v.imgUrl)}
                                    className="w-10 h-10 object-cover rounded border border-darkBorder cursor-zoom-in shrink-0 bg-darkCard" 
                                  />
                                )}
                                <span className="font-bold text-white text-[11px]">{v.name}</span>
                              </div>
                              <div className="text-right">
                                <span className="text-[9px] text-gray-500 block uppercase">Harga Jual (+{markup}%)</span>
                                <b className="text-shopee font-extrabold text-[11px]">{calcPriceVal(v.price, markup)}</b>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons Footer */}
              <div className="pt-6 border-t border-darkBorder/60 flex items-center gap-3">
                <button 
                  onClick={() => handleCopy(selectedProduct.description)}
                  className="flex-1 bg-glassBg hover:bg-white/5 border border-darkBorder hover:border-gray-600 text-white py-3 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-emerald-400" /> Tersalin!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" /> Salin Deskripsi
                    </>
                  )}
                </button>
                
                <a 
                  href={selectedProduct.product_link} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="flex-1 shopee-gradient hover:bg-shopeeHover text-white py-3 rounded-xl font-bold text-xs shadow-lg shadow-shopee/15 transition-all flex items-center justify-center gap-1.5"
                >
                  <ExternalLink className="w-4 h-4" /> Buka di Shopee
                </a>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Lightbox Zoom Modal */}
      {lightboxImg && (
        <div 
          onClick={() => setLightboxImg(null)}
          className="fixed inset-0 bg-black/95 backdrop-blur-md z-50 flex items-center justify-center p-4"
        >
          <span 
            onClick={() => setLightboxImg(null)}
            className="absolute top-6 right-8 text-gray-400 hover:text-white text-3xl cursor-pointer w-12 h-12 flex items-center justify-center rounded-full bg-white/5 border border-white/10 hover:bg-shopee/20 hover:border-shopee transition-all"
          >
            &times;
          </span>
          <img 
            src={lightboxImg} 
            alt="Zoomed view"
            onClick={(e) => e.stopPropagation()}
            className="max-w-full max-h-[90vh] object-contain rounded-2xl border border-darkBorder shadow-2xl"
          />
        </div>
      )}

      {/* Footer Info */}
      <footer className="py-8 border-t border-darkBorder text-center text-xs text-gray-600 font-semibold bg-darkCard/30 mt-12">
        ⚡ ShopeeBot Professional Web Catalog © {new Date().getFullYear()} — Premium Dropship Management
      </footer>
    </div>
  );
}
