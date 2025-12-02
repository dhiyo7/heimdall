import subprocess
import threading
from collections import deque

class VisionLog:
    """
    Sniffs ADB logcat for specific keywords in a non-blocking thread.
    """

    def __init__(self, keywords=None, max_lines=50):
        """
        Initializes the logcat sniffer.

        Args:
            keywords (list, optional): A list of keywords to filter for (e.g., ['HTTP', 'API']).
                                       Defaults to None, which captures all logs.
            max_lines (int): The maximum number of recent matching log lines to store.
        """
        self.keywords = keywords or []
        self.log_buffer = deque(maxlen=max_lines)
        self.is_running = False
        self._log_thread = None

    def _monitor_logcat(self):
        """
        The internal method that runs in a separate thread to monitor logcat.
        """
        # Clear previous logs before starting
        subprocess.run(["adb", "logcat", "-c"], check=False)
        
        # Start a new logcat process
        process = subprocess.Popen(["adb", "logcat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while self.is_running and not process.poll():
            line = process.stdout.readline()
            if not line:
                continue

            # If keywords are specified, filter lines; otherwise, capture all.
            if not self.keywords or any(keyword in line for keyword in self.keywords):
                self.log_buffer.append(line.strip())

        process.terminate() # Ensure the process is killed on exit

    def start(self):
        """
        Starts the logcat monitoring thread.
        """
        if self.is_running:
            print("VisionLog is already running.")
            return

        self.is_running = True
        self._log_thread = threading.Thread(target=self._monitor_logcat, daemon=True)
        self._log_thread.start()
        print("VisionLog started monitoring logcat.")

    def stop(self):
        """
        Stops the logcat monitoring thread.
        """
        if not self.is_running:
            print("VisionLog is not running.")
            return

        self.is_running = False
        if self._log_thread:
            self._log_thread.join(timeout=5) # Wait for the thread to finish
        print("VisionLog stopped.")

    def get_logs(self, last_n_lines=3) -> list:
        """
        Retrieves the last N lines from the log buffer.

        Args:
            last_n_lines (int): The number of recent lines to retrieve.

        Returns:
            list: A list of the last N captured log lines.
        """
        return list(self.log_buffer)[-last_n_lines:]

    def clear(self):
        """
        Clears the internal log buffer.
        """
        self.log_buffer.clear()