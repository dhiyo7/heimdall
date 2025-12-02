import uiautomator2 as u2
from uiautomator2 import UiObjectNotFoundError

class HeimdallDriver:
    """
    A wrapper for uiautomator2 to provide robust element finding for Heimdall.
    """
    def __init__(self, device_serial=None):
        """
        Initializes the HeimdallDriver and connects to the specified device.

        Args:
            device_serial (str, optional): The serial number of the target Android device.
                                           If not provided, it connects to the first available device.
        """
        self.d = u2.connect(device_serial)

    def find_element_robust(self, selector: str) -> u2.UiObject:
        """
        Finds an element using the "Hierarchy Fallback Strategy".

        The search is performed in the following order:
        1.  By resource-id.
        2.  By exact text.
        3.  By exact content-description.

        Args:
            selector (str): The identifier for the element (e.g., "Masuk", "com.example:id/button").

        Returns:
            uiautomator2.UiObject: The found UI object.

        Raises:
            UiObjectNotFoundError: If the element cannot be found using any of the strategies.
        """
        try:
            # 1. ID Check
            element = self.d(resourceId=selector)
            if element.exists:
                return element
        except UiObjectNotFoundError:
            pass

        try:
            # 2. Text Check
            element = self.d(text=selector)
            if element.exists:
                return element
        except UiObjectNotFoundError:
            pass

        try:
            # 3. Desc Check
            element = self.d(description=selector)
            if element.exists:
                return element
        except UiObjectNotFoundError:
            pass

        raise UiObjectNotFoundError({"message": f"Element with selector '{selector}' not found"})

    def find_input_by_label(self, label: str, input_class="android.widget.EditText") -> u2.UiObject:
        """
        Finds an input field located spatially below a given text label.

        Args:
            label (str): The text of the label above the input field.
            input_class (str): The class name of the input widget.

        Returns:
            uiautomator2.UiObject: The found input field.

        Raises:
            UiObjectNotFoundError: If the label or a corresponding input field cannot be found.
        """
        label_element = self.find_element_robust(label)
        
        # Find all elements of the specified input class that are below the label
        possible_inputs = self.d(className=input_class).down(selector=f'className={input_class}')
        
        if not possible_inputs:
             raise UiObjectNotFoundError({"message": f"No input field of class '{input_class}' found below label '{label}'"})

        # Assume the closest one is the correct one for now
        return possible_inputs[0]


    def get_current_activity(self) -> str:
        """
        Retrieves the name of the current foreground activity.

        Returns:
            str: The name of the current activity.
        """
        return self.d.app_current()['activity']

    def take_screenshot(self, path: str):
        """
        Takes a screenshot and saves it to the specified path.

        Args:
            path (str): The full path where the screenshot will be saved.
        """
        self.d.screenshot(path)