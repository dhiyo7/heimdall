import streamlit.web.cli as stcli
import os, sys
import main  # Import logic utama kita

def resolve_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

if __name__ == "__main__":
    # --- MODE KULI (WORKER) ---
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        sys.argv.pop(0) 
        sys.argv[0] = "main.py"
        print("🤖 Worker Process Started...")
        main.main()
    
    # --- MODE BOS (DASHBOARD) ---
    else:
        app_path = resolve_path("app.py")
        
        # [FIX] CONFIGURATION FLAGS
        sys.argv = [
            "streamlit",
            "run",
            app_path,
            "--global.developmentMode=false",
            "--server.fileWatcherType=none",  # <--- INI SOLUSI INOTIFY ERROR
            "--browser.gatherUsageStats=false", # Matikan telemetri biar ringan
        ]
        
        print(f"🚀 Launching Heimdall Dashboard...")
        sys.exit(stcli.main())