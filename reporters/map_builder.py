from graphviz import Digraph
import os

class MapBuilder:
    """
    Generates a flowchart/mind map of the execution path using Graphviz.
    """

    def __init__(self, scenario_name: str, output_dir="reports"):
        """
        Initializes the map builder.

        Args:
            scenario_name (str): The name of the test scenario for the map title.
            output_dir (str): The directory where the map will be saved.
        """
        self.scenario_name = scenario_name
        self.output_dir = os.path.join(os.getcwd(), output_dir)
        self.dot = Digraph(comment=f'Heimdall Flow: {self.scenario_name}')
        self.dot.attr(rankdir='LR', size='10,10', label=f'Flow: {scenario_name}', fontsize='20')
        self.dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', fontname='Helvetica')
        self.dot.attr('edge', fontname='Helvetica', fontsize='10')
        
        # Start node is always present
        self.dot.node("Start", style='rounded,filled', fillcolor='#4CAF50') # Green
        self.nodes = {"Start"}

    def add_transition(self, from_activity: str, action_name: str, to_activity: str, status: str):
        """
        Adds a state transition to the map.

        Args:
            from_activity (str): The name of the source activity.
            action_name (str): The name of the action/command performed.
            to_activity (str): The name of the destination activity.
            status (str): The result of the action ('Success' or 'Failed').
        """
        # Sanitize node names
        from_node = from_activity.split('.')[-1]
        to_node = to_activity.split('.')[-1]

        # Add nodes if they don't exist
        if from_node not in self.nodes:
            self.dot.node(from_node)
            self.nodes.add(from_node)
        if to_node not in self.nodes:
            self.dot.node(to_node)
            self.nodes.add(to_node)

        # Determine color based on status
        color = '#4CAF50' if status == 'Success' else '#F44336' # Green or Red
        
        # Color the destination node
        self.dot.node(to_node, style='rounded,filled', fillcolor=color)

        # Create the edge with the action as the label
        self.dot.edge(from_node, to_node, label=action_name)

    def render_map(self, filename=None):
        """
        Saves the flowchart to a file (e.g., PNG).

        Args:
            filename (str, optional): The name of the output file (without extension).
                                      Defaults to a generated name.
        """
        if filename is None:
            safe_scenario_name = "".join(c for c in self.scenario_name if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"Heimdall_Flow_{safe_scenario_name}"

        output_path = os.path.join(self.output_dir, filename)
        try:
            self.dot.render(output_path, format='png', view=False, cleanup=True)
            print(f"Map saved to: {output_path}.png")
        except Exception as e:
            print(f"!!! Could not generate map. Is Graphviz installed and in your PATH? Error: {e}")