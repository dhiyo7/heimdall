import re

class StateManager:
    """
    The Brain of Heimdall.
    Berfungsi ganda:
    1. Mencatat Rute Activity (untuk Mindmap).
    2. Menyimpan Variabel Global (untuk Data Passing).
    """

    def __init__(self):
        # --- BAGIAN 1: MEMORI VARIABEL (BARU) ---
        self.variables = {}

        # --- BAGIAN 2: TRACKING ACTIVITY (LAMA) ---
        self.activity_path = []
        self.last_activity = None

    # ==========================================
    # FITUR MEMORI (Variable Storage)
    # ==========================================
    def set_variable(self, key, value):
        """Menyimpan data ke memori. Contoh: {Total} = 50000"""
        clean_key = key.replace("{", "").replace("}", "")
        self.variables[clean_key] = str(value)
        print(f"  🧠 [Memory] Disimpan: {{{clean_key}}} = '{value}'")

    def get_variable(self, key):
        """Mengambil data dari memori."""
        clean_key = key.replace("{", "").replace("}", "")
        return self.variables.get(clean_key, None)

    def resolve_text(self, text):
        """
        Magic Function! Mengganti placeholder {Var} dengan nilai aslinya.
        Contoh input: "Harga {Total}" -> Output: "Harga 50000"
        """
        if not isinstance(text, str):
            return text

        # Cari pola {...}
        matches = re.findall(r'\{(.*?)\}', text)
        
        resolved_text = text
        for key in matches:
            if key in self.variables:
                val = self.variables[key]
                resolved_text = resolved_text.replace(f"{{{key}}}", val)
                
        return resolved_text

    # ==========================================
    # FITUR TRACKING (Untuk Mindmap)
    # ==========================================
    def update_activity(self, activity_name: str):
        """Update posisi activity saat ini."""
        if activity_name and activity_name != self.last_activity:
            simple_name = activity_name.split('.')[-1]
            self.activity_path.append(simple_name)
            self.last_activity = activity_name
            # print(f"  [State] Activity changed to: {simple_name}")

    def get_path(self) -> list:
        """Mengambil history perjalanan."""
        return self.activity_path