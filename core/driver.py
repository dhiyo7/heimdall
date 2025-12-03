import uiautomator2 as u2
from uiautomator2.exceptions import UiObjectNotFoundError
import time

class HeimdallDriver:
    """
    A wrapper for uiautomator2 to provide robust element finding for Heimdall.
    Implements 'Hierarchy Fallback', 'Smart Scroll', and 'Native Typing'.
    """
    def __init__(self, device_serial=None):
        self.d = u2.connect(device_serial)
        # Set implicit wait agar tidak buru-buru error (default 20s)
        self.d.implicitly_wait(10.0)

    def find_element_robust(self, selector: str) -> u2.UiObject:
        """
        Mencari elemen dengan urutan strategi:
        1. ID
        2. Text (Contains - Partial Match)
        3. Description (Contains)
        
        Jika gagal, lakukan Scroll (Swipe Up) dan coba lagi hingga 3x.
        """
        for i in range(4):  # 1 attempt awal + 3 kali scroll
            # 1. Resource ID Check
            if self.d(resourceId=selector).exists:
                return self.d(resourceId=selector)

            # 2. Text Check (Prioritaskan Exact, lalu Contains)
            if self.d(text=selector).exists:
                return self.d(text=selector)
            if self.d(textContains=selector).exists:
                return self.d(textContains=selector)

            # 3. Content Description Check
            if self.d(descriptionContains=selector).exists:
                return self.d(descriptionContains=selector)

            # Jika belum ketemu dan masih punya nyawa scroll
            if i < 3:
                print(f"  [Heimdall Vision] '{selector}' not visible. Scrolling down... ({i+1}/3)")
                self.scroll_down_coordinate()
        
        # Jika sudah menyerah
        raise UiObjectNotFoundError({'message': f"Element '{selector}' not found after 3 scrolls."})

    def scroll_down_coordinate(self):
        """
        Melakukan swipe di area ATAS layar agar aman dari Keyboard.
        Swipe dari Tengah (50%) ke Atas (20%).
        """
        w, h = self.d.window_size()
        
        # PENTING: Kita swipe di paruh atas layar (0.5 ke 0.2)
        # Agar tidak tidak sengaja menyentuh keyboard yang muncul di bawah
        print("  [Heimdall] Performing Safe-Scroll (Top Half)...")
        self.d.swipe(w * 0.5, h * 0.5, w * 0.5, h * 0.2, duration=0.5)
        
        time.sleep(1.5) # Beri waktu lebih untuk animasi & layout refresh

    def input_text_on_field(self, text: str, label: str):
        print(f"Action: Typing '{text}'...")

        # --- [STRATEGI BARU: BY INDEX / URUTAN] ---
        # Jika script bilang: pada kolom "urutan 1"
        if "urutan" in label.lower():
            import re
            # Ambil angka dari teks label (misal "urutan 1" -> 1)
            match = re.search(r'\d+', label)
            if match:
                # Kurangi 1 karena komputer mulai dari 0 (User bilang 1 = Index 0)
                idx = int(match.group()) - 1
                print(f"  > Mode Urutan Aktif: Menargetkan EditText ke-{idx + 1}")
                
                target_element = self.d(className="android.widget.EditText", instance=idx)
                if not target_element.exists:
                     raise UiObjectNotFoundError({'message': f"Input field urutan ke-{idx+1} tidak ditemukan!"})
                
                self._execute_typing(target_element, text)
                return
        # ------------------------------------------

        # ... (Logika Label/Placeholder lama tetap ada di bawah ini untuk backup) ...
        
        # A. Cari Titik Acuan (Label atau Placeholder text)
        try:
            label_ui = self.find_element_robust(label)
        except UiObjectNotFoundError:
            # Fallback terakhir: Coba cari EditText yang mengandung text label tersebut
            fallback = self.d(className="android.widget.EditText", textContains=label)
            if fallback.exists:
                self._execute_typing(fallback, text)
                return
            raise UiObjectNotFoundError({'message': f"Label/Placeholder '{label}' not found."})

        # B. Deteksi Target Elemen (Strategi Relative)
        target_element = None
        
        if label_ui.down(className="android.widget.EditText").exists:
            target_element = label_ui.down(className="android.widget.EditText")
        elif label_ui.right(className="android.widget.EditText").exists:
            target_element = label_ui.right(className="android.widget.EditText")
        else:
            # Asumsi Placeholder
            target_element = label_ui

        # C. Eksekusi
        self._execute_typing(target_element, text)

    def _execute_typing(self, element, text):
        """
        Helper private untuk mengetik dan MEMBUNUH Keyboard/Fokus setelahnya.
        """
        # 1. Klik & Tunggu Fokus
        element.click()
        time.sleep(0.5) 

        # 2. Ketik Teks (ADB Shell - Safe Method)
        safe_text = text.replace(" ", "%s")
        try:
            self.d.shell(f"input text {safe_text}")
        except:
            element.send_keys(text)
        
        time.sleep(0.5)

        # ====================================================
        # STRATEGI: KEYBOARD KILLER & FOCUS REMOVER
        # ====================================================
        print("  > Force-Closing Keyboard & Clearing Focus...")

        # Langkah A: Tekan ENTER (Seringkali otomatis menutup keyboard/pindah field)
        self.d.press("enter")
        time.sleep(0.3)

        # Langkah B: Tekan BACK (ADB Shell) - Lakukan 2x !
        # Back pertama: Tutup Suggestion Bar (jika ada)
        self.d.shell("input keyevent 4") 
        time.sleep(0.3)
        # Back kedua: Tutup Keyboard utama (jika masih bandel)
        self.d.shell("input keyevent 4") 
        
        # Langkah C: KLIK AREA NETRAL (Penting!)
        # Kita klik bagian atas layar (Logo/Judul) untuk mematikan fokus dari form.
        # Koordinat: Tengah Lebar (50%), Atas Tinggi (10% - 15%)
        w, h = self.d.window_size()
        # Klik di area aman (biasanya logo atau teks 'Selamat Datang')
        self.d.click(w * 0.5, h * 0.15)
        
        print("  > Keyboard closed & focus cleared. Ready for next step.")
        time.sleep(1.5) # Wajib jeda agar UI 'turun' dan tombol Masuk terlihat

    def get_current_activity(self) -> str:
        """Mengambil nama activity aktif untuk reporting"""
        try:
            return self.d.app_current()['activity']
        except:
            return "Unknown"

    def take_screenshot(self, path: str):
        self.d.screenshot(path)