class StateManager:
    """
    Tracks the state of the application flow, primarily for mind map generation.
    """

    def __init__(self):
        """
        Initializes the state manager.
        """
        self.activity_path = []
        self.last_activity = None

    def update_activity(self, activity_name: str):
        """
        Updates the current activity, tracking the path taken.

        Args:
            activity_name (str): The name of the current activity.
        """
        if activity_name and activity_name != self.last_activity:
            # To keep the map clean, let's simplify common Android activity names
            simple_name = activity_name.split('.')[-1]
            self.activity_path.append(simple_name)
            self.last_activity = activity_name
            print(f"  [State] Activity changed to: {simple_name}")

    def get_path(self) -> list:
        """
        Returns the recorded path of activities.

        Returns:
            list: A list of activity names in the order they were visited.
        """
        return self.activity_path