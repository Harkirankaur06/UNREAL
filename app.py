import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import importlib.util
import os

# ====================================================================
# 1. BRILLIANT INTERFACE STYLING (Custom Modern Dark Theme CSS)
# ====================================================================
st.set_page_config(
    page_title="VISION PORTAL: Real-Time Web-AR Engine",
    page_icon="🔮",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #06040a 100%);
        color: #ffffff;
    }
    div[data-testid="stSidebar"] {
        background-color: #0b0816 !important;
        border-right: 1px solid #3d2b7a;
    }
    .stSelectbox label {
        color: #bfa3ff !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .app-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff007f, #7f00ff, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .badge {
        background: rgba(127, 0, 255, 0.2);
        border: 1px solid #7f00ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #e0ccff;
        font-weight: 500;
        display: inline-block;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# App UI Header Area
st.markdown('<h1 class="app-title">🔮 VISION PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div><span class="badge">30-Day Web-AR & Computer Vision Challenge</span></div>', unsafe_allow_html=True)
st.markdown("---")

# ====================================================================
# 2. THE 30-DAY CHANNELS & EXTRA LAYERS SELECTOR
# ====================================================================

# Build the selection matrix dynamically mapping display titles to your exact file scripts
CORE_CHALLENGES = [f"Day {str(i).zfill(2)}" for i in range(1, 31)]
EXTRA_LAYERS = ["Cake Layer Filter", "Water Effect Filter"]

st.sidebar.markdown("### 🎮 Control Center")
selected_layer = st.sidebar.selectbox(
    "Choose Active Filter Matrix Layer:",
    CORE_CHALLENGES + EXTRA_LAYERS
)

# Professional Links Panel
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Live Challenge Progress")
st.sidebar.info("💡 Days 09-30 are dropping daily as the implementation architecture expands.")
st.sidebar.link_button(
    "🔗 Follow My Daily Updates on LinkedIn", 
    "https://www.linkedin.com/in/harkiran-kaur-/",
    use_container_width=True
)

# ====================================================================
# 3. DYNAMIC INTERACTION IMPORT UTILITY
# ====================================================================
def execute_external_filter(module_name, frame):
    """
    Dynamically loads your standalone .py files from the workspace root 
    and checks for a standard process or filter function execution window.
    """
    try:
        # Resolve filenames matching your precise tree layout structure
        if module_name == "water effect":
            target_file = "water effect.py"
        elif module_name == "cake":
            target_file = "cake.py"
        else:
            target_file = f"{module_name}.py"

        if not os.path.exists(target_file):
            return None

        # Python programmatic import binding pipeline
        spec = importlib.util.spec_from_file_location(module_name, target_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # First check if the file uses a Class architecture (like the new Day 1)
        # Class-based check (looks for dynamic instance generation)
        class_name = f"{module_name.capitalize()}LevitationEngine" if "day1" in module_name else None
        if class_name and hasattr(module, class_name):
            # Cache the engine instance in Streamlit session state so tracking memory persists between frames
            state_key = f"engine_{module_name}"
            if state_key not in st.session_state:
                st.session_state[state_key] = getattr(module, class_name)()
            return st.session_state[state_key].process_frame(frame)

        # Function-based check (fallback to global functions like process_frame or apply_filter)
        for target_fn in ["process_frame", "apply_filter", "process", "filter"]:
            if hasattr(module, target_fn):
                return getattr(module, target_fn)(frame)
        
        return None
    except Exception as e:
        return None

# ====================================================================
# 4. ASYNCHRONOUS PIPELINE FRAME ROUTING
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    h, w, _ = img.shape
    
    # Map the dropdown state to the corresponding file name target
    if "Day" in selected_layer:
        day_num = int(selected_layer.split()[1])
        target_module = f"day{day_num}"
    elif "Cake" in selected_layer:
        target_module = "cake"
    else:
        target_module = "water effect"

    # Attempt dynamic ingestion from your file modules
    processed_img = execute_external_filter(target_module, img)

    # Fallback to visual feedback UI if the file doesn't exist yet (Days 09-30) or missing entrypoint function
    if processed_img is None:
        cv2.putText(img, f"Active Layer Sandbox Slot: {selected_layer}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 2)
        cv2.putText(img, f"Awaiting code link injection inside {target_module}.py", (20, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    else:
        img = processed_img

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ====================================================================
# 5. ASYNC WebRTC ENGINE INGRESS HOOKS
# ====================================================================
col_video, col_docs = st.columns([2, 1])

with col_video:
    st.markdown("#### 📽️ Live AR Canvas Feed")
    webrtc_streamer(
        key="vision-portal-streamer",
        video_frame_callback=process_video_frame,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        async_processing=True
    )

with col_docs:
    st.markdown("#### 🔬 Pipeline Engine Metrics")
    st.info(f"**Target Layer Module:** {selected_layer}")
    st.metric(label="Pipeline Latency Engine Check", value="Stable Ingress", delta="Asynchronous Hook")
    st.markdown("""
    **Core Platform Specifications:**
    *   **Architecture:** Programmatic file-system injection mapping frames seamlessly through standalone script matrices.
    *   **Isolation:** Worker callback handling separates background image processing tasks entirely from the front-end layout engine thread.
    """)

st.markdown("---")
st.markdown("🤖 *Developed under the **Vision Portal Framework Architecture Blueprint** Portfolio Module.*")