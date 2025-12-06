import argparse
import os
import time
from core.driver import HeimdallDriver
from core.parser import HeimdallParser
from core.vision_log import LogSniffer
from core.storyteller import HeimdallStoryteller
from core.state_manager import StateManager
from reporters.map_builder import MapBuilder
from reporters.saga_writer import SagaWriter

# Global Context
ctx = {
    "driver": None,
    "parser": None,
    "state": None,
    "mapper": None,
    "saga": None,
    "sniffer": None,
    "ss_dir": "",
    "step_count": 0,
    "activity": "Start"
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to .heim file")
    args = parser.parse_args()

    scenario_name = os.path.splitext(os.path.basename(args.file))[0]
    output_dir = os.path.join("reports", scenario_name)
    ctx["ss_dir"] = os.path.join(output_dir, "screenshots")
    if not os.path.exists(ctx["ss_dir"]): os.makedirs(ctx["ss_dir"])

    print(f"🛡️ HEIMDALL STARTING: {scenario_name}")
    
    ctx["driver"] = HeimdallDriver()
    ctx["parser"] = HeimdallParser(ctx["driver"])
    ctx["state"] = StateManager()
    ctx["mapper"] = MapBuilder(scenario_name, output_dir)
    ctx["saga"] = SagaWriter(scenario_name, output_dir)
    ctx["sniffer"] = LogSniffer()
    ctx["sniffer"].start()

    try:
        for step in ctx["parser"].parse_file(args.file):
            process_step(step)
            
        ctx["mapper"].add_step("Selesai", "end")

    except Exception as e:
        print(f"!!! Critical System Failure: {e}")
    finally:
        ctx["sniffer"].stop()
        ctx["saga"].save()
        ctx["mapper"].render_map()
        ctx["driver"].stop_driver()
        print("=== HEIMDALL SESSION ENDED ===")

def process_step(step):
    # A. Feature Grouping
    if step.get('type') == 'feature':
        print(f"\n--- [Feature: {step['name']}] ---")
        ctx["mapper"].set_feature(step['name'])
        return

    # B. Conditional Logic
    if step.get('type') == 'conditional':
        raw_cond = step['condition']
        target = ctx["state"].resolve_text(raw_cond)
        
        ctx["mapper"].add_step(f"Muncul '{target}'?", step_type="logic")
        print(f"  ❓ [Logic] Mengecek kondisi: '{target}'...")
        
        is_visible = False
        try:
            ctx["driver"].d(textContains=target).wait(timeout=2.0)
            if ctx["driver"].d(textContains=target).exists: is_visible = True
        except: pass

        if is_visible:
            print(f"  ✅ [Logic] TRUE. Masuk blok JIKA.")
            for sub_step in ctx["parser"].parse_lines(step['body'], "Conditional Block"):
                process_step(sub_step)
        else:
            print(f"  ⏩ [Logic] FALSE. Skip.")
        return

    # C. Standard Action
    ctx["step_count"] += 1
    
    resolved_args = []
    if 'args' in step:
        for arg in step['args']:
            resolved_args.append(ctx["state"].resolve_text(arg))
            
    raw_target = str(resolved_args[0]) if resolved_args else ""
    narrative = HeimdallStoryteller.generate_narrative(step['cmd'], raw_target)
    print(f"[Step {ctx['step_count']}]> {narrative}")

    time.sleep(0.5)

    try:
        cmd = step['cmd']
        driver = ctx["driver"]
        
        # --- EKSEKUSI ---
        if cmd == "open_app": driver.d.app_start(resolved_args[0])
        elif cmd == "input_text": driver.input_text_on_field(resolved_args[0], resolved_args[1])
        elif cmd == "click":
            if str(resolved_args[0]).upper() == "FAB": driver.find_element_robust("FAB").click()
            else: driver.find_element_robust(resolved_args[0]).click()
        elif cmd == "wait": driver.find_element_robust(resolved_args[0])
        elif cmd == "assert": 
            if not driver.find_element_robust(resolved_args[0]).exists: raise Exception("Assert Failed")
        elif cmd == "scroll": driver.scroll_down_coordinate()
        elif cmd == "save_text":
            text = driver.get_text_from_element(resolved_args[0])
            ctx["state"].set_variable(resolved_args[1], text)
        elif cmd == "press_key":
            key = str(resolved_args[0]).lower()
            if key == "back": driver.d.press("back")
            elif key == "home": driver.d.press("home")
            elif key == "enter": driver.d.press("enter")
            else: driver.d.press(key)

        # --- SUKSES ---
        time.sleep(1.5)
        next_act = driver.get_current_activity()
        ss_path = os.path.join(ctx["ss_dir"], f"step_{ctx['step_count']}.png")
        driver.take_screenshot(ss_path)
        logs = ctx["sniffer"].get_recent_logs()
        
        ctx["saga"].add_step(ctx["step_count"], narrative, ctx["activity"], ss_path, logs)
        ctx["state"].update_activity(next_act)
        ctx["activity"] = next_act
        ctx["mapper"].add_step(narrative, step_type="action")

    except Exception as e:
        # --- [MODIFIKASI: SOFT FAILURE] ---
        # Jangan raise e (jangan matikan program)
        # Cukup catat error dan lanjut
        print(f"!!! ERROR (Soft Fail): {e}")
        
        # Ambil Screenshot Error
        err_path = os.path.join(ctx["ss_dir"], f"error_step_{ctx['step_count']}.png")
        ctx["driver"].take_screenshot(err_path)
        
        # Catat di Report sebagai Error tapi Lanjut
        # Kita beri tanda [FAILED] di narasi agar user tau
        fail_narrative = f"[FAILED] {narrative}"
        ctx["saga"].add_step(ctx["step_count"], fail_narrative, ctx["activity"], err_path, [{"status": "ERROR", "msg": str(e)}])
        
        # Catat di Diagram sebagai Merah
        ctx["mapper"].add_step(narrative, step_type="error")
        
        # PENTING: Jangan 'raise e' disini agar loop for di atas tetap lanjut
        pass 

if __name__ == "__main__":
    main()