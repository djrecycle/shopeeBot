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

class ShopeeBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ShopeeBot Automation Control Panel")
        self.geometry("1100x850")

        # Color Configuration
        self.orange_color = "#EE4D2D"
        self.orange_hover = "#D73211"
        self.bg_color = "#0f0f12"
        self.sidebar_color = "#19191e"
        
        # Grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛍️ ShopeeBot", 
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color=self.orange_color)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.sub_label = ctk.CTkLabel(self.sidebar_frame, text="Automation Tools", 
                                       font=ctk.CTkFont(size=12), text_color="gray")
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Sidebar buttons
        self.btn_dashboard = self.create_sidebar_button("🏠 Dashboard", self.show_dashboard, row=2)
        self.btn_view_db = self.create_sidebar_button("📊 Lihat Database", self.show_database_view, row=3)
        self.btn_generate = self.create_sidebar_button("🌐 Generate Site", lambda: self.run_script("generate_site.py"), row=4)
        self.btn_open_html = self.create_sidebar_button("📂 Buka Preview", self.open_preview_file, row=5)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Theme:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # Main Content Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(self.main_frame, text="Automation Control Panel", 
                                         font=ctk.CTkFont(size=22, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        # Create frames for different views
        self.create_home_view()
        self.create_database_view()

        # Show default view
        self.show_dashboard()

        # Status Bar
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30, corner_radius=0, fg_color="#19191e")
        self.status_frame.grid(row=2, column=0, sticky="ew")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: Ready", font=ctk.CTkFont(size=11))
        self.status_label.pack(side="left", padx=20)

    def create_home_view(self):
        self.home_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)

        # Input Parameters Area
        self.inputs_frame = ctk.CTkFrame(self.home_frame, fg_color="#19191e", corner_radius=10)
        self.inputs_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew", padx=40)
        self.inputs_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.keyword_label = ctk.CTkLabel(self.inputs_frame, text="Keyword / URL Toko:", font=ctk.CTkFont(size=12, weight="bold"))
        self.keyword_label.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        self.keyword_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Contoh: Senar Gitar", height=35)
        self.keyword_entry.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.category_label = ctk.CTkLabel(self.inputs_frame, text="Kategori (Folder):", font=ctk.CTkFont(size=12, weight="bold"))
        self.category_label.grid(row=0, column=1, padx=20, pady=(15, 0), sticky="w")
        self.category_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Contoh: Musik", height=35)
        self.category_entry.grid(row=1, column=1, padx=20, pady=(5, 15), sticky="ew")

        self.pages_label = ctk.CTkLabel(self.inputs_frame, text="Jumlah Halaman:", font=ctk.CTkFont(size=12, weight="bold"))
        self.pages_label.grid(row=0, column=2, padx=20, pady=(15, 0), sticky="w")
        self.pages_entry = ctk.CTkEntry(self.inputs_frame, placeholder_text="Default: 1", height=35)
        self.pages_entry.grid(row=1, column=2, padx=20, pady=(5, 15), sticky="ew")

        # Control Buttons Area
        self.controls_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew", padx=40)
        
        self.btn_login = self.create_action_button("🔑 Login", lambda: self.run_script("open_browser.py"), 0, 0)
        self.btn_scrape_links = self.create_action_button("🔗 Link Scraper", lambda: self.run_script("scrape_links.py"), 0, 1)
        self.btn_scrape_products = self.create_action_button("📦 Product Scraper", lambda: self.run_script("shoppescrap.py"), 0, 2)
        self.btn_send_msg = self.create_action_button("💬 Messenger", lambda: self.run_script("send_message.py"), 0, 3)

        # Console Output
        self.console_label = ctk.CTkLabel(self.home_frame, text="Real-Time Activity Console", 
                                          font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.console_label.grid(row=2, column=0, pady=(10, 5), sticky="w", padx=40)

        self.console_text = ctk.CTkTextbox(self.home_frame, corner_radius=10, 
                                           fg_color="#1e1e24", text_color="#27ae60", 
                                           font=ctk.CTkFont(family="Courier", size=13))
        self.console_text.grid(row=3, column=0, sticky="nsew", pady=(0, 20), padx=40)
        self.console_text.insert("0.0", ">>> ShopeeBot GUI initialized.\n>>> Masukkan parameter di atas lalu klik tombol aksi.\n")
        self.console_text.configure(state="disabled")

    def create_database_view(self):
        self.database_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.database_frame.grid_columnconfigure(0, weight=1)
        self.database_frame.grid_rowconfigure(1, weight=1)

        # Top Bar for Database View
        self.db_controls = ctk.CTkFrame(self.database_frame, fg_color="transparent")
        self.db_controls.grid(row=0, column=0, pady=(0, 10), sticky="ew", padx=40)
        
        self.btn_refresh_db = ctk.CTkButton(self.db_controls, text="🔄 Refresh Data", width=120, 
                                            fg_color="#27ae60", hover_color="#219150", 
                                            command=self.load_table_data)
        self.btn_refresh_db.pack(side="left", padx=5)

        # Style for Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#1e1e24", 
                        foreground="white", 
                        fieldbackground="#1e1e24", 
                        rowheight=30)
        style.map("Treeview", background=[('selected', self.orange_color)])
        style.configure("Treeview.Heading", background="#19191e", foreground="white", relief="flat", font=('Arial', 10, 'bold'))

        # Frame for treeview and scrollbar
        self.tree_frame = ctk.CTkFrame(self.database_frame, fg_color="#1e1e24", corner_radius=10)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 20))

        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=("Kategori", "Keyword", "Link", "Rating", "Status"), show="headings")
        
        self.tree.heading("Kategori", text="Kategori")
        self.tree.heading("Keyword", text="Keyword")
        self.tree.heading("Link", text="Link Produk")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Status", text="Status Chat")

        self.tree.column("Kategori", width=120, anchor="center")
        self.tree.column("Keyword", width=120, anchor="center")
        self.tree.column("Link", width=450)
        self.tree.column("Rating", width=80, anchor="center")
        self.tree.column("Status", width=120, anchor="center")

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

    def show_dashboard(self):
        self.header_label.configure(text="ShopeeBot Dashboard")
        self.database_frame.grid_forget()
        self.home_frame.grid(row=1, column=0, sticky="nsew")
        self.log(">>> Halaman Dashboard Aktif")

    def show_database_view(self):
        self.header_label.configure(text="Database Hasil Scrape")
        self.home_frame.grid_forget()
        self.database_frame.grid(row=1, column=0, sticky="nsew")
        self.load_table_data()
        self.log(">>> Halaman Database Aktif")

    def open_preview_file(self):
        preview_file = "preview.html"
        if os.path.exists(preview_file):
            file_url = "file://" + os.path.abspath(preview_file)
            self.log(f"🚀 Membuka {preview_file} di browser...")
            webbrowser.open(file_url)
        else:
            self.log("⚠️ File preview.html tidak ditemukan. Klik 'Generate Site' terlebih dahulu.")

    def load_table_data(self):
        csv_path = "shopee_links.csv"
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not os.path.exists(csv_path):
            self.log("⚠️ File shopee_links.csv tidak ditemukan!")
            return

        try:
            df = pd.read_csv(csv_path)
            for index, row in df.iterrows():
                self.tree.insert("", "end", values=(
                    row.get("Kategori", "-"),
                    row.get("Keyword", "-"),
                    row.get("Link Produk", "-"),
                    row.get("Rating", "-"),
                    row.get("Status Chat", "-")
                ))
            self.log(f"✅ Berhasil memuat {len(df)} data ke tabel.")
        except Exception as e:
            self.log(f"❌ Gagal memuat data tabel: {e}")

    def create_sidebar_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, corner_radius=8, height=40,
                            fg_color="transparent", text_color=("gray10", "gray90"),
                            hover_color=("gray70", "gray30"), anchor="w",
                            font=ctk.CTkFont(size=14), command=command)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        return btn

    def create_action_button(self, text, command, row, col):
        btn = ctk.CTkButton(self.controls_frame, text=text, corner_radius=8, height=50,
                            fg_color=self.orange_color, hover_color=self.orange_hover,
                            font=ctk.CTkFont(size=14, weight="bold"), command=command)
        btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        self.controls_frame.grid_columnconfigure(col, weight=1)
        return btn

    def log(self, message):
        self.console_text.configure(state="normal")
        self.console_text.insert("end", message + "\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def update_status(self, text):
        self.status_label.configure(text=f"Status: {text}")

    def run_script(self, script_name):
        self.log(f"\n🚀 Executing {script_name}...")
        self.update_status(f"Running {script_name}...")
        
        params = {
            "keyword": self.keyword_entry.get().strip(),
            "category": self.category_entry.get().strip(),
            "pages": self.pages_entry.get().strip()
        }
        
        thread = threading.Thread(target=self._execute_subprocess, args=(script_name, params))
        thread.daemon = True
        thread.start()

    def _execute_subprocess(self, script_name, params):
        if hasattr(sys, '_MEIPASS'):
            cmd = [sys.executable, "--run-script", script_name]
        else:
            python_path = os.path.join(os.getcwd(), "venv", "bin", "python")
            if not os.path.exists(python_path):
                python_path = sys.executable
            
            script_path = os.path.join("modules", script_name)
            cmd = [python_path, script_path, "--gui"]
            
            if params["keyword"]:
                cmd.extend(["--keyword", params["keyword"]])
            if params["category"]:
                cmd.extend(["--category", params["category"]])
            if params["pages"]:
                cmd.extend(["--pages", params["pages"]])

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )

            for line in process.stdout:
                self.after(0, self.log, line.strip())
            
            process.wait()
            if process.returncode == 0:
                self.after(0, lambda: self.log(f"✅ {script_name} finished successfully."))
                self.after(0, lambda: self.update_status("Ready"))
            else:
                self.after(0, lambda: self.log(f"❌ {script_name} exited with code {process.returncode}."))
                self.after(0, lambda: self.update_status("Error"))
                
        except Exception as e:
            self.after(0, lambda: self.log(f"⚠️ Error running {script_name}: {str(e)}"))
            self.after(0, lambda: self.update_status("Error"))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

def run_worker(script_name):
    """Dispatcher to run the actual script logic."""
    if script_name == "open_browser.py":
        from modules import open_browser
        open_browser.login_shopee()
    elif script_name == "scrape_links.py":
        from modules import scrape_links
        scrape_links.scrape_links()
    elif script_name == "shoppescrap.py":
        from modules import shoppescrap
        shoppescrap.scrape_shopee()
    elif script_name == "send_message.py":
        from modules import send_message
        send_message.send_messages()
    elif script_name == "generate_site.py":
        from modules import generate_site
        generate_site.generate_site()
    else:
        print(f"Unknown script: {script_name}")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--run-script":
        run_worker(sys.argv[2])
    else:
        app = ShopeeBotGUI()
        app.mainloop()
