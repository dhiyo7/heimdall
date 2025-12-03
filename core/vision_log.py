import subprocess
import re
import threading
import time

class LogSniffer:
    def __init__(self):
        self.logs = []
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        subprocess.run(["adb", "logcat", "-c"]) # Clear logs
        self.thread = threading.Thread(target=self._sniff)
        self.thread.daemon = True
        self.thread.start()

    def _sniff(self):
        process = subprocess.Popen(
            ["adb", "logcat", "-v", "time"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='ignore'
        )

        # Regex yang lebih toleran untuk OkHttp
        # Menangkap "<-- 200" atau "<-- 500" atau "HTTP 200"
        status_pattern = re.compile(r'<--\s+(\d{3})') 
        
        # Regex URL
        url_pattern = re.compile(r'-->\s+(GET|POST|PUT|DELETE)\s+(http[^\s]+)')

        while not self.stop_event.is_set():
            line = process.stdout.readline()
            if not line: break
            
            # 1. Cek URL Request
            url_match = url_pattern.search(line)
            if url_match:
                method = url_match.group(1)
                full_url = url_match.group(2)
                # Ambil path doang biar pendek
                endpoint = "/" + "/".join(full_url.split('/')[3:]) 
                self.logs.append({"method": method, "endpoint": endpoint, "status": "-"}) # Default status strip

            # 2. Cek Status Response
            status_match = status_pattern.search(line)
            if status_match:
                code = status_match.group(1)
                # Jika ada request sebelumnya yang statusnya masih "-", update statusnya
                if self.logs and self.logs[-1]["status"] == "-":
                    self.logs[-1]["status"] = code

    def get_recent_logs(self):
        captured = self.logs[:]
        self.logs = [] # Reset buffer
        return captured

    def stop(self):
        self.stop_event.set()