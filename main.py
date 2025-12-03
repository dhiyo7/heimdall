import argparse
import os
import time
from core.driver import HeimdallDriver
from core.parser import HeimdallParser
from core.vision_log import LogSniffer
from core.storyteller import HeimdallStoryteller
from reporters.map_builder import MapBuilder
from reporters.saga_writer import SagaWriter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to .heim file")
    args = parser.parse_args()

    scenario_name = os.path.splitext(os.path.basename(args.file))[0]
    output_dir = os.path.join("reports", scenario_name)
    screenshot_dir = os.path.join(output_dir, "screenshots")
    if not os.path.exists(screenshot_dir): os.makedirs(screenshot_dir)

    print(f"🛡️ HEIMDALL STARTING: {scenario_name}")
    
    driver = HeimdallDriver()
    # PENTING: Parser baru hanya butuh driver
    heim_parser = HeimdallParser(driver)
    
    mapper = MapBuilder(scenario_name, output_dir)
    saga = SagaWriter(scenario_name, output_dir)
    
    # Start Sniffer di awal
    sniffer = LogSniffer()
    sniffer.start()
    
    step_counter = 0
    current_activity = "Start"

    try:
        # Loop langkah demi langkah
        for step in heim_parser.parse_file(args.file):
            if step['type'] == 'feature':
                print(f"\n--- [Feature: {step['name']}] ---")
                mapper.set_feature(step['name'])
                continue
            
            step_counter += 1
            
            # --- 1. GENERATE STORY (User POV) ---
            # Kita buat narasi SEBELUM eksekusi agar user tau apa yang 'akan' dilakukan
            raw_target = str(step['args'][0]) if step['args'] else ""
            user_narrative = HeimdallStoryteller.generate_narrative(step['cmd'], raw_target)
            
            print(f"[Step {step_counter}]> {user_narrative}")
            
            try:
                # --- 2. EKSEKUSI ---
                cmd = step['cmd']
                if cmd == "open_app": driver.d.app_start(step['args'][0])
                elif cmd == "input_text": driver.input_text_on_field(step['args'][0], step['args'][1])
                elif cmd == "click":
                    if str(step['args'][0]).upper() == "FAB": driver.find_element_robust("FAB").click()
                    else: driver.find_element_robust(step['args'][0]).click()
                elif cmd == "wait": driver.find_element_robust(step['args'][0])
                elif cmd == "assert": 
                    if not driver.find_element_robust(step['args'][0]).exists: raise Exception("Assert Failed")
                elif cmd == "scroll": driver.scroll_down_coordinate()

                # --- 3. TUNGGU API (Fix Status ?) ---
                # Beri waktu lebih lama (2.5 detik) agar response API sempat masuk log
                time.sleep(2.5) 

                # --- 4. DATA COLLECTION ---
                next_activity = driver.get_current_activity()
                ss_path = os.path.join(screenshot_dir, f"step_{step_counter}.png")
                driver.take_screenshot(ss_path)
                
                # Ambil log API terbaru
                api_logs = sniffer.get_recent_logs()
                
                # --- 5. REPORTING ---
                # PENTING: Gunakan 'user_narrative' (bukan step['desc'])
                saga.add_step(step_counter, user_narrative, current_activity, ss_path, api_logs)
                
                mapper.add_transition(current_activity, user_narrative, next_activity, "Success")
                current_activity = next_activity

            except Exception as e:
                print(f"!!! ERROR: {e}")
                mapper.add_transition(current_activity, step['desc'], current_activity, "Failed")
                raise e

    except Exception as e:
        print(f"!!! Critical Failure: {e}")
    finally:
        sniffer.stop()
        saga.save()
        mapper.render_map()
        driver.stop_driver()
        print("=== HEIMDALL SESSION ENDED ===")

if __name__ == "__main__":
    main()