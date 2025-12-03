import subprocess
import threading
from collections import deque
import re
from urllib.parse import urlparse

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
        # Clear previous logs
        subprocess.run(["adb", "logcat", "-c"], check=False)
        
        process = subprocess.Popen(["adb", "logcat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Regex for request and response lines
        req_pattern = re.compile(r"--> (GET|POST|PUT|DELETE) (https://[^ ]+)")
        res_pattern = re.compile(r"<-- (\d{3})")

        temp_request = None

        while self.is_running and not process.poll():
            line = process.stdout.readline()
            if not line:
                continue

            if "OkHttp" not in line:
                continue

            req_match = req_pattern.search(line)
            if req_match:
                method, url = req_match.groups()
                path = urlparse(url).path
                temp_request = {"method": method, "endpoint": path}
                continue

            res_match = res_pattern.search(line)
            if res_match and temp_request:
                status_code = res_match.group(1)
                temp_request["status_code"] = status_code
                self.log_buffer.append(temp_request)
                temp_request = None

        process.terminate()

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

    def get_logs(self, last_n_lines=5) -> list:
        """
        Retrieves the last N log entries from the buffer.
        """
        # Returns a list of dictionaries
        return list(self.log_buffer)[-last_n_lines:]

    def clear(self):
        """
        Clears the internal log buffer.
        """
        self.log_buffer.clear()