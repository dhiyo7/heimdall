import re
from uiautomator2 import UiObjectNotFoundError
from heimdall.core.driver import HeimdallDriver
from heimdall.core.vision_log import VisionLog
from heimdall.reporters.saga_writer import SagaWriter
from heimdall.core.state_manager import StateManager
from heimdall.reporters.map_builder import MapBuilder


class HeimdallParser:
    """
    Parses .heim files and executes commands using the HeimdallDriver.
    """

    def __init__(self, driver: HeimdallDriver, logger: VisionLog, reporter: SagaWriter, state: StateManager, map_builder: MapBuilder):
        """
        Initializes the parser with a driver, logger, reporter, state manager, and map builder instance.

        Args:
            driver (HeimdallDriver): The driver to execute commands with.
            logger (VisionLog): The logger for capturing context data.
            reporter (SagaWriter): The reporter for generating the Saga document.
            state (StateManager): The manager for tracking application state.
            map_builder (MapBuilder): The builder for generating the flowchart.
        """
        self.driver = driver
        self.logger = logger
        self.reporter = reporter
        self.state = state
        self.map_builder = map_builder

    def parse_file(self, filepath: str):
        """
        Reads and executes a .heim script file line by line.

        Args:
            filepath (str): The path to the .heim file.
        """
        print(f"--- Starting scenario: {filepath} ---")
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                print(f"\n[Step {line_num}]> {line}")
                status = "Success"
                from_activity = self.state.last_activity or "Start"

                try:
                    # 1. Capture context BEFORE the action
                    context_data = self.capture_context(line_num)
                    
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
                        step_number=line_num,
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

        print(f"--- Scenario finished: {filepath} ---")

    def capture_context(self, step_number: int) -> dict:
        """
        Captures the state (screenshot, activity, logs) before an action.
        Returns a dictionary containing the captured data.
        """
        print("  [Context] Capturing state...")
        context = {"activity": "N/A", "logs": [], "screenshot": "N/A"}

        # Get current activity and update state
        try:
            activity_name = self.driver.get_current_activity()
            context["activity"] = activity_name
            self.state.update_activity(activity_name)
            print(f"    - Activity: {context['activity']}")
        except Exception as e:
            print(f"    - Could not get activity: {e}")

        # Get recent logs
        context["logs"] = self.logger.get_logs(last_n_lines=3)
        if context["logs"]:
            print("    - Recent Logs:")
            for log_line in context["logs"]:
                print(f"      {log_line}")
        
        # Define a consistent place for screenshots
        screenshot_dir = self.reporter.output_dir
        screenshot_path = f"{screenshot_dir}/step_{step_number}.png"
        context["screenshot"] = screenshot_path

        # Take screenshot
        try:
            self.driver.take_screenshot(screenshot_path)
            print(f"    - Screenshot saved to {screenshot_path}")
        except Exception as e:
            print(f"    - Could not take screenshot: {e}")
        
        return context


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
            try:
                # Per requirement, try spatial search first for input fields
                element = self.driver.find_input_by_label(label)
                element.set_text(text_to_type)
            except (UiObjectNotFoundError, IndexError):
                print(f"Info: Spatial search failed. Falling back to robust search for '{label}'.")
                # Fallback to general robust search
                element = self.driver.find_element_robust(label)
                element.set_text(text_to_type)

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