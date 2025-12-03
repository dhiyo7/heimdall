import sys
import os

# Add the project root to the Python path to resolve the ModuleNotFoundError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from heimdall.core.driver import HeimdallDriver
from heimdall.core.parser import HeimdallParser
from heimdall.core.vision_log import VisionLog
from heimdall.reporters.saga_writer import SagaWriter
from heimdall.reporters.map_builder import MapBuilder
from heimdall.core.state_manager import StateManager

def main():
    """
    Main entry point for the Heimdall automation tool.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Heimdall: A Keyword-Driven Android Automation Tool.")
    parser.add_argument("scenario_file", help="Path to the .heim scenario file to execute.")
    parser.add_argument("-d", "--device", help="The serial number of the target Android device.", default=None)
    args = parser.parse_args()

    # Check if the scenario file exists
    if not os.path.exists(args.scenario_file):
        print(f"Error: Scenario file not found at '{args.scenario_file}'")
        return

    # --- Dynamic Directory Setup ---
    scenario_name = os.path.splitext(os.path.basename(args.scenario_file))[0]
    output_dir = os.path.join("reports", scenario_name)
    screenshots_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    print(f"Reports will be saved in: {output_dir}")

    # --- Initialize Core Components ---
    vision_logger = VisionLog(keywords=["HTTP", "OkHttp", "Retrofit"])
    saga_reporter = SagaWriter(scenario_name, output_dir=output_dir)
    map_builder = MapBuilder(scenario_name, output_dir=output_dir)
    state_manager = StateManager()

    try:
        # Start logcat monitoring
        vision_logger.start()

        # 1. Initialize the driver
        print("Initializing Heimdall Driver...")
        driver = HeimdallDriver(device_serial=args.device)
        print(f"Connected to device: {driver.d.device_info['serial']}")

        # 2. Initialize the parser with all components
        parser = HeimdallParser(
            driver=driver,
            logger=vision_logger,
            reporter=saga_reporter,
            state=state_manager,
            map_builder=map_builder,
            screenshots_dir=screenshots_dir
        )

        # Execute the scenario
        parser.parse_file(args.scenario_file)

    except Exception as e:
        print(f"\n--- A critical error occurred ---")
        print(f"Error details: {e}")
    finally:
        # Stop services and generate final reports
        vision_logger.stop()
        saga_reporter.save()
        
        # Build and save the final map
        map_builder.render_map()
        
        # --- TAMBAHAN: Restore Keyboard ---
        if 'driver' in locals():
            driver.stop_driver()



if __name__ == "__main__":
    main()