import uiautomator2 as u2
from uiautomator2.exceptions import UiObjectNotFoundError, InputIMEError
import time

class HeimdallDriver:
    def __init__(self, device_serial=None):
        print(f"  [Init] Connecting to {device_serial}...")
        self.d = u2.connect(device_serial)
        self.d.implicitly_wait(10.0)
        
        try:
            print("  [Init] Enabling FastInputIME (Ghost Keyboard)...")
            self.d.set_fastinput_ime(True)
        except Exception:
            print("  ⚠️ Fallback: Menggunakan Keyboard Standar.")
            self.d.set_fastinput_ime(False) 

    # --- JURUS MABUK (SHELL COMMANDS) ---
    def _safe_click(self, x, y):
        try:
            # Coba klik normal dulu (lebih akurat)
            self.d.click(x, y)
        except Exception:
            # Kalau ditolak Security, pakai Shell
            print(f"  ⚠️ [Permission] Menggunakan Shell Tap di ({x}, {y})...")
            self.d.shell(f"input tap {x} {y}")

    def _safe_swipe(self, x1, y1, x2, y2, duration=0.4):
        try:
            self.d.swipe(x1, y1, x2, y2, duration=duration)
        except Exception:
            print("  ⚠️ [Permission] Menggunakan Shell Swipe...")
            ms = int(duration * 1000)
            self.d.shell(f"input swipe {x1} {y1} {x2} {y2} {ms}")

    # --- PENCARIAN PINTAR ---
    def find_element_robust(self, selector: str):
        if selector.upper() in ["FAB", "FLOATING ACTION BUTTON", "TOMBOL TAMBAH"]:
            return VirtualFAB(self.d, self)

        # Loop Scroll & Cari
        for i in range(4):
            # Cek apakah elemen muncul?
            found = None
            if self.d(resourceId=selector).exists: found = self.d(resourceId=selector)
            elif self.d(text=selector).exists: found = self.d(text=selector)
            elif self.d(textContains=selector).exists: found = self.d(textContains=selector)
            elif self.d(descriptionContains=selector).exists: found = self.d(descriptionContains=selector)

            if found:
                return found

            # Jika belum ketemu dan belum limit, Scroll!
            if i < 3:
                print(f"  [Vision] '{selector}' belum terlihat. Scroll ke bawah... ({i+1}/3)")
                self.scroll_down_coordinate()
        
        raise UiObjectNotFoundError({'message': f"Elemen '{selector}' tidak ketemu setelah 3x scroll."})

    # --- FUNGSI BARU: TAP PINTAR ---
    def tap_element(self, selector: str):
        print(f"Action: Mencari & Mengetuk '{selector}'...")
        
        # 1. Cari elemen (Otomatis scroll kalau gak ada)
        element = self.find_element_robust(selector)
        
        # 2. Ambil koordinat tengah elemen
        # (Ini penting biar kita bisa pake Shell Tap)
        try:
            x, y = element.center()
        except:
            # Fallback jika gagal dapat center, ambil dari bounds info
            info = element.info
            bounds = info['bounds']
            x = (bounds['left'] + bounds['right']) // 2
            y = (bounds['top'] + bounds['bottom']) // 2
            
        # 3. Eksekusi Tap Aman
        self._safe_click(x, y)
        time.sleep(1.0) # Jeda stabilisasi

    def scroll_down_coordinate(self):
        w, h = self.d.window_size()
        center_x = w * 0.5
        start_y = h * 0.7 
        end_y   = h * 0.3
        self._safe_swipe(center_x, start_y, center_x, end_y, duration=0.4)
        time.sleep(1.0)

    def input_text_on_field(self, text: str, label: str):
        print(f"Action: Typing '{text}'...")
        try: self.d.shell("input keyevent 111") 
        except: pass

        if "urutan" in label.lower():
            import re
            match = re.search(r'\d+', label)
            if match:
                idx = int(match.group()) - 1
                target = self.d(className="android.widget.EditText", instance=idx)
                if target.exists:
                    self._execute_typing(target, text)
                    return

        try:
            label_ui = self.find_element_robust(label)
        except UiObjectNotFoundError:
            fallback = self.d(className="android.widget.EditText", textContains=label)
            if fallback.exists:
                self._execute_typing(fallback, text)
                return
            raise UiObjectNotFoundError({'message': f"Label '{label}' not found."})

        target = None
        if label_ui.down(className="android.widget.EditText").exists:
            target = label_ui.down(className="android.widget.EditText")
        elif label_ui.right(className="android.widget.EditText").exists:
            target = label_ui.right(className="android.widget.EditText")
        else:
            target = label_ui 

        self._execute_typing(target, text)

    def _execute_typing(self, element, text):
        try:
            x, y = element.center()
            self._safe_click(x, y)
        except:
            element.click()

        time.sleep(0.5)
        safe_text = text.replace(" ", "%s")
        try: self.d.shell(f"input text {safe_text}")
        except: element.send_keys(text) 
        time.sleep(0.5)
        try: self.d.shell("input keyevent 111")
        except: pass
        time.sleep(0.2)
        self.d.press("back")
        time.sleep(1.0)

    def get_current_activity(self) -> str:
        try: return self.d.app_current()['activity']
        except: return "Unknown"

    def take_screenshot(self, path: str):
        try: self.d.screenshot(path)
        except: pass

    def stop_driver(self):
        try: self.d.set_fastinput_ime(False) 
        except: pass

class VirtualFAB:
    def __init__(self, d, driver):
        self.d = d
        self.driver = driver
    def click(self):
        w, h = self.d.window_size()
        x = w * 0.85
        y = h * 0.80
        print(f"  [VirtualFAB] Tapping coordinates: ({x}, {y})")
        self.driver._safe_click(x, y)
        time.sleep(1.5)
    def exists(self): return True