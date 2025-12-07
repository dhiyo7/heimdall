import argparse
import os
import time
import sys  # Wajib untuk sys.stdout
from core.driver import HeimdallDriver
from core.parser import HeimdallParser
from core.vision_log import LogSniffer
from core.storyteller import HeimdallStoryteller
from core.state_manager import StateManager
from reporters.map_builder import MapBuilder
from reporters.saga_writer import SagaWriter

# Global Context
ctx = {
    "driver": None, "parser": None, "state": None,
    "mapper": None, "saga": None, "sniffer": None,
    "ss_dir": "", "step_count": 0, "activity": "Start"
}

def main():
    # [FIX 1] Real-time Logging (Anti-Macet di Linux/Streamlit)
    sys.stdout.reconfigure(line_buffering=True)
    
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
        print(f"⛔ CRITICAL STOP: {e}")
        ctx["mapper"].add_step("STOP (Critical Error)", step_type="error")
    finally:
        ctx["sniffer"].stop()
        ctx["saga"].save()
        ctx["mapper"].render_map()
        ctx["driver"].stop_driver()
        print("=== HEIMDALL SESSION ENDED ===")

def process_step(step):
    if step.get('type') == 'feature':
        print(f"\n--- [Feature: {step['name']}] ---")
        ctx["mapper"].set_feature(step['name'])
        return

    if step.get('type') == 'conditional':
        raw_cond = step['condition']
        target = ctx["state"].resolve_text(raw_cond)
        
        ctx["mapper"].add_step(f"Muncul '{target}'?", step_type="logic")
        print(f"  ❓ [Logic] Mengecek kondisi: '{target}'...")
        is_visible = False
        try:
            if ctx["driver"].d(textContains=target).exists: is_visible = True
        except: pass

        if is_visible:
            print(f"  ✅ [Logic] TRUE.")
            for sub_step in ctx["parser"].parse_lines(step['body'], "Conditional Block"):
                process_step(sub_step)
        else:
            print(f"  ⏩ [Logic] FALSE.")
        return

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
        if cmd == "open_app": 
            driver.d.app_start(resolved_args[0])
        elif cmd == "input_text": 
            driver.input_text_on_field(resolved_args[0], resolved_args[1])
        elif cmd == "click":
            # [FIX 2] Gunakan tap_element (Shell Click untuk Xiaomi/Emulator)
            if str(resolved_args[0]).upper() == "FAB": 
                driver.find_element_robust("FAB").click()
            else: 
                driver.tap_element(resolved_args[0])
                
        elif cmd == "wait": 
            driver.find_element_robust(resolved_args[0])
        elif cmd == "scroll": 
            driver.scroll_down_coordinate()
        elif cmd == "save_text":
            text = driver.get_text_from_element(resolved_args[0])
            ctx["state"].set_variable(resolved_args[1], text)
        elif cmd == "press_key":
            key = str(resolved_args[0]).lower()
            if key == "back": driver.d.press("back")
            elif key == "home": driver.d.press("home")
            elif key == "enter": driver.d.press("enter")
            else: driver.d.press(key)

        # --- [FIX 3] DYNAMIC ASSERTION LOGIC ---
        
        # A. SOFT ASSERTION (Keyword: PASTIKAN) -> Lanjut
        elif cmd == "assert" or cmd == "assert_soft": 
            if not driver.d(textContains=resolved_args[0]).exists and \
               not driver.d(resourceId=resolved_args[0]).exists:
                 # Raise biasa akan ditangkap sebagai Soft Fail
                 raise Exception(f"Check Failed: '{resolved_args[0]}' tidak ditemukan")
        
        # B. HARD ASSERTION (Keyword: WAJIB) -> STOP
        elif cmd == "assert_hard":
             if not driver.d(textContains=resolved_args[0]).exists and \
               not driver.d(resourceId=resolved_args[0]).exists:
                 # Raise RuntimeError Khusus untuk mematikan program
                 raise RuntimeError(f"CRITICAL CHECK FAILED: '{resolved_args[0]}' WAJIB ADA!")

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
        # [FIX 3] ERROR HANDLING
        
        # Jika Hard Assert (Critical), Lempar ke atas agar program MATI
        if isinstance(e, RuntimeError) and "CRITICAL" in str(e):
            err_path = os.path.join(ctx["ss_dir"], f"FATAL_ERROR_{ctx['step_count']}.png")
            ctx["driver"].take_screenshot(err_path)
            ctx["saga"].add_step(ctx["step_count"], f"[FATAL] {narrative}", ctx["activity"], err_path, [{"status": "FATAL", "msg": str(e)}])
            ctx["mapper"].add_step("FATAL STOP", step_type="danger")
            raise e 
            
        # Jika Soft Assert / Error Biasa, LANJUT
        print(f"⚠️ SOFT FAIL: {e}")
        err_path = os.path.join(ctx["ss_dir"], f"error_step_{ctx['step_count']}.png")
        ctx["driver"].take_screenshot(err_path)
        
        fail_narrative = f"[FAILED] {narrative}"
        ctx["saga"].add_step(ctx["step_count"], fail_narrative, ctx["activity"], err_path, [{"status": "ERROR", "msg": str(e)}])
        ctx["mapper"].add_step(narrative, step_type="error")
        pass # Lanjut ke step berikutnya

if __name__ == "__main__":
    main()