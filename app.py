import streamlit as st
import subprocess
import os
import sys
import pandas as pd
import altair as alt
from PIL import Image
import re
import time
import tkinter as tk
from tkinter import filedialog

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Heimdall Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:first-child {
        background-color: #0051a2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'scenario_path' not in st.session_state:
    st.session_state['scenario_path'] = os.path.join(os.getcwd(), "scenarios")

# --- FUNGSI UTAMA ---

def select_folder():
    try:
        root = tk.Tk()
        root.withdraw() 
        root.wm_attributes('-topmost', 1) 
        folder_selected = filedialog.askdirectory(master=root)
        root.destroy()
        return folder_selected
    except:
        return None

def get_connected_devices():
    try:
        startupinfo = None
        if os.name == 'nt': 
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.check_output(["adb", "devices"], startupinfo=startupinfo).decode("utf-8")
        lines = result.strip().split("\n")[1:]
        devices = [line.split("\t")[0] for line in lines if "device" in line]
        return devices if devices else ["No Device Found"]
    except FileNotFoundError:
        return ["ADB Not Installed"]
    except Exception as e:
        return [f"ADB Error: {str(e)}"]

def get_scenarios(base_path):
    scenarios = []
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".heim"):
                    full_path = os.path.join(root, file)
                    scenarios.append(full_path)
    return sorted(scenarios)

def parse_log_line(line):
    step_match = re.search(r'\[Step (\d+)\]> (.*)', line)
    if step_match:
        return {"step": step_match.group(1), "desc": step_match.group(2), "status": "Running"}
    if "!!! ERROR" in line or "Critical Failure" in line:
        return {"status": "Fail"}
    return None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/viking-helmet.png", width=70)
    st.title("HEIMDALL")
    st.caption("v1.0 - Hybrid Edition")
    st.divider()

    st.subheader("📱 Device Manager")
    devices = get_connected_devices()
    selected_device = st.radio("Target Device:", devices)
    
    if st.button("🔄 Refresh Devices"):
        st.rerun()

    st.divider()

    st.subheader("📂 Scenario Source")
    st.caption(f"Path: ...{str(st.session_state['scenario_path'])[-25:]}")
    
    if st.button("📂 Ganti Folder Scenario"):
        new_folder = select_folder()
        if new_folder:
            st.session_state['scenario_path'] = new_folder
            st.rerun()

    heim_files = get_scenarios(st.session_state['scenario_path'])
    if heim_files:
        format_func = lambda x: os.path.basename(x)
        selected_scenario = st.selectbox("Pilih File Test:", heim_files, format_func=format_func)
    else:
        st.warning(f"Tidak ada file .heim di folder ini.")
        selected_scenario = None

    st.divider()
    show_logs = st.checkbox("Show Live Logs", value=True)

# --- MAIN AREA ---

st.title("🚀 Control Center")

c1, c2, c3 = st.columns(3)
c1.metric("Selected Scenario", os.path.basename(selected_scenario) if selected_scenario else "-")
c2.metric("Target Device", selected_device)
status_metric = c3.empty()
status_metric.metric("Status", "Ready")

st.divider()

# --- EKSEKUSI ---
if st.button("▶️ MULAI TEST SEKARANG"):
    if not selected_device or "Error" in selected_device or "No Device" in selected_device:
        st.error(f"❌ Error Device: {selected_device}")
    elif not selected_scenario:
        st.error("❌ Pilih skenario terlebih dahulu!")
    else:
        status_metric.metric("Status", "Running...", delta_color="off")
        
        log_expander = st.expander("Terminal Logs", expanded=show_logs)
        log_container = log_expander.empty()
        
        full_logs = []
        step_data = [] 
        failed_flag = False

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # [FIX HYBRID LOGIC]
        # Cek apakah kita sedang jalan sebagai Portable (.exe) atau Script Biasa (.py)
        if getattr(sys, 'frozen', False):
            # Mode Portable: Panggil diri sendiri sebagai worker
            cmd = [sys.executable, "worker", selected_scenario]
        else:
            # Mode Dev: Panggil main.py langsung via python interpreter
            cmd = [sys.executable, "main.py", selected_scenario]

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                bufsize=1,
                startupinfo=startupinfo,
                env=env
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    clean_line = line.strip()
                    full_logs.append(clean_line)
                    log_container.code("\n".join(full_logs[-12:]), language="bash")
                    
                    parsed = parse_log_line(clean_line)
                    if parsed:
                        if "step" in parsed:
                            if step_data and step_data[-1]['Status'] == "Running":
                                step_data[-1]['Status'] = "Pass"
                            
                            step_data.append({
                                "Step": f"Step {parsed['step']}",
                                "Description": parsed['desc'],
                                "Status": "Running"
                            })
                        
                        if parsed.get("status") == "Fail":
                            failed_flag = True
                            if step_data: step_data[-1]['Status'] = "Fail"

            if step_data and step_data[-1]['Status'] == "Running":
                step_data[-1]['Status'] = "Pass" if not failed_flag else "Fail"

            if process.returncode == 0 and not failed_flag:
                st.success("✅ Testing Selesai: SUKSES")
                status_metric.metric("Status", "Completed", delta="Success")
            else:
                st.error("❌ Testing Selesai: GAGAL")
                status_metric.metric("Status", "Failed", delta="-Error", delta_color="inverse")

            st.divider()
            st.subheader("📊 Executive Summary")
            
            df_steps = pd.DataFrame(step_data)
            if not df_steps.empty:
                pass_count = len(df_steps[df_steps['Status'] == 'Pass'])
                fail_count = len(df_steps[df_steps['Status'] == 'Fail'])
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    chart_data = pd.DataFrame({'Status': ['Pass', 'Fail'], 'Count': [pass_count, fail_count]})
                    base = alt.Chart(chart_data).encode(theta=alt.Theta("Count", stack=True))
                    pie = base.mark_arc(outerRadius=100).encode(
                        color=alt.Color("Status", scale=alt.Scale(domain=['Pass', 'Fail'], range=['#2ecc71', '#e74c3c'])),
                        tooltip=["Status", "Count"]
                    )
                    # [FIX DEPRECATION] Ganti use_column_width jadi use_container_width
                    st.altair_chart(pie, use_container_width=True)

                with c2:
                    st.write("**Detail Execution:**")
                    st.dataframe(df_steps, use_container_width=True, hide_index=True)

            st.divider()
            scenario_name = os.path.splitext(os.path.basename(selected_scenario))[0]
            report_dir = os.path.join("reports", scenario_name)
            
            t1, t2 = st.tabs(["🗺️ Flowchart", "📥 Download Report"])
            
            with t1:
                flow_img = os.path.join(report_dir, "flowchart.png")
                if os.path.exists(flow_img):
                    image = Image.open(flow_img)
                    # [FIX DEPRECATION] Ganti use_column_width jadi use_container_width
                    st.image(image, caption="Visual Logic Flow", use_container_width=True)
                else:
                    st.warning("Flowchart tidak tersedia.")
                    
            with t2:
                doc_path = os.path.join(report_dir, f"Heimdall_Saga_{scenario_name}.docx")
                if os.path.exists(doc_path):
                    with open(doc_path, "rb") as file:
                        st.download_button(
                            label="📄 Download Laporan Word",
                            data=file,
                            file_name=f"Report_{scenario_name}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
        except Exception as e:
            st.error(f"Execution Error: {e}")