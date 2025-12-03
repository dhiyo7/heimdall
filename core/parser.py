import re
import os
import time
from uiautomator2.exceptions import UiObjectNotFoundError
from heimdall.core.driver import HeimdallDriver
from heimdall.core.vision_log import VisionLog
from heimdall.reporters.saga_writer import SagaWriter
from heimdall.core.state_manager import StateManager
from heimdall.reporters.map_builder import MapBuilder


class HeimdallParser:
    """
    Parses .heim files and executes commands using the HeimdallDriver.
    """

    def __init__(self, driver: HeimdallDriver, logger: VisionLog, reporter: SagaWriter, state: StateManager, map_builder: MapBuilder, screenshots_dir: str):
        """
        Initializes the parser with a driver, logger, reporter, state manager, and map builder instance.

        Args:
            driver (HeimdallDriver): The driver to execute commands with.
            logger (VisionLog): The logger for capturing context data.
            reporter (SagaWriter): The reporter for generating the Saga document.
            state (StateManager): The manager for tracking application state.
            map_builder (MapBuilder): The builder for generating the flowchart.
            screenshots_dir (str): The directory to save screenshots.
        """
        self.driver = driver
        self.logger = logger
        self.reporter = reporter
        self.state = state
        self.map_builder = map_builder
        self.screenshots_dir = screenshots_dir

    def parse_file(self, filepath: str):
        """
        Reads and executes a .heim script file line by line.

        Args:
            filepath (str): The path to the .heim file.
        """
        print(f"--- Starting scenario: {filepath} ---")
        step_counter = 1
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Check for feature comment
                if line.startswith('# FEATURE:') or line.startswith('# FITUR:'):
                    feature_name = line.split(':', 1)[1].strip()
                    self.map_builder.set_feature(feature_name)
                    print(f"\n--- Entering Feature: {feature_name} ---")
                    continue

                if line.startswith('#'): # Skip other comments
                    continue

                # Add a delay to allow the UI to settle from the previous action
                time.sleep(1.5)
                
                print(f"\n[Step {step_counter}]> {line}")
                status = "Success"
                from_activity = self.state.last_activity or "Start"

                try:
                    # 1. Capture context BEFORE the action
                    context_data = self.capture_context(step_counter)
                    
                    # 2. Execute the command
                    self.execute_command(line)

                    # 3. Capture context AFTER the action for the transition
                    to_activity = self.driver.get_current_activity()
                    self.state.update_activity(to_activity)

                except Exception as e:
                    status = "Failed"
                    to_activity = self.state.last_activity # Stay on the same activity if failed
                    print(f"!!! ERROR on line {line_num}: {e}")
                    # In a full implementation, we would add failure details to the report
                    raise
                finally:
                    # 4. Add step to Saga report
                    self.reporter.add_step(
                        step_command=line,
                        step_number=step_counter,
                        screenshot_path=context_data["screenshot"],
                        context_data=context_data
                    )
                    # 5. Add transition to Map report
                    self.map_builder.add_transition(
                        from_activity=from_activity,
                        action_name=line,
                        to_activity=to_activity,
                        status=status
                    )
                    step_counter += 1

        print(f"--- Scenario finished: {filepath} ---")

    def capture_context(self, step_number: int) -> dict:
        """
        Captures the current state (screenshot, activity, logs) for reporting.

        Args:
            step_number (int): The current step number, used for the screenshot filename.

        Returns:
            dict: A dictionary containing the screenshot path, activity name, and recent logs.
        """
        # 1. Take Screenshot
        screenshot_path = os.path.join(self.screenshots_dir, f"step_{step_number}.png")
        self.driver.take_screenshot(screenshot_path)

        # 2. Get Current Activity
        activity_name = self.driver.get_current_activity()
        self.state.update_activity(activity_name)

        # 3. Get Recent Logs (now a list of dicts)
        logs = self.logger.get_logs()

        return {
            "screenshot": screenshot_path,
            "activity": activity_name,
            "logs": logs
        }


    def execute_command(self, command: str):
        """
        Parses and executes a single command string.
        The parser is case-insensitive and uses quoted text as arguments.
        """
        normalized_command = command.lower()
        args_in_quotes = re.findall(r'"(.*?)"', command)

        if normalized_command.startswith('buka aplikasi'):
            if not args_in_quotes:
                raise ValueError("'Buka aplikasi' command requires a package name in quotes.")
            package_name = args_in_quotes[0]
            print(f"Action: Launching app '{package_name}'")
            self.driver.d.app_start(package_name, stop=True)

        elif normalized_command.startswith('tunggu sampai'):
            if not args_in_quotes:
                raise ValueError("'Tunggu sampai' command requires text in quotes.")
            text_to_wait = args_in_quotes[0]
            timeout = 20 # seconds
            print(f"Action: Waiting for element '{text_to_wait}' to appear (timeout: {timeout}s)")
            if not self.driver.d(text=text_to_wait).wait(timeout=timeout):
                 raise UiObjectNotFoundError({"message": f"Element with text '{text_to_wait}' did not appear within {timeout}s."})

        elif normalized_command.startswith('ketuk'):
            if not args_in_quotes:
                raise ValueError("'Ketuk' command requires a selector in quotes.")
            selector = args_in_quotes[0]
            print(f"Action: Tapping on element '{selector}'")
            element = self.driver.find_element_robust(selector)
            element.click()

        elif normalized_command.startswith('ketik'):
            if len(args_in_quotes) < 2:
                raise ValueError("'Ketik' command requires two arguments in quotes: text to type and a selector.")
            text_to_type = args_in_quotes[0]
            label = args_in_quotes[1]
            print(f"Action: Typing '{text_to_type}' into field associated with '{label}'")
            self.driver.input_text_on_field(text_to_type, label)

        elif normalized_command.startswith('pastikan muncul'):
            if not args_in_quotes:
                raise ValueError("'Pastikan muncul' command requires text in quotes.")
            text_to_assert = args_in_quotes[0]
            print(f"Action: Verifying that element '{text_to_assert}' is visible.")
            try:
                self.driver.find_element_robust(text_to_assert)
                print(f"Success: Element '{text_to_assert}' found.")
            except UiObjectNotFoundError:
                raise AssertionError(f"Verification failed: Element '{text_to_assert}' was not found on screen.")

        elif normalized_command.startswith('gulir'):
            if not args_in_quotes:
                raise ValueError("'Gulir' command requires a direction or text in quotes.")
            target = args_in_quotes[0].lower()
            print(f"Action: Scrolling towards '{target}'")
            scrollable_element = self.driver.d(scrollable=True)
            if not scrollable_element.exists:
                raise UiObjectNotFoundError({"message": "Cannot scroll, no scrollable view found on screen."})

            if target == 'bawah':
                scrollable_element.scroll.forward(steps=100)
            elif target == 'atas':
                scrollable_element.scroll.backward(steps=100)
            elif target == 'kanan':
                scrollable_element.scroll.horiz.forward(steps=100)
            elif target == 'kiri':
                scrollable_element.scroll.horiz.backward(steps=100)
            else:
                # Assume it's text to scroll to
                scrollable_element.scroll.to(text=args_in_quotes[0]) # Use original case for text
        else:
            raise ValueError(f"Unknown command keyword in line: '{command}'")