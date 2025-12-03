import re

class HeimdallStoryteller:
    """
    Converts technical command strings into user-centric narratives.
    """

    def _humanize(self, text: str) -> str:
        """Converts an identifier into a human-readable, title-cased string."""
        # Replace underscores/hyphens with spaces, then title case
        return re.sub(r'[_-]', ' ', text).title()

    def generate_narrative(self, command: str) -> str:
        """
        Generates a narrative from a given command line.

        Args:
            command (str): The raw .heim command.

        Returns:
            str: A user-centric narrative description of the action.
        """
        normalized_command = command.lower()
        args_in_quotes = re.findall(r'"(.*?)"' , command)
        target = self._humanize(args_in_quotes[0]) if args_in_quotes else ""

        if normalized_command.startswith('buka aplikasi'):
            return f"User memulai sesi dengan membuka aplikasi {target}."
        
        if normalized_command.startswith('ketik'):
            # For input, the target is the second argument (the label)
            target_label = self._humanize(args_in_quotes[1]) if len(args_in_quotes) > 1 else ""
            return f"User melengkapi form dengan menginput informasi ke '{target_label}'."

        if normalized_command.startswith('ketuk'):
            # Context-aware click descriptions
            if 'simpan' in target.lower():
                return f"User menyimpan perubahan dengan memilih '{target}'."
            if 'batal' in target.lower():
                return f"User membatalkan aksi dengan memilih '{target}'."
            if 'fab' in target.lower() or 'add' in target.lower():
                return f"User memulai alur baru dengan menekan tombol '{target}'."
            return f"User memilih opsi '{target}'."

        if normalized_command.startswith('pastikan muncul') or normalized_command.startswith('tunggu sampai'):
            return f"Sistem memverifikasi elemen '{target}' tampil di layar."

        if normalized_command.startswith('gulir'):
            return f"User melakukan navigasi dengan menggulir ke arah '{target}'."

        return command # Fallback to the raw command