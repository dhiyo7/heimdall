import uiautomator2 as u2
# [FIX] Pastikan baris ini ada!
from uiautomator2.exceptions import UiObjectNotFoundError 
import time

class HeimdallDriver:
    def __init__(self, device_serial=None):
        self.d = u2.connect(device_serial)
        self.d.implicitly_wait(10.0)
        print("  [Init] Enabling FastInputIME (Ghost Keyboard)...")
        self.d.set_fastinput_ime(True)

    def find_element_robust(self, selector: str):
        if selector.upper() in ["FAB", "FLOATING ACTION BUTTON", "TOMBOL TAMBAH"]:
            print("  [Heimdall] Target is FAB. Using coordinate strategy.")
            return VirtualFAB(self.d)

        for i in range(4):
            if self.d(resourceId=selector).exists: return self.d(resourceId=selector)
            if self.d(text=selector).exists: return self.d(text=selector)
            if self.d(textContains=selector).exists: return self.d(textContains=selector)
            if self.d(descriptionContains=selector).exists: return self.d(descriptionContains=selector)

            if i < 3:
                print(f"  [Heimdall Vision] '{selector}' not visible. Scrolling down... ({i+1}/3)")
                self.scroll_down_coordinate()
        
        raise UiObjectNotFoundError({'message': f"Element '{selector}' not found after 3 scrolls."})

    def get_text_from_element(self, selector: str) -> str:
        print(f"Action: Reading text from '{selector}'...")
        try:
            element = self.find_element_robust(selector)
            text = element.info.get('text')
            if not text: text = element.info.get('contentDescription')
            return text if text else ""
        except UiObjectNotFoundError:
            raise UiObjectNotFoundError({'message': f"Cannot read text. Element '{selector}' not found."})

    def scroll_down_coordinate(self):
        w, h = self.d.window_size()
        self.d.swipe(w * 0.5, h * 0.5, w * 0.5, h * 0.2, duration=0.5)
        time.sleep(1.0)

    def input_text_on_field(self, text: str, label: str):
        print(f"Action: Typing '{text}'...")
        self.d.shell("input keyevent 111") 

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
        element.click()
        time.sleep(0.5)
        safe_text = text.replace(" ", "%s")
        try:
            self.d.shell(f"input text {safe_text}")
        except:
            element.send_keys(text)
        time.sleep(0.5)
        print("  > Input finished. Dismissing UI with ESC (111)...")
        self.d.shell("input keyevent 111")
        time.sleep(0.2)
        self.d.press("back")
        time.sleep(1.0)

    def get_current_activity(self) -> str:
        try: return self.d.app_current()['activity']
        except: return "Unknown"

    def take_screenshot(self, path: str):
        self.d.screenshot(path)

    def stop_driver(self):
        print("  [Teardown] Disabling FastInputIME...")
        self.d.set_fastinput_ime(False) 

class VirtualFAB:
    def __init__(self, d):
        self.d = d
    def click(self):
        w, h = self.d.window_size()
        x = w * 0.85
        y = h * 0.80
        print(f"  [VirtualFAB] Tapping coordinates: ({x}, {y})")
        self.d.click(x, y)
        time.sleep(1.5)
    def exists(self): return True