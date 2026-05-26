import os
import sys
import subprocess
import argparse

def get_web_dir():
    # Get absolute path to the shoppe/web_dashboard directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "web_dashboard")

def run_command(cmd, cwd, desc):
    print(f"🚀 Menjalankan: {desc}...")
    try:
        # Use shell=True on Windows, standard list on Unix
        import platform
        use_shell = platform.system() == "Windows"
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=use_shell
        )
        
        for line in process.stdout:
            print(line.strip())
                
        process.wait()
        rc = process.returncode
        if rc == 0:
            print(f"✅ {desc} BERHASIL!")
            return True
        else:
            print(f"❌ {desc} GAGAL dengan kode status: {rc}")
            return False
    except Exception as e:
        print(f"❌ {desc} ERROR: {str(e)}")
        return False

def setup_web():
    web_dir = get_web_dir()
    print(f"📂 Direktori web: {web_dir}")
    
    # 1. Run npm install
    npm_cmd = ["npm", "install"]
    success = run_command(npm_cmd, web_dir, "npm install (Instalasi Dependensi)")
    if not success:
        return False
        
    # 2. Run sync database
    sync_cmd = ["node", "scripts/sync.js"]
    success = run_command(sync_cmd, web_dir, "node sync.js (Sinkronisasi Database SQLite)")
    return success

def sync_database():
    web_dir = get_web_dir()
    sync_cmd = ["node", "scripts/sync.js"]
    return run_command(sync_cmd, web_dir, "node sync.js (Sinkronisasi Database SQLite)")

def main():
    parser = argparse.ArgumentParser(description="ShopeeBot Next.js Web Runner Integration")
    parser.add_argument("action", choices=["setup", "sync"], help="Aksi yang akan dijalankan")
    args = parser.parse_args()

    if args.action == "setup":
        success = setup_web()
        sys.exit(0 if success else 1)
    elif args.action == "sync":
        success = sync_database()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
