'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ShoppingBag, Folder, Check, LogOut, ArrowLeft, 
  Trash2, Edit, Save, Database, Activity, 
  Star, ExternalLink, RefreshCw, Search, X, Loader2
} from 'lucide-react';

export default function AdminPage() {
  const router = useRouter();
  const [authLoading, setAuthLoading] = useState(true);
  const [username, setUsername] = useState('');
  
  // Data State
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('stats'); // stats | catalog | links
  
  // Link View Filters
  const [linkSearch, setLinkSearch] = useState('');
  const [linkCatFilter, setLinkCatFilter] = useState('');
  const [linkStatusFilter, setLinkStatusFilter] = useState('');
  const [linkChatFilter, setLinkChatFilter] = useState('');
  const [linkPage, setLinkPage] = useState(1);
  const linksPageSize = 10;
  
  // Product Editor Modal
  const [editingProduct, setEditingProduct] = useState(null);
  const [savingProduct, setSavingProduct] = useState(false);
  
  // Checking Autentikasi
  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (res.ok && data.authenticated) {
          setUsername(data.username);
          setAuthLoading(false);
        } else {
          router.push('/login');
        }
      } catch (err) {
        router.push('/login');
      }
    }
    checkAuth();
  }, []);

  // Fetch Admin Data
  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Stats
      const statsRes = await fetch('/api/stats');
      const statsData = await statsRes.json();
      setStats(statsData);
      
      // 2. Products
      const prodRes = await fetch('/api/products');
      const prodData = await prodRes.json();
      setProducts(prodData);
      
      // 3. Links
      const linksRes = await fetch('/api/links');
      const linksData = await linksRes.json();
      setLinks(linksData);
    } catch (err) {
      console.error('Error fetching admin dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      fetchData();
    }
  }, [authLoading]);

  // Logout Handler
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      router.push('/');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Helper to strip HTML tags and "Harga Upload:" text
  const stripHtml = (html) => {
    if (!html) return '';
    let text = String(html).replace(/<[^>]*>?/gm, '');
    text = text.replace(/^Harga Upload:\s*/i, '');
    return text.trim();
  };

  // Helper to calculate upload price (+20% markup), supports ranges
  const calcUploadPrice = (priceStr) => {
    if (!priceStr) return '—';
    const parseRp = (s) => parseInt(String(s).replace(/[^0-9]/g, '')) || 0;
    const formatRp = (n) => 'Rp' + Math.ceil(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const clean = stripHtml(priceStr);
    if (clean.includes('-')) {
      const parts = clean.split('-');
      return formatRp(parseRp(parts[0]) * 1.2) + ' - ' + formatRp(parseRp(parts[1]) * 1.2);
    }
    const val = parseRp(clean);
    return val > 0 ? formatRp(val * 1.2) : '—';
  };

  // Products CRUD
  const handleEditProductClick = (p) => {
    setEditingProduct({ ...p, original_price: stripHtml(p.original_price) });
  };

  const handleSaveProduct = async () => {
    if (!editingProduct) return;
    setSavingProduct(true);
    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: editingProduct.id,
          name: editingProduct.name,
          original_price: editingProduct.original_price,
          category: editingProduct.category,
          description: editingProduct.description
        })
      });
      if (res.ok) {
        setEditingProduct(null);
        await fetchData(); // Refresh data
      } else {
        alert('Gagal menyimpan produk');
      }
    } catch (err) {
      alert('Terjadi kesalahan koneksi server');
    } finally {
      setSavingProduct(false);
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!confirm('Hapus produk ini secara permanen dari database SQLite?')) return;
    try {
      const res = await fetch(`/api/products?id=${id}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchData();
      } else {
        alert('Gagal menghapus produk');
      }
    } catch (err) {
      alert('Error koneksi server');
    }
  };

  // Scraping Links Administration
  const handleDeleteLink = async (id) => {
    if (!confirm('Hapus baris link ini dari database?')) return;
    try {
      const res = await fetch(`/api/links?id=${id}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchData();
      } else {
        alert('Gagal menghapus link');
      }
    } catch (err) {
      alert('Error koneksi');
    }
  };

  const handleDeleteAllLinks = async () => {
    const confirmation = prompt('Ketik "ya" jika Anda ingin menghapus SEMUA link target database secara permanen:');
    if (confirmation && confirmation.toLowerCase() === 'ya') {
      try {
        const res = await fetch('/api/links?all=true', { method: 'DELETE' });
        if (res.ok) {
          await fetchData();
        } else {
          alert('Gagal menghapus database');
        }
      } catch (err) {
        alert('Error koneksi');
      }
    }
  };

  // Links filter logic
  const filteredLinks = useMemo(() => {
    return links.filter(row => {
      const matchesSearch = 
        (row.shop || '').toLowerCase().includes(linkSearch.toLowerCase()) ||
        (row.link || '').toLowerCase().includes(linkSearch.toLowerCase()) ||
        (row.keyword || '').toLowerCase().includes(linkSearch.toLowerCase());
        
      const matchesCat = !linkCatFilter || row.category === linkCatFilter;
      
      const matchesStatus = !linkStatusFilter ||
        (linkStatusFilter === 'Done' && (row.status === 'Done' || row.status === 'Sent')) ||
        (linkStatusFilter === 'Pending' && row.status !== 'Done' && row.status !== 'Sent');
        
      const matchesChat = !linkChatFilter ||
        (linkChatFilter === 'Sent' && row.chat_status === 'Sent') ||
        (linkChatFilter === 'Skip' && row.chat_status && row.chat_status.includes('Skip')) ||
        (linkChatFilter === 'Failed' && row.chat_status === 'Failed') ||
        (linkChatFilter === 'Pending' && (!row.chat_status || row.chat_status === 'nan' || row.chat_status === '-'));

      return matchesSearch && matchesCat && matchesStatus && matchesChat;
    });
  }, [links, linkSearch, linkCatFilter, linkStatusFilter, linkChatFilter]);

  const uniqueLinkCategories = useMemo(() => {
    const cats = links.map(l => l.category).filter(Boolean);
    return [...new Set(cats)].sort();
  }, [links]);

  // Pagination calculations
  const totalPages = Math.ceil(filteredLinks.length / linksPageSize);
  const paginatedLinks = useMemo(() => {
    const start = (linkPage - 1) * linksPageSize;
    return filteredLinks.slice(start, start + linksPageSize);
  }, [filteredLinks, linkPage]);

  // Loading Screen
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0A0A0C] flex flex-col justify-center items-center gap-4">
        <Loader2 className="w-10 h-10 text-shopee animate-spin" />
        <p className="text-xs text-gray-500 font-bold uppercase tracking-widest">Memverifikasi Sesi Admin...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0C] flex flex-col">
      {/* Top Header Dashboard */}
      <header className="h-20 bg-darkCard/90 backdrop-blur-md border-b border-darkBorder flex items-center justify-between px-8 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-gray-400 hover:text-white mr-2 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="w-9 h-9 shopee-gradient rounded-lg flex items-center justify-center font-bold text-base shadow-md shadow-shopee/10">🤖</div>
          <div>
            <h1 className="text-md font-extrabold text-white tracking-tight">ShopeeBot <span className="text-shopee text-glow">PRO</span></h1>
            <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">Dashboard Panel Admin</p>
          </div>
        </div>

        {/* Tab Menus */}
        <div className="flex bg-black/40 border border-darkBorder rounded-xl p-1">
          {[
            { id: 'stats', label: 'Overview', icon: Activity },
            { id: 'catalog', label: 'Katalog Manager', icon: ShoppingBag },
            { id: 'links', label: 'Database Links', icon: Database }
          ].map(t => {
            const Icon = t.icon;
            return (
              <button 
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`px-4 py-2 rounded-lg font-semibold text-xs transition-all flex items-center gap-1.5 ${activeTab === t.id ? 'bg-shopee text-white shadow-md shadow-shopee/15' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              >
                <Icon className="w-3.5 h-3.5" /> {t.label}
              </button>
            );
          })}
        </div>

        {/* Logged user */}
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-400 font-semibold">Logged as: <b className="text-white font-bold">{username}</b></span>
          <button 
            onClick={handleLogout}
            className="bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-400 hover:text-rose-300 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1"
          >
            <LogOut className="w-3.5 h-3.5" /> Logout
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-8 space-y-8">
        
        {loading ? (
          <div className="flex flex-col items-center justify-center p-36 space-y-4">
            <Loader2 className="w-12 h-12 text-shopee animate-spin" />
            <p className="text-xs text-gray-500">Menghubungkan ke database SQLite...</p>
          </div>
        ) : (
          <>
            {/* =========================================================================
                TAB 1: 📊 OVERVIEW & STATS CAMPAIGN
                ========================================================================= */}
            {activeTab === 'stats' && stats && (
              <div className="space-y-8 animate-fade-in">
                {/* Header title */}
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-extrabold text-white">Analitik Real-Time Kampanye</h2>
                    <p className="text-xs text-gray-400 mt-1">Metrik visual real-time langsung yang disinkronkan ke database SQLite.</p>
                  </div>
                  <button 
                    onClick={fetchData}
                    className="p-2 bg-glassBg hover:bg-white/5 border border-darkBorder hover:border-gray-600 rounded-xl transition-all"
                  >
                    <RefreshCw className="w-4 h-4 text-gray-400 hover:text-white" />
                  </button>
                </div>

                {/* Cards widget */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  {/* Total link */}
                  <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[130px]">
                    <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-gray-400">
                      <span>Total DB Link</span>
                      <Database className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-extrabold text-white tracking-tight">{stats.totalTargets}</div>
                      <p className="text-[10px] text-gray-500 mt-0.5">Link tersimpan di database</p>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500"></div>
                  </div>

                  {/* Scraped */}
                  <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[130px]">
                    <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-gray-400">
                      <span>Sukses Crawl</span>
                      <ShoppingBag className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="mt-2">
                      <div className="text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-1.5">
                        {stats.scrapedTargets}
                        <span className="text-xs text-emerald-400 font-semibold">({stats.totalTargets > 0 ? Math.round((stats.scrapedTargets / stats.totalTargets) * 100) : 0}%)</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mt-1.5">
                        <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${stats.totalTargets > 0 ? (stats.scrapedTargets / stats.totalTargets) * 100 : 0}%` }}></div>
                      </div>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
                  </div>

                  {/* Chat Sent */}
                  <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[130px]">
                    <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-gray-400">
                      <span>Broadcast Chat</span>
                      <Check className="w-4 h-4 text-shopee" />
                    </div>
                    <div className="mt-2">
                      <div className="text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-1.5">
                        {stats.chatSentTargets}
                        <span className="text-xs text-shopee font-semibold">({stats.totalTargets > 0 ? Math.round((stats.chatSentTargets / stats.totalTargets) * 100) : 0}%)</span>
                      </div>
                      <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mt-1.5">
                        <div className="bg-shopee h-full rounded-full" style={{ width: `${stats.totalTargets > 0 ? (stats.chatSentTargets / stats.totalTargets) * 100 : 0}%` }}></div>
                      </div>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-shopee"></div>
                  </div>

                  {/* Categories */}
                  <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between min-h-[130px]">
                    <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-gray-400">
                      <span>Kategori Aktif</span>
                      <Folder className="w-4 h-4 text-purple-400" />
                    </div>
                    <div className="mt-3">
                      <div className="text-3xl font-extrabold text-white tracking-tight">{stats.totalCategories}</div>
                      <p className="text-[10px] text-gray-500 mt-0.5">Brand / kategori produk ter-crawled</p>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-purple-500"></div>
                  </div>
                </div>

                {/* Categories Table Detail */}
                <div className="glass-card rounded-2xl p-6 space-y-4">
                  <h3 className="text-sm font-bold text-white">Analisis Kemajuan per Kategori</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                          <th className="p-4 w-12 text-center">#</th>
                          <th className="p-4">Nama Kategori</th>
                          <th className="p-4 text-center">Total Link</th>
                          <th className="p-4 text-center">Produk</th>
                          <th className="p-4 text-center">Scrape Selesai</th>
                          <th className="p-4 text-center">Chat Terkirim</th>
                          <th className="p-4">Kemajuan Crawl</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-darkBorder/40">
                        {stats.categoryStats.length === 0 ? (
                          <tr>
                            <td colSpan="7" className="p-8 text-center text-gray-500">Tidak ada kategori. Silakan jalankan scraper.</td>
                          </tr>
                        ) : (
                          stats.categoryStats.map((c, idx) => {
                            const pct = c.total > 0 ? Math.round((c.scraped / c.total) * 100) : 0;
                            return (
                              <tr key={idx} className="hover:bg-white/[0.01]">
                                <td className="p-4 text-center text-gray-500 font-bold">{idx + 1}</td>
                                <td className="p-4 font-bold text-white">{c.category}</td>
                                <td className="p-4 text-center font-semibold text-gray-300">{c.total || '—'}</td>
                                <td className="p-4 text-center font-bold text-purple-400">{c.productCount || 0}</td>
                                <td className="p-4 text-center font-bold text-emerald-400">{c.scraped || 0}</td>
                                <td className="p-4 text-center font-bold text-shopee">{c.chatSent || 0}</td>
                                <td className="p-4">
                                  {c.total > 0 ? (
                                    <div className="flex items-center gap-3">
                                      <div className="w-24 bg-white/5 h-1.5 rounded-full overflow-hidden shrink-0">
                                        <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                                      </div>
                                      <span className="font-extrabold text-emerald-400">{pct}%</span>
                                    </div>
                                  ) : (
                                    <span className="text-gray-600 text-[10px]">Belum ada link</span>
                                  )}
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}


            {/* =========================================================================
                TAB 2: 🏪 CATALOG MANAGER (CRUD PRODUCTS)
                ========================================================================= */}
            {activeTab === 'catalog' && (
              <div className="space-y-6 animate-fade-in">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-extrabold text-white">Manajer Katalog Produk</h2>
                    <p className="text-xs text-gray-400 mt-1">Ubah harga asli, deskripsi produk, atau hapus item dari katalog publik.</p>
                  </div>
                </div>

                <div className="glass-card rounded-2xl overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                          <th className="p-4 w-12 text-center">#</th>
                          <th className="p-4">Gambar</th>
                          <th className="p-4">Nama Produk</th>
                          <th className="p-4">Kategori</th>
                          <th className="p-4">Harga Asli</th>
                          <th className="p-4">Harga Upload (+20%)</th>
                          <th className="p-4 pr-6 text-center w-32">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-darkBorder/40">
                        {products.length === 0 ? (
                          <tr>
                            <td colSpan="7" className="p-12 text-center text-gray-500">Tidak ada produk dalam katalog. Silakan inisialisasi sync data.</td>
                          </tr>
                        ) : (
                          products.map((p, idx) => (
                            <tr key={p.id} className="hover:bg-white/[0.01]">
                              <td className="p-4 text-center text-gray-500 font-bold">{idx + 1}</td>
                              <td className="p-4">
                                <img 
                                  src={p.images && p.images[0] ? p.images[0] : 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop'} 
                                  alt="Thumb" 
                                  className="w-10 h-10 object-cover rounded border border-darkBorder bg-black"
                                  onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop'; }}
                                />
                              </td>
                              <td className="p-4 font-bold text-white max-w-[280px] truncate" title={p.name}>{p.name}</td>
                              <td className="p-4 text-gray-400 font-medium">{p.category}</td>
                              <td className="p-4 font-bold text-gray-300">{stripHtml(p.original_price)}</td>
                              <td className="p-4 font-bold text-emerald-400">{calcUploadPrice(stripHtml(p.original_price))}</td>
                              <td className="p-4 pr-6 text-center">
                                <div className="flex items-center justify-center gap-2">
                                  <button 
                                    onClick={() => handleEditProductClick(p)}
                                    className="p-2 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 hover:border-blue-500/40 text-blue-400 rounded-lg transition-all"
                                    title="Edit Produk"
                                  >
                                    <Edit className="w-3.5 h-3.5" />
                                  </button>
                                  <button 
                                    onClick={() => handleDeleteProduct(p.id)}
                                    className="p-2 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/40 text-rose-400 rounded-lg transition-all"
                                    title="Hapus Produk"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* =========================================================================
                TAB 3: 🔗 DATABASE LINKS (DATATABLE)
                ========================================================================= */}
            {activeTab === 'links' && (
              <div className="space-y-6 animate-fade-in">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-extrabold text-white">Database Link Scraping</h2>
                    <p className="text-xs text-gray-400 mt-1">Interaksi langsung dengan database SQLite target link Shopee.</p>
                  </div>
                  <button 
                    onClick={handleDeleteAllLinks}
                    className="bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/40 text-rose-400 px-4 py-2 rounded-xl text-xs font-bold transition-all"
                  >
                    ⚠️ Kosongkan Database Link
                  </button>
                </div>

                {/* Filter and Search Bar */}
                <div className="glass-card rounded-2xl p-5 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Search Field */}
                    <div className="relative flex items-center md:col-span-1">
                      <input 
                        type="text" 
                        placeholder="Cari toko, link, keyword..." 
                        value={linkSearch}
                        onChange={(e) => { setLinkSearch(e.target.value); setLinkPage(1); }}
                        className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl pl-9 pr-4 py-2.5 text-xs text-white outline-none transition-all"
                      />
                      <Search className="absolute left-3 text-gray-500 w-3.5 h-3.5" />
                    </div>

                    {/* Category Filter */}
                    <select 
                      value={linkCatFilter}
                      onChange={(e) => { setLinkCatFilter(e.target.value); setLinkPage(1); }}
                      className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                    >
                      <option value="">Semua Kategori</option>
                      {uniqueLinkCategories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>

                    {/* Scrape Status Filter */}
                    <select 
                      value={linkStatusFilter}
                      onChange={(e) => { setLinkStatusFilter(e.target.value); setLinkPage(1); }}
                      className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                    >
                      <option value="">Semua Status Scrape</option>
                      <option value="Done">Selesai (Done)</option>
                      <option value="Pending">Tertunda (Pending)</option>
                    </select>

                    {/* Chat Status Filter */}
                    <select 
                      value={linkChatFilter}
                      onChange={(e) => { setLinkChatFilter(e.target.value); setLinkPage(1); }}
                      className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee rounded-xl px-3 py-2.5 text-xs text-white outline-none transition-all cursor-pointer"
                    >
                      <option value="">Semua Status Chat</option>
                      <option value="Sent">Terkirim (Sent)</option>
                      <option value="Skip">Lewati (Skip)</option>
                      <option value="Failed">Gagal (Failed)</option>
                      <option value="Pending">Belum Dikirim</option>
                    </select>
                  </div>
                </div>

                {/* Links Table */}
                <div className="glass-card rounded-2xl overflow-hidden flex flex-col">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-black/45 border-b border-darkBorder text-[10px] uppercase font-bold text-gray-400">
                          <th className="p-4 w-12 text-center">#</th>
                          <th className="p-4">Nama Toko</th>
                          <th className="p-4">Kategori</th>
                          <th className="p-4">Link Shopee</th>
                          <th className="p-4 text-center w-16">Rating</th>
                          <th className="p-4 text-center w-24">Scrape</th>
                          <th className="p-4 text-center w-24">Chat Status</th>
                          <th className="p-4 pr-6 text-center w-20">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-darkBorder/40">
                        {paginatedLinks.length === 0 ? (
                          <tr>
                            <td colSpan="8" className="p-12 text-center text-gray-500 font-medium">Tidak ada target link yang cocok dengan filter.</td>
                          </tr>
                        ) : (
                          paginatedLinks.map((row, idx) => {
                            const globalIdx = (linkPage - 1) * linksPageSize + idx + 1;
                            const isDone = row.status === 'Done' || row.status === 'Sent';
                            
                            let chatBadge = <span className="px-2 py-0.5 rounded bg-slate-500/10 border border-slate-500/20 text-gray-500 text-[10px] font-bold">-</span>;
                            if (row.chat_status === 'Sent') {
                              chatBadge = <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold">Sent</span>;
                            } else if (row.chat_status && row.chat_status.includes('Skip')) {
                              chatBadge = <span className="px-2 py-0.5 rounded bg-blue-500/10 border border-emerald-500/30 text-blue-400 text-[10px] font-bold">Skip</span>;
                            } else if (row.chat_status === 'Failed') {
                              chatBadge = <span className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[10px] font-bold">Failed</span>;
                            }
                            
                            return (
                              <tr key={row.id} className="hover:bg-white/[0.01]">
                                <td className="p-4 text-center text-gray-500 font-bold">{globalIdx}</td>
                                <td className="p-4 font-bold text-white max-w-[120px] truncate">{row.shop || '-'}</td>
                                <td className="p-4 text-gray-400">{row.category}</td>
                                <td className="p-4 max-w-[200px] truncate">
                                  <a href={row.link} target="_blank" rel="noopener noreferrer" className="text-shopee hover:underline flex items-center gap-1 font-semibold truncate">
                                    {row.link} <ExternalLink className="w-3 h-3 shrink-0" />
                                  </a>
                                </td>
                                <td className="p-4 text-center">
                                  <div className="flex items-center justify-center gap-1 text-amber-400 font-bold">
                                    <Star className="w-3.5 h-3.5 fill-current" />
                                    <span>{row.rating || '-'}</span>
                                  </div>
                                </td>
                                <td className="p-4 text-center">
                                  {isDone ? (
                                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold">Done</span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[10px] font-bold">Pending</span>
                                  )}
                                </td>
                                <td className="p-4 text-center">{chatBadge}</td>
                                <td className="p-4 pr-6 text-center">
                                  <button 
                                    onClick={() => handleDeleteLink(row.id)}
                                    className="p-1.5 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/40 text-rose-400 rounded-lg transition-all"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination control */}
                  {totalPages > 1 && (
                    <div className="px-6 py-4 border-t border-darkBorder/40 flex items-center justify-between text-xs font-semibold text-gray-400 bg-black/15">
                      <span>Menampilkan {(linkPage - 1) * linksPageSize + 1} hingga {Math.min(linkPage * linksPageSize, filteredLinks.length)} dari {filteredLinks.length} target</span>
                      <div className="flex items-center gap-1.5">
                        <button 
                          disabled={linkPage === 1}
                          onClick={() => setLinkPage(p => Math.max(1, p - 1))}
                          className="px-3 py-1.5 rounded-lg border border-darkBorder hover:text-white disabled:opacity-40 transition-all"
                        >
                          Prev
                        </button>
                        <button 
                          disabled={linkPage === totalPages}
                          onClick={() => setLinkPage(p => Math.min(totalPages, p + 1))}
                          className="px-3 py-1.5 rounded-lg border border-darkBorder hover:text-white disabled:opacity-40 transition-all"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Product Editor Modal */}
      {editingProduct && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="w-full max-w-xl bg-darkCard border border-darkBorder rounded-3xl p-8 space-y-6 shadow-2xl relative">
            <button 
              onClick={() => setEditingProduct(null)}
              className="absolute top-6 right-6 text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-extrabold text-white">Edit Detail Produk</h3>
            
            <div className="space-y-4 text-xs text-gray-300">
              <div className="space-y-1.5">
                <label className="font-bold text-gray-400 uppercase">Nama Produk</label>
                <input 
                  type="text" 
                  value={editingProduct.name}
                  onChange={(e) => setEditingProduct({ ...editingProduct, name: e.target.value })}
                  className="w-full bg-black/45 border border-darkBorder focus:border-shopee rounded-xl px-4 py-3 text-white outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="font-bold text-gray-400 uppercase">Kategori</label>
                  <input 
                    type="text" 
                    value={editingProduct.category}
                    onChange={(e) => setEditingProduct({ ...editingProduct, category: e.target.value })}
                    className="w-full bg-black/45 border border-darkBorder focus:border-shopee rounded-xl px-4 py-3 text-white outline-none"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="font-bold text-gray-400 uppercase">Harga Asli (Format Rp)</label>
                  <input 
                    type="text" 
                    value={editingProduct.original_price}
                    onChange={(e) => setEditingProduct({ ...editingProduct, original_price: e.target.value })}
                    className="w-full bg-black/45 border border-darkBorder focus:border-shopee rounded-xl px-4 py-3 text-white outline-none"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="font-bold text-gray-400 uppercase">Deskripsi Produk</label>
                <textarea 
                  rows="6"
                  value={editingProduct.description}
                  onChange={(e) => setEditingProduct({ ...editingProduct, description: e.target.value })}
                  className="w-full bg-black/45 border border-darkBorder focus:border-shopee rounded-xl px-4 py-3 text-white outline-none resize-none"
                ></textarea>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button 
                onClick={() => setEditingProduct(null)}
                className="flex-1 bg-glassBg hover:bg-white/5 border border-darkBorder text-white py-3 rounded-xl font-bold text-xs transition-all"
              >
                Batal
              </button>
              <button 
                onClick={handleSaveProduct}
                disabled={savingProduct}
                className="flex-1 shopee-gradient hover:bg-shopeeHover text-white py-3 rounded-xl font-bold text-xs shadow-lg shadow-shopee/15 transition-all flex items-center justify-center gap-1.5"
              >
                {savingProduct ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Save className="w-4 h-4" /> Simpan Perubahan
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer Info */}
      <footer className="py-8 border-t border-darkBorder text-center text-xs text-gray-600 font-semibold bg-darkCard/30 mt-12">
        ⚡ ShopeeBot Administration Dashboard © {new Date().getFullYear()} — Premium Management Panel
      </footer>
    </div>
  );
}
