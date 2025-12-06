import re
import os
import ast

class HeimdallParser:
    """
    Parser Terlengkap (V6.1 - Bugfix Case Sensitivity).
    """
    def __init__(self, driver):
        self.driver = driver

    def parse_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"!!! Error: File tidak ditemukan: {file_path}")
            return
        yield from self._parse_recursive(file_path, "Default Feature")

    def parse_lines(self, lines, parent_feature="Dynamic"):
        state = {
            'in_loop': False, 'loop_var': '', 'loop_data': [], 'loop_buf': [],
            'in_if': False, 'if_cond': '', 'if_buf': []
        }
        for line in lines:
            line = line.strip()
            if not line or (line.startswith("#") and "FITUR" not in line.upper()): continue
            yield from self._process_line(line, parent_feature, state)

    def _parse_recursive(self, file_path, parent_feature):
        if not os.path.exists(file_path): return
        state = {
            'in_loop': False, 'loop_var': '', 'loop_data': [], 'loop_buf': [],
            'in_if': False, 'if_cond': '', 'if_buf': []
        }
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or (line.startswith("#") and "FITUR" not in line.upper()): continue
                yield from self._process_line(line, parent_feature, state)

    def _process_line(self, line, current_feature, state):
        
        # 1. Feature Detection
        if line.upper().startswith("# FITUR:") or line.upper().startswith("# FEATURE:"):
            try:
                fname = line.split(":", 1)[1].strip()
                yield {"type": "feature", "name": fname}
            except: pass
            return

        # ==========================================
        # 2. FITUR CONDITIONAL (JIKA) - [FIXED]
        # ==========================================
        # Kita ubah pengecekan menjadi HURUF BESAR SEMUA agar cocok
        if line.upper().startswith("JIKA MUNCUL TEKS"):
            match = re.search(r'JIKA muncul teks "(.*?)"', line, re.IGNORECASE)
            if match:
                state['if_cond'] = match.group(1)
                state['in_if'] = True 
                state['if_buf'] = []
                return

        if line.upper() == "AKHIR JIKA":
            if state['in_if']:
                state['in_if'] = False
                yield {
                    "type": "conditional",
                    "condition": state['if_cond'],
                    "body": state['if_buf'][:] 
                }
            return

        # Buffer baris jika sedang di dalam blok JIKA
        if state['in_if']:
            state['if_buf'].append(line)
            return
        # ==========================================

        # 3. FITUR LOOPING (ULANGI)
        if line.upper().startswith("ULANGI"):
            try:
                match = re.search(r'ULANGI\s+"(.*?)"\s+DARI\s+(\[.*\])', line, re.IGNORECASE)
                if match:
                    state['loop_var'] = match.group(1)
                    state['loop_data'] = ast.literal_eval(match.group(2))
                    state['in_loop'] = True
                    state['loop_buf'] = []
                    return
            except: pass
        
        if line.upper() == "SELESAI ULANGI":
            if state['in_loop']:
                state['in_loop'] = False
                dataset = state['loop_data']
                var_name = state['loop_var']
                buffer = state['loop_buf']
                for item in dataset:
                    print(f"--- 🔄 Iteration: {item} ---")
                    for buf_line in buffer:
                        injected = buf_line.replace(f"{{{var_name}}}", str(item))
                        yield from self.parse_lines([injected], current_feature)
            return

        if state['in_loop']:
            state['loop_buf'].append(line)
            return

        # 4. Modular Include
        if line.upper().startswith("JALANKAN") or line.upper().startswith("INCLUDE"):
            parts = line.split('"')
            if len(parts) >= 2:
                yield from self._parse_recursive(parts[1], current_feature)
            return

        # 5. Standard Commands
        yield from self._parse_single_line(line, current_feature)

    def _parse_single_line(self, line, current_feature):
        # A. MEMORY
        if line.startswith("SIMPAN teks"):
            match = re.search(r'SIMPAN teks dari "(.*?)" KE "(.*?)"', line)
            if match:
                yield {"type": "action", "cmd": "save_text", "args": [match.group(1), match.group(2)], "desc": line, "feature": current_feature}
            return
        # B. SYSTEM KEYS
        if line.upper().startswith('TEKAN TOMBOL SISTEM'):
            parts = line.split('"')
            if len(parts) >= 2:
                yield {"type": "action", "cmd": "press_key", "args": [parts[1]], "desc": line, "feature": current_feature}
            return
        # C. STANDARD
        parts = line.split('"')
        if len(parts) < 2: return
        if line.startswith('Buka aplikasi'): yield {"type": "action", "cmd": "open_app", "args": [parts[1]], "desc": line, "feature": current_feature}
        elif line.startswith('Ketik'): 
            if len(parts) >= 4: yield {"type": "action", "cmd": "input_text", "args": [parts[1], parts[3]], "desc": line, "feature": current_feature}
        elif line.startswith('Ketuk tombol'): yield {"type": "action", "cmd": "click", "args": [parts[1]], "desc": line, "feature": current_feature}
        elif line.startswith('Tunggu sampai muncul'): yield {"type": "action", "cmd": "wait", "args": [parts[1]], "desc": line, "feature": current_feature}
        elif line.startswith('Pastikan muncul'): yield {"type": "action", "cmd": "assert", "args": [parts[1]], "desc": line, "feature": current_feature}
        elif line.startswith('Gulir ke'): yield {"type": "action", "cmd": "scroll", "args": [parts[1]], "desc": line, "feature": current_feature}