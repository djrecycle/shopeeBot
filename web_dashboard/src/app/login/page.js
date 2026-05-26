'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LogIn, Key, User, ArrowLeft, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Username dan password wajib diisi');
      return;
    }
    
    setError('');
    setSubmitting(true);
    
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      
      if (res.ok && data.success) {
        router.push('/admin');
      } else {
        setError(data.error || 'Username atau password salah');
      }
    } catch (err) {
      setError('Terjadi kesalahan koneksi server');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0C] flex flex-col justify-center items-center p-4 relative">
      {/* Back to Catalog Link */}
      <Link href="/" className="absolute top-8 left-8 text-xs text-gray-500 hover:text-white flex items-center gap-1.5 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" /> Kembali ke Katalog
      </Link>

      <div className="w-full max-w-md glass-card rounded-3xl p-8 md:p-10 space-y-8 shadow-2xl relative overflow-hidden">
        {/* Glow Element */}
        <div className="absolute -top-12 -left-12 w-28 h-28 bg-shopee/20 blur-2xl rounded-full"></div>
        
        {/* Header Title */}
        <div className="text-center space-y-3 relative">
          <div className="w-14 h-14 shopee-gradient rounded-2xl flex items-center justify-center shadow-lg shadow-shopee/20 mx-auto font-bold text-2xl">🛒</div>
          <div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight">Login Dashboard Admin</h2>
            <p className="text-[11px] text-gray-500 font-semibold uppercase tracking-wider mt-1">ShopeeBot Pro Console</p>
          </div>
        </div>

        {/* Form Inputs */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-semibold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Username Field */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Username</label>
            <div className="relative flex items-center">
              <input 
                type="text"
                placeholder="Masukkan username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={submitting}
                className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee focus:ring-1 focus:ring-shopee/25 rounded-xl pl-11 pr-4 py-3 text-xs text-white outline-none transition-all"
              />
              <User className="absolute left-3.5 text-gray-500 w-4 h-4" />
            </div>
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider block">Password</label>
            <div className="relative flex items-center">
              <input 
                type="password"
                placeholder="Masukkan password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting}
                className="w-full bg-black/45 border border-darkBorder hover:border-gray-700 focus:border-shopee focus:ring-1 focus:ring-shopee/25 rounded-xl pl-11 pr-4 py-3 text-xs text-white outline-none transition-all"
              />
              <Key className="absolute left-3.5 text-gray-500 w-4 h-4" />
            </div>
          </div>

          {/* Submit Button */}
          <button 
            type="submit"
            disabled={submitting}
            className="w-full shopee-gradient hover:bg-shopeeHover disabled:opacity-50 text-white py-3.5 rounded-xl font-bold text-xs shadow-lg shadow-shopee/15 transition-all flex items-center justify-center gap-1.5 mt-2"
          >
            {submitting ? (
              <div className="w-4 h-4 rounded-full border-2 border-white/20 border-t-white animate-spin"></div>
            ) : (
              <>
                <LogIn className="w-4 h-4" /> Masuk ke Panel Control
              </>
            )}
          </button>
        </form>

        {/* Footer Hint */}
        <div className="text-center text-[10px] text-gray-600 font-semibold leading-relaxed">
          Default akun: <span className="text-gray-400 font-bold">admin</span> / <span className="text-gray-400 font-bold">admin123</span>
        </div>
      </div>
    </div>
  );
}
