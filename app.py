import streamlit as st
import subprocess
import os
import pandas as pd
import altair as alt
from PIL import Image
import re
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Heimdall Web Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #0051a2;
        color: white;
        height: 3em;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI UTAMA ---

def get_connected_devices():
    try:
        result = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        lines = result.strip().split("\n")[1:]
        devices = [line.split("\t")[0] for line in lines if "device" in line]
        return devices if devices else ["No Device Found"]
    except:
        return ["ADB Error"]

def get_scenarios():
    scenarios = []
    if os.path.exists("scenarios"):
        for root, dirs, files in os.walk("scenarios"):
            for file in files:
                if file.endswith(".heim"):
                    full_path = os.path.join(root, file)
                    scenarios.append(full_path)
    return sorted(scenarios)

def parse_log_line(line):
    """Membaca baris log untuk mengekstrak Step dan Status"""
    step_match = re.search(r'\[Step (\d+)\]> (.*)', line)
    if step_match:
        # Return lowercase keys for internal logic
        return {"step": step_match.group(1), "desc": step_match.group(2), "status": "Running"}
    
    if "!!! ERROR" in line or "Critical Failure" in line:
        return {"status": "Fail"}
    
    return None

# --- LAYOUT: SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/viking-helmet.png", width=70)
    st.title("HEIMDALL")
    st.caption("v1.0 - Automation Platform")
    st.divider()

    st.subheader("📱 Device Manager")
    devices = get_connected_devices()
    selected_device = st.radio("Target Device:", devices)
    
    if st.button("🔄 Refresh Devices"):
        st.rerun()

    st.divider()

    st.subheader("📜 Scenario Selector")
    heim_files = get_scenarios()
    if heim_files:
        selected_scenario = st.selectbox("Pilih Skenario Test:", heim_files)
    else:
        st.warning("Tidak ada file .heim di folder scenarios/")
        selected_scenario = None

    st.divider()
    show_logs = st.checkbox("Show Live Logs", value=True)

# --- LAYOUT: MAIN AREA ---

st.title("🚀 Control Center")

col1, col2, col3 = st.columns(3)
col1.metric("Selected Scenario", os.path.basename(selected_scenario) if selected_scenario else "-")
col2.metric("Target Device", selected_device)
status_metric = col3.empty()
status_metric.metric("Status", "Ready")

st.divider()

# --- EKSEKUSI ---
if st.button("▶️ MULAI TEST SEKARANG"):
    if selected_device == "No Device Found":
        st.error("❌ Hubungkan HP terlebih dahulu!")
    elif not selected_scenario:
        st.error("❌ Pilih skenario terlebih dahulu!")
    else:
        status_metric.metric("Status", "Running...", delta_color="off")
        
        log_expander = st.expander("Terminal Logs", expanded=show_logs)
        log_container = log_expander.empty()
        
        full_logs = []
        step_data = [] 
        failed_flag = False

        # Command dengan python -u (Unbuffered)
        cmd = ["python", "-u", "main.py", selected_scenario]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            bufsize=1
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
                    # Logic: Jika ketemu Step baru, step sebelumnya dianggap Pass
                    if "step" in parsed:
                        if step_data:
                            # [FIX] Gunakan 'Status' (Huruf Besar)
                            if step_data[-1]['Status'] == "Running":
                                step_data[-1]['Status'] = "Pass"
                        
                        # [FIX] Gunakan Key 'Status' (Huruf Besar) konsisten
                        step_data.append({
                            "Step": f"Step {parsed['step']}",
                            "Description": parsed['desc'],
                            "Status": "Running" 
                        })
                    
                    # Logic: Jika ketemu Error, step terakhir jadi Fail
                    if parsed.get("status") == "Fail":
                        failed_flag = True
                        if step_data:
                            # [FIX] Gunakan 'Status' (Huruf Besar)
                            step_data[-1]['Status'] = "Fail"

        # Finalisasi status step terakhir setelah loop selesai
        if step_data:
            # [FIX] Gunakan 'Status' (Huruf Besar)
            if step_data[-1]['Status'] == "Running":
                step_data[-1]['Status'] = "Pass" if not failed_flag else "Fail"

        # --- HASIL AKHIR ---
        if process.returncode == 0 and not failed_flag:
            st.success("✅ Testing Selesai: SUKSES")
            status_metric.metric("Status", "Completed", delta="Success")
        else:
            st.error("❌ Testing Selesai: GAGAL")
            status_metric.metric("Status", "Failed", delta="-Error", delta_color="inverse")

        # --- REPORTING DASHBOARD ---
        st.divider()
        st.subheader("📊 Executive Summary")
        
        df_steps = pd.DataFrame(step_data)
        if not df_steps.empty:
            # Hitung statistik dari kolom 'Status' (Huruf Besar)
            pass_count = len(df_steps[df_steps['Status'] == 'Pass'])
            fail_count = len(df_steps[df_steps['Status'] == 'Fail'])
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                chart_data = pd.DataFrame({
                    'Status': ['Pass', 'Fail'],
                    'Count': [pass_count, fail_count]
                })
                base = alt.Chart(chart_data).encode(theta=alt.Theta("Count", stack=True))
                pie = base.mark_arc(outerRadius=100).encode(
                    color=alt.Color("Status", scale=alt.Scale(domain=['Pass', 'Fail'], range=['#2ecc71', '#e74c3c'])),
                    tooltip=["Status", "Count"]
                )
                text = base.mark_text(radius=120).encode(
                    text="Count", order=alt.Order("Status"), color=alt.value("black")  
                )
                st.altair_chart(pie + text, use_container_width=True)

            with c2:
                st.write("**Detail Execution:**")
                st.dataframe(
                    df_steps, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Result",
                            help="Pass or Fail",
                            validate="^(Pass|Fail)$"
                        )
                    }
                )

        # --- DOWNLOADS ---
        st.divider()
        scenario_name = os.path.splitext(os.path.basename(selected_scenario))[0]
        report_dir = os.path.join("reports", scenario_name)
        
        t1, t2 = st.tabs(["🗺️ Flowchart", "📥 Download Report"])
        
        with t1:
            flow_img = os.path.join(report_dir, "flowchart.png")
            if os.path.exists(flow_img):
                image = Image.open(flow_img)
                st.image(image, caption="Visual Logic Flow", use_column_width=True)
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