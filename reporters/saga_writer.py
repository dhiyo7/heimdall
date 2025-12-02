from docx import Document
from docx.shared import Inches, Pt
import os

class SagaWriter:
    """
    Generates a narrative Word document report (The Saga) for a test scenario.
    """

    def __init__(self, scenario_name: str, output_dir="reports"):
        """
        Initializes the report generator.

        Args:
            scenario_name (str): The name of the test scenario, used for the report title.
            output_dir (str): The directory where the report will be saved.
        """
        self.scenario_name = scenario_name
        self.output_dir = os.path.join(os.getcwd(), output_dir) # Use absolute path
        self.document = Document()
        self.document.add_heading(f"Heimdall Saga: {self.scenario_name}", level=0)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def add_step(self, step_command: str, step_number: int, screenshot_path: str, context_data: dict):
        """
        Adds a single step to the report in a two-column table.

        Args:
            step_command (str): The .heim command that was executed.
            step_number (int): The step number in the sequence.
            screenshot_path (str): Path to the screenshot image for this step.
            context_data (dict): A dictionary containing context like 'activity' and 'logs'.
        """
        self.document.add_heading(f"Step {step_number}: {step_command}", level=2)

        # Create a two-column table
        table = self.document.add_table(rows=1, cols=2)
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

        # Add Logs
        p_right.add_run('API Log Status:\n').bold = True
        font = p_right.runs[-1].font
        font.size = Pt(11)
        logs = context_data.get('logs', [])
        if logs:
            for log_line in logs:
                log_run = p_right.add_run(f"  {log_line}\n")
                log_run.font.size = Pt(8)
        else:
            p_right.add_run("  No relevant logs captured.\n")

        self.document.add_paragraph() # Add some space after the table

    def save(self, filename=None):
        """
        Saves the Word document.

        Args:
            filename (str, optional): The name of the output file. 
                                      If not provided, a default is generated.
        """
        if filename is None:
            safe_scenario_name = "".join(c for c in self.scenario_name if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"Heimdall_Saga_{safe_scenario_name}.docx"
        
        save_path = os.path.join(self.output_dir, filename)
        self.document.save(save_path)
        print(f"---\nSaga report saved to: {save_path}\n---")