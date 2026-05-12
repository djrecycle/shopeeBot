import customtkinter as ctk
import subprocess
import sys
import os
import threading
import pandas as pd
import webbrowser
from tkinter import ttk
from PIL import Image

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LocationPickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, options, initial_selection, callback):
        super().__init__(parent)
        self.title("Pilih Lokasi Penjual")
        self.geometry("400x600")
        self.callback = callback
        self.options = options
        self.checkboxes = {}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Cari Provinsi / Kota...")
        self.search_entry.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_locations)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.render_locations()

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.btn_ok = ctk.CTkButton(self.btn_frame, text="Selesai", command=self.apply_selection, fg_color="#27ae60", hover_color="#219150")
        self.btn_ok.pack(side="right", padx=5)
        
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Batal", command=self.destroy, fg_color="gray")
        self.btn_cancel.pack(side="right", padx=5)

        if initial_selection:
            for sid in initial_selection.split(","):
                if sid in self.checkboxes: self.checkboxes[sid].select()
        self.grab_set()

    def render_locations(self, filter_text=""):
        for cb in self.checkboxes.values(): cb.destroy()
        self.checkboxes = {}
        row = 0
        for id, opt in self.options.items():
            if filter_text.lower() in opt["label"].lower():
                cb = ctk.CTkCheckBox(self.scroll_frame, text=opt["label"])
                cb.grid(row=row, column=0, padx=10, pady=5, sticky="w")
                self.checkboxes[id] = cb
                row += 1

    def filter_locations(self, e): self.render_locations(self.search_entry.get())

    def apply_selection(self):
        selected_ids = [id for id, cb in self.checkboxes.items() if cb.get() == 1]
        self.callback(",".join(selected_ids) if selected_ids else "1")
        self.destroy()

class ScraperSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, sort_options, location_data, current_loc_ids, defaults, start_callback):
        super().__init__(parent)
        self.title("⚙️ Konfigurasi Link Scraper")
        self.geometry("550x650")
        self.start_callback = start_callback
        self.sort_options = sort_options
        self.location_data = location_data
        self.selected_loc_ids = current_loc_ids
        
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Konfigurasi Pencarian & Scraping", font=ctk.CTkFont(size=18, weight="bold"), text_color="#EE4D2D").grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        self.add_field("Target Keyword / URL Toko:", defaults.get("keyword", ""), 1)
        self.keyword_entry = self.last_entry
        self.add_field("Simpan ke Kategori:", defaults.get("category", ""), 3)
        self.category_entry = self.last_entry
        self.add_field("Maksimal Halaman (Max Page):", defaults.get("pages", "1"), 5)
        self.pages_entry = self.last_entry

        self.add_label("Urutan Pencarian:", 7)
        self.sort_option = ctk.CTkOptionMenu(self, values=list(self.sort_options.keys()), height=35)
        self.sort_option.set("Terlaris")
        self.sort_option.grid(row=8, column=0, padx=30, pady=(5, 10), sticky="ew")

        self.add_label("Filter Lokasi Toko:", 9)
        self.loc_btn = ctk.CTkButton(self, text="📍 Pilih Lokasi (Semua)", height=35, fg_color="#2c2c36", command=self.open_location_picker)
        self.loc_btn.grid(row=10, column=0, padx=30, pady=(5, 10), sticky="ew")
        self.update_loc_text()

        self.add_field("Min Rating (0.0 - 5.0):", "4.9", 11)
        self.rating_entry = self.last_entry

        self.btn_start = ctk.CTkButton(self, text="🚀 Mulai Scraping Sekarang", height=55, fg_color="#EE4D2D", hover_color="#D73211", font=ctk.CTkFont(size=14, weight="bold"), command=self.start)
        self.btn_start.grid(row=13, column=0, padx=30, pady=(10, 30), sticky="ew")
        self.grab_set()

    def add_label(self, text, row):
        ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=13, weight="bold")).grid(row=row, column=0, padx=30, pady=(5, 0), sticky="w")

    def add_field(self, label, default, row):
        self.add_label(label, row)
        self.last_entry = ctk.CTkEntry(self, height=35)
        self.last_entry.insert(0, default)
        self.last_entry.grid(row=row+1, column=0, padx=30, pady=(5, 10), sticky="ew")

    def open_location_picker(self): LocationPickerDialog(self, self.location_data, self.selected_loc_ids, self.update_location_selection)
    def update_location_selection(self, ids):
        self.selected_loc_ids = ids
        self.update_loc_text()
    def update_loc_text(self):
        labels = [self.location_data[id]["label"] for id in self.selected_loc_ids.split(",")]
        text = f"📍 {', '.join(labels)}"
        if len(text) > 45: text = text[:42] + "..."
        self.loc_btn.configure(text=text)

    def start(self):
        params = {
            "keyword": self.keyword_entry.get().strip(),
            "category": self.category_entry.get().strip(),
            "pages": self.pages_entry.get().strip(),
            "sort": self.sort_options.get(self.sort_option.get(), "3"),
            "location": self.selected_loc_ids,
            "rating": self.rating_entry.get().strip()
        }
        self.start_callback(params)
        self.destroy()

class ProductScraperSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, category_stats, start_callback):
        super().__init__(parent)
        self.title("⚙️ Konfigurasi Product Scraper")
        self.geometry("550x650")
        self.start_callback = start_callback
        self.category_stats = category_stats  # dict: {cat: {done: N, pending: N, keywords: {kw: {done, pending}}}}
        
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Konfigurasi Detail Scraper", font=ctk.CTkFont(size=18, weight="bold"), text_color="#EE4D2D").grid(row=0, column=0, padx=30, pady=(30, 15), sticky="w")

        # Prepare Category values
        total_done = sum(s["done"] for s in category_stats.values())
        total_pending = sum(s["pending"] for s in category_stats.values())
        
        self.cat_map = {f"Semua Kategori (✅ {total_done} | 📋 {total_pending})": "Semua"}
        cat_display_values = [list(self.cat_map.keys())[0]]
        for cat, stats in category_stats.items():
            label = f"{cat} (✅ {stats['done']} | 📋 {stats['pending']})"
            cat_display_values.append(label)
            self.cat_map[label] = cat

        # Select Kategori
        ctk.CTkLabel(self, text="Pilih Kategori:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=30, pady=(10, 0), sticky="w")
        self.cat_option = ctk.CTkOptionMenu(self, values=cat_display_values, height=35, command=self.on_cat_change)
        self.cat_option.set(cat_display_values[0])
        self.cat_option.grid(row=2, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Select Keyword
        ctk.CTkLabel(self, text="Pilih Target (Keyword/Toko):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=3, column=0, padx=30, pady=(10, 0), sticky="w")
        self.target_option = ctk.CTkOptionMenu(self, values=["Semua Target"], height=35, command=self.on_target_change)
        self.target_option.grid(row=4, column=0, padx=30, pady=(5, 10), sticky="ew")
        
        self.keyword_map = {}

        # Info label
        self.info_label = ctk.CTkLabel(self, text=f"Total: {total_done + total_pending} produk  |  ✅ {total_done} selesai  |  📋 {total_pending} tersisa", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.info_label.grid(row=5, column=0, padx=30, pady=(0, 15), sticky="w")

        # Max URLs
        ctk.CTkLabel(self, text="Maksimal Produk discrape (Batch):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=6, column=0, padx=30, pady=(10, 0), sticky="w")
        self.max_urls_entry = ctk.CTkEntry(self, height=35)
        self.max_urls_entry.insert(0, str(min(total_pending, 10)) if total_pending > 0 else "10")
        self.max_urls_entry.grid(row=7, column=0, padx=30, pady=(5, 15), sticky="ew")

        # Force Re-scrape
        self.force_var = ctk.BooleanVar(value=False)
        self.force_cb = ctk.CTkCheckBox(self, text="Paksa Scrape Ulang (Re-scrape)", variable=self.force_var, font=ctk.CTkFont(size=13))
        self.force_cb.grid(row=8, column=0, padx=30, pady=10, sticky="w")

        # Start Button
        self.btn_start = ctk.CTkButton(self, text="📦 Mulai Scrape Detail Produk", height=55, fg_color="#EE4D2D", hover_color="#D73211", font=ctk.CTkFont(size=14, weight="bold"), command=self.start)
        self.btn_start.grid(row=9, column=0, padx=30, pady=(20, 30), sticky="ew")
        
        # Initialize Keyword Dropdown
        self.on_cat_change(cat_display_values[0])
        
        self.grab_set()

    def on_cat_change(self, choice):
        cat = self.cat_map.get(choice, "Semua")
        
        # Populate Keywords based on Category
        kw_display_values = []
        self.keyword_map = {}
        
        if cat == "Semua":
            # Show all keywords across all categories
            all_done = sum(s["done"] for s in self.category_stats.values())
            all_pending = sum(s["pending"] for s in self.category_stats.values())
            label_all = f"Semua Target (✅ {all_done} | 📋 {all_pending})"
            kw_display_values.append(label_all)
            self.keyword_map[label_all] = "Semua"
            
            for c_stats in self.category_stats.values():
                for kw, stats in c_stats["keywords"].items():
                    label = f"{kw} (✅ {stats['done']} | 📋 {stats['pending']})"
                    if label not in kw_display_values: # Avoid duplicates if same keyword in diff cats
                        kw_display_values.append(label)
                        self.keyword_map[label] = kw
        else:
            c_stats = self.category_stats.get(cat, {"done":0, "pending":0, "keywords":{}})
            label_all = f"Semua Target (✅ {c_stats['done']} | 📋 {c_stats['pending']})"
            kw_display_values.append(label_all)
            self.keyword_map[label_all] = "Semua"
            
            for kw, stats in c_stats["keywords"].items():
                label = f"{kw} (✅ {stats['done']} | 📋 {stats['pending']})"
                kw_display_values.append(label)
                self.keyword_map[label] = kw
                
        self.target_option.configure(values=kw_display_values)
        self.target_option.set(kw_display_values[0])
        self.on_target_change(kw_display_values[0])

    def on_target_change(self, choice):
        kw = self.keyword_map.get(choice, "Semua")
        cat_choice = self.cat_option.get()
        cat = self.cat_map.get(cat_choice, "Semua")
        
        if kw == "Semua":
            if cat == "Semua":
                done = sum(s["done"] for s in self.category_stats.values())
                pending = sum(s["pending"] for s in self.category_stats.values())
            else:
                stats = self.category_stats.get(cat, {"done": 0, "pending": 0})
                done, pending = stats["done"], stats["pending"]
        else:
            # Find keyword stats
            done, pending = 0, 0
            if cat == "Semua":
                for c_stats in self.category_stats.values():
                    if kw in c_stats["keywords"]:
                        done = c_stats["keywords"][kw]["done"]
                        pending = c_stats["keywords"][kw]["pending"]
                        break
            else:
                c_stats = self.category_stats.get(cat, {"keywords":{}})
                if kw in c_stats["keywords"]:
                    done = c_stats["keywords"][kw]["done"]
                    pending = c_stats["keywords"][kw]["pending"]
                    
        self.info_label.configure(text=f"Total: {done + pending} produk  |  ✅ {done} selesai  |  📋 {pending} tersisa")

    def start(self):
        selected_kw = self.target_option.get()
        actual_keyword = self.keyword_map.get(selected_kw, "Semua")
        
        selected_cat = self.cat_option.get()
        actual_category = self.cat_map.get(selected_cat, "Semua")
        
        params = {
            "target_category": actual_category,
            "target_keyword": actual_keyword,
            "max_urls": self.max_urls_entry.get().strip(),
            "force": self.force_var.get()
        }
        self.start_callback(params)
        self.destroy()

class MessageSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, category_stats, start_callback):
        super().__init__(parent)
        self.title("💬 Konfigurasi Messenger")
        self.geometry("600x750")
        self.start_callback = start_callback
        self.category_stats = category_stats
        
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Konfigurasi Broadcast Pesan", font=ctk.CTkFont(size=18, weight="bold"), text_color="#27ae60").grid(row=0, column=0, padx=30, pady=(30, 15), sticky="w")

        # Prepare Category values
        total_sent = sum(s.get("sent_only", 0) for s in category_stats.values())
        total_scraped = sum(s.get("scraped", 0) for s in category_stats.values())
        total_all = sum(s["done"] + s["pending"] for s in category_stats.values())
        total_unchatted = total_all - total_sent
        
        self.cat_map = {f"Semua Kategori (✅ {total_scraped} di-scrape | 💬 {total_sent} terkirim | 📋 {total_unchatted} tersisa)": "Semua"}
        cat_display_values = [list(self.cat_map.keys())[0]]
        for cat, stats in category_stats.items():
            sent = stats.get("sent_only", 0)
            scraped = stats.get("scraped", 0)
            total = stats["done"] + stats["pending"]
            label = f"{cat} (✅ {scraped} di-scrape | 💬 {sent} terkirim | 📋 {total - sent} tersisa)"
            cat_display_values.append(label)
            self.cat_map[label] = cat

        # Select Kategori
        ctk.CTkLabel(self, text="Pilih Kategori Target:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=30, pady=(10, 0), sticky="w")
        self.cat_option = ctk.CTkOptionMenu(self, values=cat_display_values, height=35, command=self.on_cat_change)
        self.cat_option.set(cat_display_values[0])
        self.cat_option.grid(row=2, column=0, padx=30, pady=(5, 10), sticky="ew")

        # Select Keyword
        ctk.CTkLabel(self, text="Pilih Target (Keyword/Toko):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=3, column=0, padx=30, pady=(10, 0), sticky="w")
        self.target_option = ctk.CTkOptionMenu(self, values=["Semua Target"], height=35, command=self.on_target_change)
        self.target_option.grid(row=4, column=0, padx=30, pady=(5, 10), sticky="ew")
        
        self.keyword_map = {}

        # Info label
        actual_sent = sum(s.get("sent_only", 0) for s in category_stats.values())
        total_all = sum(s["done"] + s["pending"] for s in category_stats.values())
        self.info_label = ctk.CTkLabel(self, text=f"Total: {total_all} toko  |  💬 {actual_sent} pesan terkirim  |  📋 {total_all - actual_sent} belum dichat", font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.info_label.grid(row=5, column=0, padx=30, pady=(0, 15), sticky="w")

        # Message Textbox
        ctk.CTkLabel(self, text="Isi Pesan (Kosongkan untuk default):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=6, column=0, padx=30, pady=(10, 0), sticky="w")
        self.msg_textbox = ctk.CTkTextbox(self, height=120, corner_radius=8)
        self.msg_textbox.grid(row=7, column=0, padx=30, pady=(5, 15), sticky="ew")
        default_msg = "Halo kak, apakah toko ini menerima dropship dan bisa menggunakan resi otomatis?, jika saya diizinkan menjadi dropshipper bolehkah saya meminta kontak yang bisa dihubungi agar mempermudah komunikasi?,, mohon maaf mengganggu waktunya kak"
        self.msg_textbox.insert("0.0", default_msg)

        # Max URLs
        ctk.CTkLabel(self, text="Maksimal Toko dichat (Batch):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=8, column=0, padx=30, pady=(10, 0), sticky="w")
        self.max_urls_entry = ctk.CTkEntry(self, height=35)
        self.max_urls_entry.insert(0, str(min(total_unchatted, 10)) if total_unchatted > 0 else "10")
        self.max_urls_entry.grid(row=9, column=0, padx=30, pady=(5, 15), sticky="ew")

        # Start Button
        self.btn_start = ctk.CTkButton(self, text="💬 Mulai Broadcast Pesan", height=55, fg_color="#27ae60", hover_color="#219150", font=ctk.CTkFont(size=14, weight="bold"), command=self.start)
        self.btn_start.grid(row=10, column=0, padx=30, pady=(20, 30), sticky="ew")
        
        # Initialize Keyword Dropdown
        self.on_cat_change(cat_display_values[0])
        
        self.grab_set()

    def on_cat_change(self, choice):
        cat = self.cat_map.get(choice, "Semua")
        kw_display_values = []
        self.keyword_map = {}
        
        if cat == "Semua":
            all_sent = sum(s.get("sent_only", 0) for s in self.category_stats.values())
            all_scraped = sum(s.get("scraped", 0) for s in self.category_stats.values())
            all_total = sum(s["done"] + s["pending"] for s in self.category_stats.values())
            label_all = f"Semua Target (✅ {all_scraped} di-scrape | 💬 {all_sent} terkirim | 📋 {all_total - all_sent} tersisa)"
            kw_display_values.append(label_all)
            self.keyword_map[label_all] = "Semua"
            
            for c_stats in self.category_stats.values():
                for kw, stats in c_stats["keywords"].items():
                    sent = stats.get("sent_only", 0)
                    scraped = stats.get("scraped", 0)
                    total = stats["done"] + stats["pending"]
                    label = f"{kw} (✅ {scraped} di-scrape | 💬 {sent} terkirim | 📋 {total - sent} tersisa)"
                    if label not in kw_display_values:
                        kw_display_values.append(label)
                        self.keyword_map[label] = kw
        else:
            c_stats = self.category_stats.get(cat, {"done":0, "pending":0, "sent_only":0, "scraped":0, "keywords":{}})
            total = c_stats["done"] + c_stats["pending"]
            sent = c_stats.get('sent_only', 0)
            scraped = c_stats.get('scraped', 0)
            label_all = f"Semua Target (✅ {scraped} di-scrape | 💬 {sent} terkirim | 📋 {total - sent} tersisa)"
            kw_display_values.append(label_all)
            self.keyword_map[label_all] = "Semua"
            
            for kw, stats in c_stats["keywords"].items():
                sent = stats.get("sent_only", 0)
                scraped = stats.get("scraped", 0)
                total = stats["done"] + stats["pending"]
                label = f"{kw} (✅ {scraped} di-scrape | 💬 {sent} terkirim | 📋 {total - sent} tersisa)"
                kw_display_values.append(label)
                self.keyword_map[label] = kw
                
        self.target_option.configure(values=kw_display_values)
        self.target_option.set(kw_display_values[0])
        self.on_target_change(kw_display_values[0])

    def on_target_change(self, choice):
        kw = self.keyword_map.get(choice, "Semua")
        cat_choice = self.cat_option.get()
        cat = self.cat_map.get(cat_choice, "Semua")
        
        if kw == "Semua":
            if cat == "Semua":
                done = sum(s.get("sent_only", 0) for s in self.category_stats.values())
                pending = sum(s["done"] + s["pending"] for s in self.category_stats.values()) - done
            else:
                stats = self.category_stats.get(cat, {"done": 0, "pending": 0, "sent_only": 0})
                done, pending = stats["sent_only"], (stats["done"] + stats["pending"]) - stats["sent_only"]
        else:
            done, pending = 0, 0
            if cat == "Semua":
                for c_stats in self.category_stats.values():
                    if kw in c_stats["keywords"]:
                        done = c_stats["keywords"][kw].get("sent_only", 0)
                        pending = (c_stats["keywords"][kw]["done"] + c_stats["keywords"][kw]["pending"]) - done
                        break
            else:
                c_stats = self.category_stats.get(cat, {"keywords":{}})
                if kw in c_stats["keywords"]:
                    done = c_stats["keywords"][kw].get("sent_only", 0)
                    pending = (c_stats["keywords"][kw]["done"] + c_stats["keywords"][kw]["pending"]) - done
                    
        self.info_label.configure(text=f"Total: {done + pending} toko  |  💬 {done} pesan terkirim  |  📋 {pending} belum dichat")

    def start(self):
        selected_kw = self.target_option.get()
        actual_keyword = self.keyword_map.get(selected_kw, "Semua")
        
        selected_cat = self.cat_option.get()
        actual_category = self.cat_map.get(selected_cat, "Semua")
        
        params = {
            "category": actual_category if actual_category != "Semua" else "",
            "keyword": actual_keyword if actual_keyword != "Semua" else "",
            "message": self.msg_textbox.get("0.0", "end").strip(),
            "max_urls": self.max_urls_entry.get().strip()
        }
        self.start_callback(params)
        self.destroy()

class ShopeeBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ShopeeBot Automation Control Panel")
        self.geometry("1100x850")
        self.orange_color, self.orange_hover, self.bg_color, self.sidebar_color = "#EE4D2D", "#D73211", "#0f0f12", "#19191e"
        self.sort_options = {"Terlaris": "3", "Terbaru": "2", "Relevan": "1", "Harga Terendah": "4", "Harga Tertinggi": "5"}
        self.location_data = {"1": {"label": "Semua Lokasi", "value": ""}, "2": {"label": "Jabodetabek", "value": "Jabodetabek"}, "3": {"label": "Jawa Barat", "value": "Jawa Barat"}, "4": {"label": "Jawa Tengah", "value": "Jawa Tengah"}, "5": {"label": "Jawa Timur", "value": "Jawa Timur"}, "6": {"label": "Banten", "value": "Banten"}, "7": {"label": "DI Yogyakarta", "value": "DI Yogyakarta"}, "8": {"label": "Bali", "value": "Bali"}, "9": {"label": "Sumatera Utara", "value": "Sumatera Utara"}, "10": {"label": "Sumatera Selatan", "value": "Sumatera Selatan"}, "11": {"label": "Sumatera Barat", "value": "Sumatera Barat"}, "12": {"label": "Riau", "value": "Riau"}, "13": {"label": "Kepulauan Riau", "value": "Kepulauan Riau"}, "14": {"label": "Lampung", "value": "Lampung"}, "15": {"label": "Kalimantan Barat", "value": "Kalimantan Barat"}, "16": {"label": "Kalimantan Selatan", "value": "Kalimantan Selatan"}, "17": {"label": "Kalimantan Timur", "value": "Kalimantan Timur"}, "18": {"label": "Sulawesi Selatan", "value": "Sulawesi Selatan"}, "19": {"label": "Sulawesi Utara", "value": "Sulawesi Utara"}, "20": {"label": "Nusa Tenggara Barat", "value": "Nusa Tenggara Barat"}, "21": {"label": "Aceh", "value": "Aceh"}, "22": {"label": "Jambi", "value": "Jambi"}, "23": {"label": "Bengkulu", "value": "Bengkulu"}, "24": {"label": "Kalimantan Tengah", "value": "Kalimantan Tengah"}, "25": {"label": "Sulawesi Tengah", "value": "Sulawesi Tengah"}, "26": {"label": "Sulawesi Tenggara", "value": "Sulawesi Tenggara"}, "27": {"label": "Papua", "value": "Papua"}, "28": {"label": "Maluku", "value": "Maluku"}}
        self.selected_location_ids = "1"
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar_frame, text="🛍️ ShopeeBot", font=ctk.CTkFont(size=24, weight="bold"), text_color=self.orange_color).grid(row=0, column=0, padx=20, pady=(30, 30))
        for i, (txt, cmd) in enumerate([("🏠 Dashboard", self.show_dashboard), ("📊 Lihat Database", self.show_database_view), ("🌐 Generate Site", lambda: self.run_script("generate_site.py")), ("📂 Manajer File MD", self.show_file_view)], 2):
            self.create_sidebar_button(txt, cmd, i)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=1, sticky="nsew"); self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_rowconfigure(1, weight=1)
        self.header_label = ctk.CTkLabel(self.main_frame, text="ShopeeBot Dashboard", font=ctk.CTkFont(size=22, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        self.create_home_view(); self.create_database_view(); self.create_file_view(); self.show_dashboard()
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Ready", font=ctk.CTkFont(size=11), fg_color="#19191e")
        self.status_label.grid(row=2, column=0, sticky="ew")

    def create_home_view(self):
        self.home_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1); self.home_frame.grid_rowconfigure(2, weight=1)
        self.inputs_frame = ctk.CTkFrame(self.home_frame, fg_color="#19191e", corner_radius=10)
        self.inputs_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew", padx=40); self.inputs_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.keyword_entry = self.add_input(self.inputs_frame, "Keyword / URL Toko:", "Contoh: Sepatu", 0, 0)
        self.category_entry = self.add_input(self.inputs_frame, "Kategori (Folder):", "Contoh: Fashion", 0, 1)
        self.pages_entry = self.add_input(self.inputs_frame, "Jumlah Halaman:", "Default: 1", 0, 2)
        self.controls_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew", padx=40)
        for i, (txt, cmd) in enumerate([("🔑 Login", lambda: self.run_script("open_browser.py")), ("🔗 Link Scraper", self.open_scraper_settings), ("📦 Product Scraper", self.open_product_scraper_settings), ("💬 Messenger", self.open_messenger_settings)]):
            self.create_action_button(txt, cmd, 0, i)
        self.console_text = ctk.CTkTextbox(self.home_frame, corner_radius=10, fg_color="#1e1e24", text_color="#27ae60", font=ctk.CTkFont(family="Courier", size=13))
        self.console_text.grid(row=3, column=0, sticky="nsew", pady=(0, 20), padx=40)
        banner = """=======================================================
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

"""
        self.log(banner)
        self.log(">>> ShopeeBot GUI initialized.\n")
        self.console_text.configure(state="disabled")

    def add_input(self, frame, label, placeholder, row, col):
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).grid(row=row, column=col, padx=20, pady=(15, 0), sticky="w")
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=35); entry.grid(row=row+1, column=col, padx=20, pady=(5, 15), sticky="ew")
        return entry

    def open_scraper_settings(self):
        defaults = {"keyword": self.keyword_entry.get().strip(), "category": self.category_entry.get().strip(), "pages": self.pages_entry.get().strip()}
        ScraperSettingsDialog(self, self.sort_options, self.location_data, self.selected_location_ids, defaults, self.start_scrape_links)

    def start_scrape_links(self, full_params):
        for e, v in [(self.keyword_entry, full_params["keyword"]), (self.category_entry, full_params["category"]), (self.pages_entry, full_params["pages"])]: e.delete(0, "end"); e.insert(0, v)
        self.selected_location_ids = full_params["location"]; self.run_script("scrape_links.py", full_params)

    def open_product_scraper_settings(self):
        csv_path = "shopee_links.csv"
        category_stats = {}
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if "Status" not in df.columns: df["Status"] = ""
                df["Status"] = df["Status"].fillna("")
                
                if "Kategori" in df.columns and "Keyword" in df.columns:
                    for cat in sorted(df["Kategori"].dropna().unique().tolist()):
                        cat_df = df[df["Kategori"] == cat]
                        cat_done = len(cat_df[cat_df["Status"].isin(["Done", "Sent"])])
                        cat_pending = len(cat_df) - cat_done
                        
                        keywords_dict = {}
                        for kw in sorted(cat_df["Keyword"].dropna().unique().tolist()):
                            kw_df = cat_df[cat_df["Keyword"] == kw]
                            done = len(kw_df[kw_df["Status"].isin(["Done", "Sent"])])
                            pending = len(kw_df) - done
                            keywords_dict[kw] = {"done": done, "pending": pending}
                            
                        category_stats[cat] = {
                            "done": cat_done,
                            "pending": cat_pending,
                            "keywords": keywords_dict
                        }
            except: pass
        ProductScraperSettingsDialog(self, category_stats, self.start_scrape_products)

    def start_scrape_products(self, params):
        self.run_script("shoppescrap.py", params)

    def open_messenger_settings(self):
        csv_path = "shopee_links.csv"
        category_stats = {}
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, dtype={"Status Chat": str}) if "Status Chat" in pd.read_csv(csv_path, nrows=0).columns else pd.read_csv(csv_path)
                if "Status Chat" not in df.columns: df["Status Chat"] = ""
                df["Status Chat"] = df["Status Chat"].fillna("")
                
                if "Kategori" in df.columns and "Keyword" in df.columns:
                    for cat in sorted(df["Kategori"].dropna().unique().tolist()):
                        cat_df = df[df["Kategori"] == cat]
                        # For messenger, "Sent" means done, skip Toko Sama, others pending
                        cat_done = len(cat_df[cat_df["Status Chat"].isin(["Sent", "Skip", "Skip (Toko Sama)"])])
                        cat_sent_only = len(cat_df[cat_df["Status Chat"] == "Sent"])
                        cat_scraped = len(cat_df[cat_df["Status"].isin(["Done", "Sent"])])
                        cat_pending = len(cat_df) - cat_done
                        
                        keywords_dict = {}
                        for kw in sorted(cat_df["Keyword"].dropna().unique().tolist()):
                            kw_df = cat_df[cat_df["Keyword"] == kw]
                            done = len(kw_df[kw_df["Status Chat"].isin(["Sent", "Skip", "Skip (Toko Sama)"])])
                            kw_sent_only = len(kw_df[kw_df["Status Chat"] == "Sent"])
                            kw_scraped = len(kw_df[kw_df["Status"].isin(["Done", "Sent"])])
                            pending = len(kw_df) - done
                            keywords_dict[kw] = {"done": done, "pending": pending, "sent_only": kw_sent_only, "scraped": kw_scraped}
                            
                        category_stats[cat] = {
                            "done": cat_done,
                            "pending": cat_pending,
                            "sent_only": cat_sent_only,
                            "scraped": cat_scraped,
                            "keywords": keywords_dict
                        }
            except: pass
        MessageSettingsDialog(self, category_stats, self.start_messenger)

    def start_messenger(self, params):
        self.run_script("send_message.py", params)

    def hide_all_views(self):
        self.home_frame.grid_forget()
        self.database_frame.grid_forget()
        if hasattr(self, 'file_frame'): self.file_frame.grid_forget()

    def show_dashboard(self): self.hide_all_views(); self.home_frame.grid(row=1, column=0, sticky="nsew")
    def show_database_view(self): self.hide_all_views(); self.database_frame.grid(row=1, column=0, sticky="nsew"); self.load_table_data()
    def show_file_view(self): self.hide_all_views(); self.file_frame.grid(row=1, column=0, sticky="nsew"); self.load_file_data()

    def create_database_view(self):
        self.database_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.database_frame.grid_columnconfigure(0, weight=1)
        self.database_frame.grid_rowconfigure(2, weight=1)

        # Header bar
        self.db_header = ctk.CTkFrame(self.database_frame, fg_color="#19191e", corner_radius=12, height=60)
        self.db_header.grid(row=0, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.db_header.grid_propagate(False)

        ctk.CTkLabel(self.db_header, text="📊 Database Link Produk", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EE4D2D").pack(side="left", padx=20)
        self.db_count_label = ctk.CTkLabel(self.db_header, text="0 link", font=ctk.CTkFont(size=13), text_color="#94A3B8")
        self.db_count_label.pack(side="left", padx=5)

        # Action buttons bar
        self.db_actions = ctk.CTkFrame(self.database_frame, fg_color="transparent")
        self.db_actions.grid(row=1, column=0, padx=30, pady=(12, 8), sticky="ew")

        ctk.CTkButton(self.db_actions, text="🔄 Refresh", width=100, height=34, corner_radius=8,
                      fg_color="#1a6b3c", hover_color="#219150", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.load_table_data).pack(side="left", padx=(0, 8))
        ctk.CTkButton(self.db_actions, text="🗑️ Hapus Terpilih", width=140, height=34, corner_radius=8,
                      fg_color="#c0392b", hover_color="#e74c3c", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.delete_selected_rows).pack(side="left", padx=4)
        ctk.CTkButton(self.db_actions, text="⚠️ Hapus Semua", width=130, height=34, corner_radius=8,
                      fg_color="#555", hover_color="#777", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.delete_all_rows).pack(side="left", padx=4)

        self.db_status_label = ctk.CTkLabel(self.db_actions, text="Klik baris untuk memilih (Ctrl+Klik untuk pilih banyak)", font=ctk.CTkFont(size=11), text_color="#636e72")
        self.db_status_label.pack(side="right", padx=10)

        # Style the Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("DB.Treeview",
                        background="#16161A",
                        foreground="#E0E0E0",
                        fieldbackground="#16161A",
                        rowheight=36,
                        font=("Segoe UI", 11),
                        borderwidth=0,
                        relief="flat")
        style.configure("DB.Treeview.Heading",
                        background="#1E1E24",
                        foreground="#EE4D2D",
                        font=("Segoe UI", 11, "bold"),
                        relief="flat",
                        borderwidth=0,
                        padding=8)
        style.map("DB.Treeview",
                  background=[("selected", "#EE4D2D")],
                  foreground=[("selected", "#FFFFFF")])
        style.map("DB.Treeview.Heading",
                  background=[("active", "#2a2a32")])

        # Table container with rounded corners
        self.tree_container = ctk.CTkFrame(self.database_frame, fg_color="#16161A", corner_radius=12, border_width=1, border_color="#2a2a32")
        self.tree_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.tree_container.grid_columnconfigure(0, weight=1)
        self.tree_container.grid_rowconfigure(0, weight=1)

        # Table
        columns = ("No", "Status Chat", "Kategori", "Keyword", "Toko", "Link", "Rating", "Status")
        self.tree = ttk.Treeview(self.tree_container, columns=columns, show="headings", selectmode="extended", style="DB.Treeview")

        self.tree.heading("No", text="#")
        self.tree.heading("Status Chat", text="💬 Chat")
        self.tree.heading("Kategori", text="📁 Kategori")
        self.tree.heading("Keyword", text="🔑 Keyword")
        self.tree.heading("Toko", text="🏪 Toko")
        self.tree.heading("Link", text="🔗 Link Produk")
        self.tree.heading("Rating", text="⭐ Rating")
        self.tree.heading("Status", text="📋 Status Scrape")

        self.tree.column("No", width=40, minwidth=40, anchor="center")
        self.tree.column("Status Chat", width=90, minwidth=60, anchor="center")
        self.tree.column("Kategori", width=100, minwidth=70, anchor="center")
        self.tree.column("Keyword", width=120, minwidth=70, anchor="center")
        self.tree.column("Toko", width=130, minwidth=80)
        self.tree.column("Link", width=250, minwidth=150)
        self.tree.column("Rating", width=60, minwidth=40, anchor="center")
        self.tree.column("Status", width=100, minwidth=60, anchor="center")

        # Scrollbars
        self.tree_vscroll = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.tree.yview)
        self.tree_hscroll = ttk.Scrollbar(self.tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_vscroll.set, xscrollcommand=self.tree_hscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(8, 0))
        self.tree_vscroll.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 4))
        self.tree_hscroll.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        # Zebra striping tags
        self.tree.tag_configure("even", background="#1a1a20")
        self.tree.tag_configure("odd", background="#16161A")
        self.tree.tag_configure("done", foreground="#27ae60")
        self.tree.tag_configure("pending", foreground="#f39c12")

    @staticmethod
    def extract_shop_name(link):
        """Extract shop identifier from Shopee URL like shopee.co.id/Product-i.SHOPID.PRODUCTID"""
        try:
            link = str(link)
            if "-i." in link:
                # Format: /Product-Name-i.ShopID.ProductID
                shop_id = link.split("-i.")[1].split(".")[0]
                return f"Shop {shop_id}"
            elif "shopee.co.id/shop/" in link:
                return link.split("shop/")[1].split("/")[0].split("?")[0]
            return "-"
        except:
            return "-"

    def load_table_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        if os.path.exists("shopee_links.csv"):
            try:
                df = pd.read_csv("shopee_links.csv")
                if "Status" not in df.columns: df["Status"] = ""
                df["Status"] = df["Status"].fillna("")
                for i, (_, row) in enumerate(df.iterrows()):
                    status_val = str(row.get("Status", ""))
                    status_chat_val = str(row.get("Status Chat", ""))
                    link = str(row.get("Link Produk", "-"))
                    
                    # Cek jika kolom Toko ada di CSV, jika tidak ambil dari URL
                    toko = str(row.get("Toko", ""))
                    if not toko or toko == "nan" or toko == "-":
                        toko = self.extract_shop_name(link)
                        
                    tag = "even" if i % 2 == 0 else "odd"
                    if status_val == "Done": tag = "done"
                    elif status_val in ("", "-"): tag = "pending"
                    self.tree.insert("", "end", values=(
                        i + 1,
                        status_chat_val if status_chat_val and status_chat_val != "nan" else "-",
                        row.get("Kategori", "-"),
                        row.get("Keyword", "-"),
                        toko,
                        link,
                        row.get("Rating", "-"),
                        status_val if status_val else "-"
                    ), tags=(tag,))
                done_count = len(df[df["Status"].isin(["Done", "Sent"])])
                chat_sent_count = len(df[df["Status Chat"] == "Sent"]) if "Status Chat" in df.columns else 0
                self.db_count_label.configure(text=f"— {len(df)} link")
                self.db_status_label.configure(text=f"✅ {done_count} di-scrape  |  💬 {chat_sent_count} pesan terkirim  |  📋 {len(df) - done_count} tersisa")
            except Exception as e:
                print(f"Error loading table: {e}")
                self.db_count_label.configure(text=f"Error: {e}")
        else:
            self.db_count_label.configure(text="— Tidak ada data")

    def delete_selected_rows(self):
        selected = self.tree.selection()
        if not selected:
            self.log("⚠️ Pilih baris yang ingin dihapus terlebih dahulu.")
            return
        dialog = ctk.CTkInputDialog(text=f"Hapus {len(selected)} baris terpilih?\nKetik 'ya' untuk konfirmasi:", title="Konfirmasi Hapus")
        result = dialog.get_input()
        if result and result.lower() == "ya":
            links_to_delete = set()
            for item in selected:
                vals = self.tree.item(item, "values")
                if vals and len(vals) > 4: links_to_delete.add(vals[4])
            try:
                df = pd.read_csv("shopee_links.csv")
                df = df[~df["Link Produk"].isin(links_to_delete)]
                df.to_csv("shopee_links.csv", index=False)
                self.log(f"🗑️ {len(links_to_delete)} baris berhasil dihapus.")
                self.load_table_data()
            except Exception as e: self.log(f"❌ Gagal menghapus: {e}")

    def delete_all_rows(self):
        dialog = ctk.CTkInputDialog(text="Hapus SEMUA data dari database?\nKetik 'ya' untuk konfirmasi:", title="⚠️ Konfirmasi Hapus Semua")
        result = dialog.get_input()
        if result and result.lower() == "ya":
            try:
                df = pd.read_csv("shopee_links.csv")
                df.iloc[0:0].to_csv("shopee_links.csv", index=False)
                self.log("🗑️ Semua data berhasil dihapus.")
                self.load_table_data()
            except Exception as e: self.log(f"❌ Gagal menghapus: {e}")

    # ==========================================
    # FILE MANAGER VIEW
    # ==========================================
    def create_file_view(self):
        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_rowconfigure(2, weight=1)

        # Header bar
        self.file_header = ctk.CTkFrame(self.file_frame, fg_color="#19191e", corner_radius=12, height=60)
        self.file_header.grid(row=0, column=0, padx=30, pady=(10, 0), sticky="ew")
        self.file_header.grid_propagate(False)

        ctk.CTkLabel(self.file_header, text="📂 File Produk Markdown", font=ctk.CTkFont(size=16, weight="bold"), text_color="#EE4D2D").pack(side="left", padx=20)
        self.file_count_label = ctk.CTkLabel(self.file_header, text="0 file", font=ctk.CTkFont(size=13), text_color="#94A3B8")
        self.file_count_label.pack(side="left", padx=5)

        # Action buttons
        self.file_actions = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.file_actions.grid(row=1, column=0, padx=30, pady=(12, 8), sticky="ew")

        ctk.CTkButton(self.file_actions, text="🔄 Refresh", width=100, height=34, corner_radius=8,
                      fg_color="#1a6b3c", hover_color="#219150", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.load_file_data).pack(side="left", padx=(0, 8))
        ctk.CTkButton(self.file_actions, text="🗑️ Hapus Terpilih", width=140, height=34, corner_radius=8,
                      fg_color="#c0392b", hover_color="#e74c3c", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.delete_selected_files).pack(side="left", padx=4)
        ctk.CTkButton(self.file_actions, text="🌐 Buka Web Preview HTML", width=180, height=34, corner_radius=8,
                      fg_color="#2980b9", hover_color="#3498db", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self.open_preview_file).pack(side="right", padx=0)

        # Table container
        self.file_tree_container = ctk.CTkFrame(self.file_frame, fg_color="#16161A", corner_radius=12, border_width=1, border_color="#2a2a32")
        self.file_tree_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.file_tree_container.grid_columnconfigure(0, weight=1)
        self.file_tree_container.grid_rowconfigure(0, weight=1)

        # Table
        columns = ("No", "Nama File", "Ukuran", "Path")
        self.file_tree = ttk.Treeview(self.file_tree_container, columns=columns, show="tree headings", selectmode="extended", style="DB.Treeview")

        # Tree column (#0) for Category grouping
        self.file_tree.heading("#0", text="📁 Kategori / Folder")
        self.file_tree.column("#0", width=200, minwidth=150)

        self.file_tree.heading("No", text="#")
        self.file_tree.heading("Nama File", text="📄 Nama File MD")
        self.file_tree.heading("Ukuran", text="📏 Ukuran")
        self.file_tree.heading("Path", text="Path Lengkap")

        self.file_tree.column("No", width=50, minwidth=40, anchor="center")
        self.file_tree.column("Nama File", width=400, minwidth=200)
        self.file_tree.column("Ukuran", width=100, minwidth=80, anchor="center")
        self.file_tree.column("Path", width=0, stretch=False)

        # Scrollbars
        self.file_vscroll = ttk.Scrollbar(self.file_tree_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.file_vscroll.set)

        self.file_tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(8, 8))
        self.file_vscroll.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 4))

    def load_file_data(self):
        for item in self.file_tree.get_children(): self.file_tree.delete(item)
        base_dir = "hasil_md"
        if not os.path.exists(base_dir):
            self.file_count_label.configure(text="— Folder hasil_md belum ada")
            return
            
        categories = {} # {cat_name: [list of files]}
        total_files = 0
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    category = os.path.basename(root)
                    if category == "hasil_md": category = "Uncategorized"
                    size_kb = os.path.getsize(full_path) / 1024
                    
                    if category not in categories: categories[category] = []
                    categories[category].append((file, f"{size_kb:.1f} KB", full_path))
                    total_files += 1
                    
        # Insert parents and children
        idx = 1
        for cat in sorted(categories.keys()):
            # Parent item (Category)
            parent_id = self.file_tree.insert("", "end", text=f" {cat}", values=("", f"({len(categories[cat])} item)", "", ""), open=False)
            
            # Child items (Files)
            for file_data in sorted(categories[cat], key=lambda x: x[0]):
                tag = "even" if idx % 2 == 0 else "odd"
                self.file_tree.insert(parent_id, "end", text="", values=(idx, file_data[0], file_data[1], file_data[2]), tags=(tag,))
                idx += 1
            
        self.file_count_label.configure(text=f"— {total_files} file")

    def delete_selected_files(self):
        selected = self.file_tree.selection()
        if not selected:
            self.log("⚠️ Pilih file yang ingin dihapus terlebih dahulu.")
            return
            
        dialog = ctk.CTkInputDialog(text=f"Hapus {len(selected)} file markdown secara permanen?\nKetik 'ya' untuk konfirmasi:", title="Konfirmasi Hapus File")
        result = dialog.get_input()
        if result and result.lower() == "ya":
            deleted_count = 0
            for item in selected:
                vals = self.file_tree.item(item, "values")
                if vals and len(vals) > 4:
                    file_path = vals[4]
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_count += 1
                    except Exception as e:
                        self.log(f"❌ Gagal menghapus {vals[2]}: {e}")
            
            self.log(f"🗑️ {deleted_count} file berhasil dihapus.")
            self.load_file_data()

    def open_preview_file(self):
        if os.path.exists("preview.html"): webbrowser.open("file://" + os.path.abspath("preview.html"))
        else: self.log("⚠️ File preview.html tidak ditemukan. Jalankan Generate Site terlebih dahulu.")

    def create_sidebar_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, height=40, fg_color="transparent", anchor="w", command=command); btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
    def create_action_button(self, text, command, row, col):
        btn = ctk.CTkButton(self.controls_frame, text=text, height=50, fg_color=self.orange_color, hover_color=self.orange_hover, font=ctk.CTkFont(size=14, weight="bold"), command=command); btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew"); self.controls_frame.grid_columnconfigure(col, weight=1)
    def log(self, message): self.console_text.configure(state="normal"); self.console_text.insert("end", message + "\n"); self.console_text.see("end"); self.console_text.configure(state="disabled")
    def run_script(self, script_name, full_params=None):
        self.log(f"\n🚀 Executing {script_name}...")
        params = full_params if full_params else {"keyword": self.keyword_entry.get().strip(), "category": self.category_entry.get().strip(), "pages": self.pages_entry.get().strip()}
        threading.Thread(target=self._execute_subprocess, args=(script_name, params), daemon=True).start()
    def _execute_subprocess(self, script_name, params):
        python_path, script_path = sys.executable, os.path.join("modules", script_name)
        cmd = [python_path, script_path, "--gui"]
        for k in ["keyword", "category", "pages", "max-urls", "target-keyword"]:
            if params.get(k.replace("-","_")): cmd.extend([f"--{k}", params[k.replace("-","_")]])
        if params.get("force"): cmd.append("--force")
        if script_name == "scrape_links.py":
            cmd.extend(["--sort", params.get("sort", "3"), "--location", params.get("location", "1")])
            if params.get("rating"): cmd.extend(["--rating", params["rating"]])
        
        # Suppress Node.js deprecation warnings from Playwright
        env = os.environ.copy()
        env["NODE_OPTIONS"] = "--no-deprecation"
        env["PYTHONUNBUFFERED"] = "1"
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, env=env)
            for line in process.stdout: self.after(0, self.log, line.strip())
            process.wait(); self.after(0, lambda: self.log(f"✅ Finished {script_name}"))
        except Exception as e: self.after(0, lambda: self.log(f"⚠️ Error: {str(e)}"))

if __name__ == "__main__": app = ShopeeBotGUI(); app.mainloop()
