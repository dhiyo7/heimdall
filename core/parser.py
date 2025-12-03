import re

class HeimdallParser:
    """
    Parser murni yang hanya bertugas membaca file .heim 
    dan mengubahnya menjadi data terstruktur (Dictionary).
    Eksekusi dilakukan oleh main.py.
    """
    def __init__(self, driver):
        self.driver = driver

    def parse_file(self, file_path):
        current_feature = "Default Feature"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 1. Skip baris kosong atau komentar biasa
                if not line or (line.startswith("#") and not "FITUR" in line.upper() and not "FEATURE" in line.upper()):
                    continue
                
                # 2. Deteksi Fitur Cluster
                if line.upper().startswith("# FITUR:") or line.upper().startswith("# FEATURE:"):
                    # Ambil nama fitur setelah titik dua
                    try:
                        feature_name = line.split(":", 1)[1].strip()
                        current_feature = feature_name
                        # Kirim sinyal ke main.py bahwa fitur berubah
                        yield {"type": "feature", "name": feature_name}
                    except:
                        pass
                    continue
                
                # 3. Parsing Perintah (Command)
                # Kita gunakan split('"') karena syntax kita konsisten pakai tanda kutip
                parts = line.split('"')
                
                # Pastikan baris memiliki setidaknya satu argumen dalam kutip
                if len(parts) < 2:
                    continue

                # --- MAPPING PERINTAH ---
                
                if line.startswith('Buka aplikasi'):
                    # Syntax: Buka aplikasi "com.package"
                    pkg = parts[1]
                    yield {
                        "type": "action", 
                        "cmd": "open_app", 
                        "args": [pkg], 
                        "desc": line, 
                        "feature": current_feature
                    }
                
                elif line.startswith('Ketik'):
                    # Syntax: Ketik "text" pada kolom "label"
                    if len(parts) >= 4:
                        text = parts[1]
                        label = parts[3]
                        yield {
                            "type": "action", 
                            "cmd": "input_text", 
                            "args": [text, label], 
                            "desc": line, 
                            "feature": current_feature
                        }

                elif line.startswith('Ketuk tombol'):
                    # Syntax: Ketuk tombol "Label"
                    label = parts[1]
                    yield {
                        "type": "action", 
                        "cmd": "click", 
                        "args": [label], 
                        "desc": line, 
                        "feature": current_feature
                    }

                elif line.startswith('Tunggu sampai muncul'):
                    # Syntax: Tunggu sampai muncul teks "Label"
                    label = parts[1]
                    yield {
                        "type": "action", 
                        "cmd": "wait", 
                        "args": [label], 
                        "desc": line, 
                        "feature": current_feature
                    }

                elif line.startswith('Pastikan muncul'):
                    # Syntax: Pastikan muncul teks "Label"
                    label = parts[1]
                    yield {
                        "type": "action", 
                        "cmd": "assert", 
                        "args": [label], 
                        "desc": line, 
                        "feature": current_feature
                    }

                elif line.startswith('Gulir ke'):
                    # Syntax: Gulir ke "Bawah"
                    direction = parts[1]
                    yield {
                        "type": "action", 
                        "cmd": "scroll", 
                        "args": [direction], 
                        "desc": line, 
                        "feature": current_feature
                    }