class HeimdallStoryteller:
    """
    Penerjemah kode teknis menjadi bahasa manusia (User POV).
    Digunakan untuk laporan Saga.
    """

    @staticmethod
    def generate_narrative(cmd: str, target: str) -> str:
        """
        Menerjemahkan perintah menjadi cerita.
        
        Args:
            cmd (str): Kode perintah (ex: 'click', 'input_text', 'press_key').
            target (str): Objek yang dimanipulasi (ex: 'Masuk', 'Back', 'Rp 50000').
        
        Returns:
            str: Kalimat narasi bahasa Indonesia.
        """
        target = str(target).strip()

        # 1. BUKA APLIKASI
        if cmd == 'open_app':
            return f"User memulai sesi dengan membuka aplikasi paket '{target}'."
        
        # 2. INPUT TEKS
        if cmd == 'input_text':
            return f"User mengisi data '{target}' pada formulir yang tersedia."

        # 3. KLIK / KETUK (Context Aware)
        if cmd == 'click':
            lower_target = target.lower()
            if 'simpan' in lower_target or 'submit' in lower_target:
                return f"User menyimpan perubahan dengan menekan tombol '{target}'."
            if 'batal' in lower_target or 'cancel' in lower_target:
                return f"User membatalkan aksi dengan menekan tombol '{target}'."
            if 'fab' in lower_target or 'tambah' in lower_target:
                return "User memulai aktivitas baru dengan menekan tombol Tambah (FAB)."
            return f"User memilih menu atau tombol '{target}'."

        # 4. TEKAN TOMBOL SISTEM (BACK, HOME) - [BARU]
        if cmd == 'press_key':
            key = target.lower()
            if 'back' in key:
                return "User menekan tombol Kembali (Back) di perangkat."
            if 'home' in key:
                return "User kembali ke layar utama (Home Screen)."
            if 'enter' in key:
                return "User menekan tombol Enter pada keyboard."
            return f"User menekan tombol fisik '{target}'."

        # 5. SIMPAN KE MEMORI - [BARU]
        if cmd == 'save_text':
            # Target di sini biasanya selector elemennya
            return f"Sistem membaca dan mengingat informasi dari elemen '{target}'."

        # 6. VALIDASI & TUNGGU
        if cmd == 'wait':
            return f"Sistem menunggu hingga elemen '{target}' siap di layar."
        if cmd == 'assert':
            return f"Sistem memverifikasi bahwa teks '{target}' tampil valid di layar."

        # 7. SCROLL
        if cmd == 'scroll':
            return f"User melakukan navigasi dengan menggulir layar ke '{target}'."

        # Fallback
        return f"User melakukan aksi {cmd} pada {target}."