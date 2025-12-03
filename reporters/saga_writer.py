from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

class SagaWriter:
    def __init__(self, scenario_name, output_dir):
        self.document = Document()
        
        # --- HEADER DOKUMEN ---
        title = self.document.add_heading(level=0)
        run = title.add_run(f'Heimdall Saga: {scenario_name}')
        run.font.name = 'Segoe UI'
        run.font.color.rgb = RGBColor(0, 51, 102) # Dark Blue Professional
        
        self.output_dir = output_dir
        # Bersihkan nama file dari karakter aneh
        safe_name = "".join([c for c in scenario_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        self.file_path = os.path.join(output_dir, f"Heimdall_Saga_{safe_name}.docx")

    def add_step(self, step_num, description, activity_name, screenshot_path, api_logs=None):
        """
        Menambahkan langkah tes ke dokumen dengan layout profesional.
        """
        # 1. STEP HEADER (Judul Langkah)
        # Ganti background/style heading agar lebih rapi
        heading = self.document.add_heading(level=1)
        run = heading.add_run(f"Step {step_num}: {description}")
        run.font.name = 'Segoe UI'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)

        # 2. ACTIVITY INFO (Kecil di bawah judul)
        p_info = self.document.add_paragraph()
        run_info = p_info.add_run(f"📍 Current Activity: {activity_name}")
        run_info.font.size = Pt(9)
        run_info.italic = True
        run_info.font.color.rgb = RGBColor(100, 100, 100) # Grey

        # 3. SCREENSHOT (Tengah)
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                # Add picture centered
                paragraph = self.document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run()
                run.add_picture(screenshot_path, width=Inches(2.5)) # Ukuran pas, tidak kegedean
            except Exception as e:
                self.document.add_paragraph(f"[Error loading screenshot: {e}]")

        # 4. API LOG TABLE (Professional Grid)
        # Hanya render tabel jika ada data API
        if api_logs and isinstance(api_logs, list) and len(api_logs) > 0:
            
            # Sub-header kecil untuk tabel
            p_api = self.document.add_paragraph()
            p_api.paragraph_format.space_before = Pt(10)
            p_api.paragraph_format.space_after = Pt(2)
            run_api = p_api.add_run("📡 API Network Activity")
            run_api.bold = True
            run_api.font.size = Pt(10)
            run_api.font.color.rgb = RGBColor(0, 51, 102)

            # Buat Tabel dengan Style 'Table Grid' (Ada Garisnya)
            table = self.document.add_table(rows=1, cols=3)
            table.style = 'Table Grid' 
            table.autofit = False 
            
            # Set Lebar Kolom Manual (Biar rapi)
            # Total width kertas A4 margin normal ~6 inches
            table.columns[0].width = Inches(0.8)  # Method
            table.columns[1].width = Inches(3.5)  # Endpoint
            table.columns[2].width = Inches(1.2)  # Status

            # --- TABLE HEADER ---
            hdr_cells = table.rows[0].cells
            self._set_cell_text(hdr_cells[0], "METHOD", bold=True)
            self._set_cell_text(hdr_cells[1], "ENDPOINT", bold=True)
            self._set_cell_text(hdr_cells[2], "STATUS", bold=True)
            
            # Beri warna background header (Light Grey)
            for cell in hdr_cells:
                self._set_cell_background(cell, "F2F2F2")

            # --- TABLE CONTENT ---
            for log in api_logs:
                # Pastikan log punya keys yang benar (handle jika log string/dict)
                method = log.get('method', '-') if isinstance(log, dict) else "-"
                endpoint = log.get('endpoint', '-') if isinstance(log, dict) else str(log)
                status = str(log.get('status', '-')) if isinstance(log, dict) else "-"

                row_cells = table.add_row().cells
                
                # Method (Bold)
                self._set_cell_text(row_cells[0], method, size=8)
                
                # Endpoint (Monospace font ala kodingan)
                self._set_cell_text(row_cells[1], endpoint, size=8, font_name='Consolas')
                
                # Status (Dengan Emoji)
                status_text = f"✅ {status}" if status.startswith('2') else f"❌ {status}"
                self._set_cell_text(row_cells[2], status_text, size=8, bold=True)

        self.document.add_paragraph("\n") # Spacer antar step

    def _set_cell_text(self, cell, text, bold=False, size=9, font_name='Segoe UI'):
        """Helper untuk format text di dalam sel tabel"""
        cell.text = "" # Clear default
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(text)
        run.font.bold = bold
        run.font.size = Pt(size)
        run.font.name = font_name

    def _set_cell_background(self, cell, color_hex):
        """Helper untuk memberi warna background sel tabel (XML manipulation)"""
        tc_pr = cell._element.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), color_hex)
        tc_pr.append(shd)

    def save(self):
        try:
            self.document.save(self.file_path)
            print(f"  📄 Report saved: {self.file_path}")
        except Exception as e:
            print(f"!!! Error saving docx: {e}")