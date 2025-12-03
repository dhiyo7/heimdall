import uiautomator2 as u2
from uiautomator2.exceptions import UiObjectNotFoundError
import time

class HeimdallDriver:
    def __init__(self, device_serial=None):
        self.d = u2.connect(device_serial)
        self.d.implicitly_wait(10.0)
        
        # [JURUS 1] Aktifkan Keyboard Hantu (FastInputIME)
        # Mencegah keyboard visual muncul -> Mencegah tombol 'Next' -> Mencegah Looping.
        print("  [Init] Enabling FastInputIME (Ghost Keyboard)...")
        self.d.set_fastinput_ime(True)

    def find_element_robust(self, selector: str):
        """
        Mencari elemen dengan strategi bertingkat.
        Juga menangani 'Virtual Element' seperti FAB.
        """
        # --- [JURUS FAB: KOORDINAT POJOK KANAN BAWAH] ---
        # Bagian ini yang TADI HILANG. Kita kembalikan lagi.
        if selector.upper() in ["FAB", "FLOATING ACTION BUTTON", "TOMBOL TAMBAH"]:
            print("  [Heimdall] Target is FAB. Using coordinate strategy.")
            return VirtualFAB(self.d)
        # -----------------------------------------------

        for i in range(4):
            if self.d(resourceId=selector).exists: return self.d(resourceId=selector)
            if self.d(text=selector).exists: return self.d(text=selector)
            if self.d(textContains=selector).exists: return self.d(textContains=selector)
            if self.d(descriptionContains=selector).exists: return self.d(descriptionContains=selector)

            if i < 3:
                print(f"  [Heimdall Vision] '{selector}' not visible. Scrolling down... ({i+1}/3)")
                self.scroll_down_coordinate()
        
        raise UiObjectNotFoundError({'message': f"Element '{selector}' not found after 3 scrolls."})

    def scroll_down_coordinate(self):
        """
        Safe scroll di area tengah ke atas agar tidak kena keyboard (jika ada).
        """
        w, h = self.d.window_size()
        # Swipe dari Tengah (50%) ke Atas (20%)
        self.d.swipe(w * 0.5, h * 0.5, w * 0.5, h * 0.2, duration=0.5)
        time.sleep(1.0)

    def input_text_on_field(self, text: str, label: str):
        """Input teks dengan penanganan fokus yang ketat."""
        print(f"Action: Typing '{text}'...")

        # Pastikan tidak ada sisa keyboard/fokus liar sebelum mulai
        self.d.shell("input keyevent 111") 

        # STRATEGI URUTAN (INDEX)
        if "urutan" in label.lower():
            import re
            match = re.search(r'\d+', label)
            if match:
                idx = int(match.group()) - 1
                # Cari ulang elemen setelah keyboard cleaning
                target = self.d(className="android.widget.EditText", instance=idx)
                if target.exists:
                    self._execute_typing(target, text)
                    return

        # STRATEGI LABEL
        try:
            label_ui = self.find_element_robust(label)
        except UiObjectNotFoundError:
            # Fallback cari EditText yang mengandung teks label (Placeholder)
            fallback = self.d(className="android.widget.EditText", textContains=label)
            if fallback.exists:
                self._execute_typing(fallback, text)
                return
            raise UiObjectNotFoundError({'message': f"Label '{label}' not found."})

        # Logic Relative Position
        target = None
        if label_ui.down(className="android.widget.EditText").exists:
            target = label_ui.down(className="android.widget.EditText")
        elif label_ui.right(className="android.widget.EditText").exists:
            target = label_ui.right(className="android.widget.EditText")
        else:
            target = label_ui # Asumsi placeholder

        self._execute_typing(target, text)

    def _execute_typing(self, element, text):
        """
        Mengetik dan MEMASTIKAN keyboard mati total (Anti-Looping Emulator).
        """
        # 1. KLIK UNTUK FOKUS
        element.click()
        time.sleep(0.5)
        
        # 2. KETIK VIA ADB (Bypass Security & Keyboard UI)
        safe_text = text.replace(" ", "%s")
        try:
            self.d.shell(f"input text {safe_text}")
        except:
            element.send_keys(text)
        
        time.sleep(0.5)

        # 3. [JURUS 2] MATIKAN PAKSA (Dismiss)
        # Gunakan ESC (111) karena ini paling ampuh di Emulator untuk kill focus
        # tanpa memicu tombol 'Next'.
        print("  > Input finished. Dismissing UI with ESC (111)...")
        self.d.shell("input keyevent 111")
        
        # Backup: Tekan Back sekali lagi jika ESC gagal
        time.sleep(0.2)
        self.d.press("back")
        
        # Jeda agar UI stabil dan tombol Masuk terlihat
        time.sleep(1.0)

    def get_current_activity(self) -> str:
        try: return self.d.app_current()['activity']
        except: return "Unknown"

    def take_screenshot(self, path: str):
        self.d.screenshot(path)

    def stop_driver(self):
        """
        Membersihkan sesi dan mengembalikan Keyboard Asli HP.
        Wajib dipanggil di akhir tes!
        """
        print("  [Teardown] Disabling FastInputIME (Restoring Original Keyboard)...")
        self.d.set_fastinput_ime(False) 

# --- CLASS TAMBAHAN: TOMBOL VIRTUAL ---
class VirtualFAB:
    """
    Objek palsu untuk klik FAB tanpa Selector.
    Diset khusus untuk Floating Button di atas Bottom Nav.
    """
    def __init__(self, d):
        self.d = d

    def click(self):
        w, h = self.d.window_size()
        
        # --- UPDATE KOORDINAT ---
        # X = 85% (Tetap di kanan)
        # Y = 80% (NAIKKAN DARI 88% KE 80%)
        # Alasannya: 88% kena Bottom Navigation Bar. FAB ada di atasnya.
        x = w * 0.85
        y = h * 0.80
        
        print(f"  [VirtualFAB] Tapping coordinates: ({x}, {y}) - Adjusted High")
        self.d.click(x, y)
        time.sleep(1.5) # Tunggu animasi menu terbuka (FAB biasanya ada animasi memutar)
        
    def exists(self):
        return True