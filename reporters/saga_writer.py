from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

class SagaWriter:
    def __init__(self, scenario_name, output_dir):
        self.document = Document()
        
        # --- DOKUMEN SETUP ---
        # Set margin agak tipis biar muat banyak
        section = self.document.sections[0]
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)

        # Header Utama
        title = self.document.add_heading(level=0)
        run = title.add_run(f'Heimdall Saga: {scenario_name}')
        run.font.name = 'Arial'
        run.font.size = Pt(22)
        run.font.color.rgb = RGBColor(33, 33, 33) # Dark Grey
        
        self.output_dir = output_dir
        safe_name = "".join([c for c in scenario_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        self.file_path = os.path.join(output_dir, f"Heimdall_Saga_{safe_name}.docx")

    def add_step(self, step_num, description, activity_name, screenshot_path, api_logs=None):
        """
        GRID SYSTEM:
        -------------------------------------------
        | [STEP HEADER & ACTIVITY]                |
        -------------------------------------------
        | [NARRATIVE TEXT]      | [SCREENSHOT]    |
        |                       |                 |
        | [API TABLE]           |                 |
        -------------------------------------------
        """
        
        # 1. HEADER SECTION (Judul Step)
        # Kita pakai Tabel 1 baris untuk header agar background bisa diwarnai (opsional)
        header_table = self.document.add_table(rows=1, cols=1)
        header_table.autofit = False
        header_table.columns[0].width = Inches(6.5)
        
        cell_header = header_table.cell(0, 0)
        p_head = cell_header.paragraphs[0]
        run_head = p_head.add_run(f"STEP {step_num}")
        run_head.bold = True
        run_head.font.size = Pt(14)
        run_head.font.name = 'Arial'
        run_head.font.color.rgb = RGBColor(0, 51, 102) # Navy Blue
        
        # Activity (Subtitle)
        p_sub = cell_header.add_paragraph()
        run_sub = p_sub.add_run(f"📍 {activity_name}")
        run_sub.font.size = Pt(8)
        run_sub.italic = True
        run_sub.font.color.rgb = RGBColor(128, 128, 128)
        p_sub.paragraph_format.space_after = Pt(10)

        # 2. CONTENT GRID (Kiri Teks, Kanan Gambar)
        # Tabel utama pengunci layout
        grid = self.document.add_table(rows=1, cols=2)
        grid.autofit = False
        grid.columns[0].width = Inches(3.8) # Kiri: Lebar Teks
        grid.columns[1].width = Inches(2.7) # Kanan: Lebar Gambar

        # --- SEL KIRI: NARASI & API ---
        left_cell = grid.cell(0, 0)
        left_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        # A. Narasi Storyteller
        p_desc = left_cell.paragraphs[0]
        run_desc = p_desc.add_run(description)
        run_desc.font.size = Pt(11)
        run_desc.font.name = 'Georgia' # Font serif enak dibaca
        p_desc.paragraph_format.space_after = Pt(20) # Jarak ke API

        # B. Tabel API (Jika Ada)
        if api_logs and len(api_logs) > 0:
            p_api_title = left_cell.add_paragraph()
            run_api = p_api_title.add_run("📡 Network Log")
            run_api.bold = True
            run_api.font.size = Pt(9)
            run_api.font.name = 'Arial'
            
            # Nested Table untuk API
            api_table = left_cell.add_table(rows=1, cols=3)
            api_table.style = 'Table Grid'
            api_table.autofit = False
            api_table.columns[0].width = Inches(0.6) # Method
            api_table.columns[1].width = Inches(2.4) # Endpoint
            api_table.columns[2].width = Inches(0.6) # Status

            # Header API
            hdr = api_table.rows[0].cells
            self._fill_cell(hdr[0], "MTHD", bg="E0E0E0", bold=True)
            self._fill_cell(hdr[1], "ENDPOINT", bg="E0E0E0", bold=True)
            self._fill_cell(hdr[2], "STS", bg="E0E0E0", bold=True)

            # Isi API
            for log in api_logs:
                # Sanitasi Data
                method = log.get('method', '-') if isinstance(log, dict) else "-"
                endpoint = log.get('endpoint', '-') if isinstance(log, dict) else str(log)
                status = str(log.get('status', '-')) if isinstance(log, dict) else "-"
                
                # Potong Endpoint Panjang
                if len(endpoint) > 35: endpoint = "..." + endpoint[-32:]

                row = api_table.add_row().cells
                self._fill_cell(row[0], method, size=7)
                self._fill_cell(row[1], endpoint, size=7, font='Consolas')
                
                # Status Icon
                icon = "✅" if status.startswith('2') else "❌"
                if status == '-': icon = "⏳"
                self._fill_cell(row[2], f"{icon}{status}", size=7, bold=True)

        # --- SEL KANAN: GAMBAR ---
        right_cell = grid.cell(0, 1)
        right_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        if screenshot_path and os.path.exists(screenshot_path):
            p_img = right_cell.paragraphs[0]
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_img = p_img.add_run()
            # Lebar gambar dimaksimalkan sesuai kolom kanan (2.7 inch)
            # Ini membuat screenshot terlihat besar dan jelas
            run_img.add_picture(screenshot_path, width=Inches(2.5))

        # 3. PAGE BREAK (Kunci 1 Halaman)
        self.document.add_page_break()

    def _fill_cell(self, cell, text, bg=None, bold=False, size=8, font='Arial'):
        """Helper canggih untuk styling sel tabel"""
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(text)
        run.font.bold = bold
        run.font.size = Pt(size)
        run.font.name = font
        
        # Set Background Color (XML Hack)
        if bg:
            tc_pr = cell._element.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), bg)
            tc_pr.append(shd)

    def save(self):
        try:
            self.document.save(self.file_path)
            print(f"  📄 Report saved: {self.file_path}")
        except Exception as e:
            print(f"!!! Error saving docx: {e}")