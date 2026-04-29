import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import time
from datetime import datetime
from src.core.processor import SecurityVisionController

# --- Page Configuration ---
st.set_page_config(
    page_title="GuardianEye Biometric Security",
    page_icon="🛡️",
    layout="wide",
)

# --- Initialization ---
# This unified app imports the core engine directly (No need to run API separately)
@st.cache_resource
def get_controller():
    return SecurityVisionController()

controller = get_controller()

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stButton>button { width: 100%; border-radius: 5px; height: 50px; font-weight: bold; }
    .status-verified { color: #238636; font-weight: bold; }
    .status-critical { color: #da3633; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://img.icons8.com/plasticine/200/secure.png", width=100)
st.sidebar.title("GuardianEye v3.0")
st.sidebar.markdown("*Alpha-Grade Biometric Security*")

menu = st.sidebar.radio("Navigation", ["🔍 Live Scan / Analysis", "📜 Event Records", "👥 Profile Management"])

# --- Data Management (Sidebar) ---
st.sidebar.divider()
st.sidebar.write("⚠️ **Danger Zone**")
if st.sidebar.button("🗑️ Clear All Events", use_container_width=True):
    import shutil
    if os.path.exists("data/events"): shutil.rmtree("data/events")
    os.makedirs("data/events")
    st.sidebar.success("Event logs deleted.")
    st.rerun()

if st.sidebar.button("💀 Reset All Profiles", use_container_width=True):
    profiles_path = "data/profiles/profiles.json"
    if os.path.exists(profiles_path):
        with open(profiles_path, "w") as f: json.dump({}, f)
    # --- IMPORTANT: Tell CACHED controller to reload memory ---
    controller.db.reload()
    st.sidebar.success("Biometric database wiped.")
    st.rerun()
# ---------------------------------

# --- Helper Functions ---
def load_events():
    history = []
    log_dir = "data/events"
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith(".json"):
                with open(os.path.join(log_dir, f), "r") as f_in:
                    history.append(json.load(f_in))
    
    if not history: return []
    
    # Flatten metrics for easy CSV/Dataframe handling
    flat_history = []
    for event in history:
        item = event.copy()
        metrics = item.pop('metrics', {})
        for k, v in metrics.items():
            item[f"biometric_{k}"] = v
        flat_history.append(item)
        
    df = pd.DataFrame(flat_history)
    # ⚖️ Clean numerical data for Zero Error reporting
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    return df.to_dict('records') # Convert back to list for existing logic

# --- MAIN UI ---
if menu == "🔍 Live Scan / Analysis":
    st.header("🔍 New Biometric Scan")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Config & Hardware")
        scan_mode = st.radio("Operation Mode", ["Verification (Check ID)", "Enrollment (New Person Entry)"], index=0)
        is_registration = (scan_mode == "Enrollment (New Person Entry)")
        
        cred_id = st.text_input("Target Credential ID", placeholder="e.g. CEO_OFFICE_01")
        door_id = st.selectbox("Hardware Access Point", ["FRONT_GATE", "SECURE_VAULT", "GENERAL_OFFICE"])
        
        st.divider()
        st.write("**🎥 Video Input Stream**")
        source_type = st.radio("Stream Source", ["Local File (Real CCTV)", "Manual Upload"])
        
        video_source = None
        if source_type == "Local File (Real CCTV)":
            video_source = st.text_input("CCTV Full Path", placeholder="data/test_clips/person_a.mp4")
        else:
            uploaded_file = st.file_uploader("Upload Fragment", type=['mp4', 'avi'])
            if uploaded_file:
                temp_path = os.path.join("data", "live_stream.mp4")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                video_source = temp_path
        
        st.divider()
        if st.button("🚀 INITIATE BIOMETRIC SCAN"):
            # Load current profiles to check availability
            profiles_path = "data/profiles/profiles.json"
            profiles = {}
            if os.path.exists(profiles_path):
                with open(profiles_path, "r") as f: profiles = json.load(f)

            if not cred_id or not video_source:
                st.error("Credential ID and Video Source are required.")
            elif not is_registration and cred_id not in profiles:
                st.warning(f"⚠️ TARGET CREDENTIAL ID '{cred_id}' DOES NOT EXIST.")
                st.info("This user has not been enrolled yet. Please switch to 'Enrollment (New Person Entry)' mode first to store their baseline metrics.")
            else:
                with st.status("🔍 Processing Biometric DNA...", expanded=True) as status:
                    st.write("Initializing YOLOv11-Pose Engine...")
                    try:
                        analysis = controller.process_video_window(video_source, cred_id, door_id, is_registration=is_registration)
                        analysis['timestamp'] = time.time()
                        
                        # Save Event Log
                        log_dir = "data/events"
                        if not os.path.exists(log_dir): os.makedirs(log_dir)
                        log_path = os.path.join(log_dir, f"event_{int(time.time())}_{cred_id}.json")
                        with open(log_path, "w") as f_log:
                            save_data = analysis.copy()
                            if "frame" in save_data: del save_data["frame"]
                            json.dump(save_data, f_log, indent=4)
                        
                        st.session_state['latest_analysis'] = analysis
                        status.update(label="✅ Analysis Success!", state="complete", expanded=False)
                        st.balloons()
                    except Exception as e:
                        st.error(f"Critical System Fault: {str(e)}")
                        status.update(label="❌ Analysis Failed", state="error")

    with col2:
        st.subheader("Analysis Output")
        if 'latest_analysis' in st.session_state:
            result = st.session_state['latest_analysis']
            
            # --- Status Header ---
            status_color = "#238636" if result['flag'] == "VERIFIED" else "#da3633"
            st.markdown(f"""
                <div style="background-color:{status_color}; padding:20px; border-radius:10px; text-align:center; margin-bottom:20px;">
                    <h2 style="color:white; margin:0;">{result['flag']}</h2>
                    <p style="color:white; margin:0; opacity:0.8;">Confidence: {round(result['confidence']*100, 1)}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- Video Preview ---
            st.write("**🎞️ Annotated Skeletal Review**")
            if result.get('evidence_video') and os.path.exists(result['evidence_video']):
                st.video(result['evidence_video'])
            
            # --- Metrics & Analysis Details ---
            st.write("**📡 Biometric DNA Breakdown**")
            m_df = pd.DataFrame(list(result['metrics'].items()), columns=['Measurement', 'Detected Value'])
            st.table(m_df)
            
            mcol1, mcol2 = st.columns(2)
            with mcol1: st.metric("Overall Match Confidence", f"{round(result.get('confidence', 0)*100, 1)}%")
            with mcol2: st.info(f"**Security Note:** {result.get('reason', 'N/A')}")
        else:
            st.info("Input a video and ID to begin the automated verification process.")

elif menu == "📜 Event Records":
    st.header("📜 Historical Verification Log")
    events = load_events()
    
    if not events:
        st.warning("No events found in the database. Perform a Live Scan to generate logs.")
    else:
        df = pd.DataFrame(events)
        # Summary Table
        st.write("### All Access Events")
        
        def highlight_mismatch(val):
            if val == "CRITICAL_MISMATCH": return 'color: #da3633; font-weight: bold;'
            if val == "VERIFIED": return 'color: #238636; font-weight: bold;'
            return 'color: #ffcc00;'

        cols_to_show = ['timestamp', 'cred_id', 'flag', 'confidence', 'biometric_estimated_height', 'biometric_torso_leg_ratio']
        existing_cols = [c for c in cols_to_show if c in df.columns]
        display_df = df[existing_cols].copy()
        
        # Safe Timestamp Parsing (Handles NaN/missing values)
        if 'timestamp' in display_df.columns:
            display_df = display_df.dropna(subset=['timestamp']) 
            display_df['DisplayTime'] = display_df['timestamp'].apply(
                lambda x: datetime.fromtimestamp(float(x)).strftime('%m-%d %H:%M:%S') if pd.notna(x) else "Unknown"
            )
        
        st.dataframe(display_df.style.map(highlight_mismatch, subset=['flag'] if 'flag' in display_df.columns else []), use_container_width=True)
        
        # CSV Export
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📤 Download Record as CSV", csv, "guardian_eye_log.csv", "text/csv")
        
        st.divider()
        st.subheader("Event Deep-Dive")
        
        if not display_df.empty:
            selected_time = st.selectbox("Select Event Time to Review Evidence", display_df['DisplayTime'].unique())
            
            # SAFE LOOKUP: Match by DisplayTime
            try:
                evt_data = next(e for e in events if datetime.fromtimestamp(e.get('timestamp', 0)).strftime('%m-%d %H:%M:%S') == selected_time)
                
                dcol1, dcol2 = st.columns([1, 1])
                with dcol1:
                    st.write("**📡 Captured Metrics**")
                    # Dynamically filter for biometric metrics only
                    metric_view = {k.replace('biometric_', ''):v for k,v in evt_data.items() if 'biometric_' in k}
                    st.json(metric_view)
                with dcol2:
                    if evt_data.get('evidence_video'):
                        st.video(evt_data['evidence_video'])
            except Exception as e:
                st.error(f"Error accessing detailed record: {e}")

elif menu == "👥 Profile Management":
    st.header("👥 Authorized Personnel Profiles")
    
    profiles_path = "data/profiles/profiles.json"
    if os.path.exists(profiles_path):
        with open(profiles_path, "r") as f:
            profiles = json.load(f)
            
        if not profiles:
            st.info("No biometric profiles registered yet.")
        else:
            for pid, pdata in profiles.items():
                with st.expander(f"Profile: {pid} ({pdata['entry_count']} entries)"):
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        st.write("**Baseline Metrics**")
                        st.json(pdata['metrics'])
                    with p_col2:
                        # Simple build description logic
                        h = pdata['metrics']['estimated_height']
                        build = "Average" if 0.2 < pdata['metrics']['frame_index'] < 0.4 else "Stocky/Wide" if pdata['metrics']['frame_index'] >= 0.4 else "Slender"
                        st.markdown(f"**Identified Build:** {build}")
                        st.markdown(f"**Stored Height:** {round(h, 1)} cm")
    else:
        st.error("Profile database not initialized.")
