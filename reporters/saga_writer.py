from docx import Document
from docx.shared import Inches, Pt
import os
import json
import re

def _format_json_log(log_line: str) -> str:
    """Extracts and formats a JSON string from a log line."""
    # Regex to find a JSON object (starts with { or [)
    match = re.search(r'[{\[].*' , log_line)
    if not match:
        return log_line # Return original if no JSON is found

    json_str = match.group(0)
    try:
        # Load and re-dump with indentation
        parsed_json = json.loads(json_str)
        return json.dumps(parsed_json, indent=4)
    except json.JSONDecodeError:
        return json_str # Return the raw string if parsing fails

class SagaWriter:
    """
    Generates a narrative .docx report of a test scenario.
    """
    def __init__(self, scenario_name: str, output_dir: str):
        """
        Initializes the SagaWriter and creates the document.

        Args:
            scenario_name (str): The name of the test scenario.
            output_dir (str): The directory where the report will be saved.
        """
        self.scenario_name = scenario_name
        self.output_dir = output_dir
        self.doc = Document()
        self.doc.add_heading(f"Heimdall Saga: {scenario_name}", level=0)
        self.doc.add_paragraph(f"This document details the execution of the '{scenario_name}' scenario.")

    def add_step(self, step_command: str, step_number: int, screenshot_path: str, context_data: dict):
        """
        Adds a single step to the report in a two-column table.

        Args:
            step_command (str): The .heim command that was executed.
            step_number (int): The step number in the sequence.
            screenshot_path (str): Path to the screenshot image for this step.
            context_data (dict): A dictionary containing context like 'activity' and 'logs'.
        """
        self.doc.add_heading(f"Step {step_number}: {step_command}", level=2)

        # Create a two-column table
        table = self.doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Inches(3.5)
        table.columns[1].width = Inches(4.0)
        
        # Get table cells
        left_cell = table.cell(0, 0)
        right_cell = table.cell(0, 1)

        # --- Left Column: Screenshot ---
        # Add the picture to the cell's paragraph
        p_left = left_cell.paragraphs[0]
        run_left = p_left.add_run()
        if os.path.exists(screenshot_path):
            try:
                run_left.add_picture(screenshot_path, width=Inches(3.2))
            except Exception as e:
                p_left.text = f"[Error adding screenshot: {e}]"
        else:
            p_left.text = "[Screenshot not available]"

        # --- Right Column: Context ---
        p_right = right_cell.paragraphs[0]
        p_right.text = "" # Clear any default text
        
        # Add Activity
        p_right.add_run('Activity:\n').bold = True
        font = p_right.runs[-1].font
        font.size = Pt(11)
        activity = context_data.get('activity', 'N/A')
        p_right.add_run(f"{activity}\n\n")

        # Add Logs in a table
        logs = context_data.get('logs', [])
        if logs:
            p_right.add_run('API Log Summary:\n').bold = True
            log_table = self.doc.add_table(rows=1, cols=3, style='Table Grid')
            log_table.autofit = True
            hdr_cells = log_table.rows[0].cells
            hdr_cells[0].text = 'Method'
            hdr_cells[1].text = 'Endpoint'
            hdr_cells[2].text = 'Status'

            for log_entry in logs:
                row_cells = log_table.add_row().cells
                row_cells[0].text = log_entry.get('method', 'N/A')
                row_cells[1].text = log_entry.get('endpoint', 'N/A')
                
                status = str(log_entry.get('status_code', 'N/A'))
                if status.startswith('2'):
                    status_icon = '✅'
                elif status.startswith(('4', '5')):
                    status_icon = '❌'
                else:
                    status_icon = ''
                row_cells[2].text = f'{status_icon} {status}'
        else:
            p_right.add_run("No relevant logs captured.\n")

        self.doc.add_paragraph() # Add some space after the table

    def save(self):
        """
        Saves the final Word document.
        """
        # Save the final document
        save_path = os.path.join(self.output_dir, f"Heimdall_Saga_{self.scenario_name}.docx")
        self.doc.save(save_path)
        print(f"Saga report saved to: {save_path}")