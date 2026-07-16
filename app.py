import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import importlib.util
import os
import sys

# ====================================================================
# 1. PREMIUM INTERFACE DESIGN (Mobile-Responsive Glassmorphism)
# ====================================================================
st.set_page_config(
    page_title="VISION PORTAL: Real-Time Web-AR Engine",
    page_icon="🔮",
    layout="wide"
)

st.markdown("""
    <style>
    /* Global Background Grade */
    .main {
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #06040a 100%);
        color: #ffffff;
    }
    /* Control Panel Alignment */
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
        font-size: 2.5rem;
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
    /* Mobile Video Wrapper Optimization and Mirroring Layout */
    iframe, video {
        border-radius: 12px;
        border: 1px solid #3d2b7a;
        max-width: 100% !important;
        height: auto !important;
        transform: scaleX(-1); /* Ensures true mirror viewport rendering across mobile browsers */
    }
    </style>
""", unsafe_allow_html=True)

# App UI Header Area
st.markdown('<h1 class="app-title">🔮 VISION PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div><span class="badge">30-Day Web-AR & Computer Vision Challenge</span></div>', unsafe_allow_html=True)
st.markdown("---")

# ====================================================================
# 2. THE COMPLETE CHALLENGE MATRIX MATRIX SELECTOR
# ====================================================================
CORE_CHALLENGES = {
    "Day 01: Continuous Live Isolation 🛸": "day1",
    "Day 02: Quantum Collapse Anomaly 🌀": "day2",
    "Day 03: True 3D Projective Saber ⚔️": "day3",
    "Day 04: Facial Expression Hulk Morph 🦖": "day4",
    "Day 05: Smart Thermal Toggle HUD 🕶️": "day5",
    "Day 06: Magical Pixie Sparkle Wand ✨": "day6",
    "Day 07: Sunlight Vampire Shimmer 💎": "day7",
    "Day 08: Live Cam Swap Grid Puzzle 🧩": "day8",
}

# Automatically populate slots for the remaining upcoming slots (9 to 30)
for day in range(9, 31):
    day_str = str(day).zfill(2)
    CORE_CHALLENGES[f"Day {day_str}: Sandbox Active Slot ⏳"] = f"day{day}"

EXTRA_LAYERS = {
    "Extra: Glassmorphic Cake Engine 🎂": "cake",
    "Extra: Chrono-Friction Temporal Mirror 🌊": "water effect"
}

ALL_LAYERS = {**CORE_CHALLENGES, **EXTRA_LAYERS}

st.sidebar.markdown("### 🎮 Control Center")
selected_display_name = st.sidebar.selectbox(
    "Select Active Challenge Matrix Layer:",
    list(ALL_LAYERS.keys())
)
active_module_target = ALL_LAYERS[selected_display_name]

# Professional Links Panel
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Live Challenge Progress")
st.sidebar.info("💡 Days 09-30 are dropping daily as the implementation architecture expands on LinkedIn.")
st.sidebar.link_button(
    "🔗 Follow My Daily Updates on LinkedIn", 
    "https://www.linkedin.com/in/harkiran-kaur-/",
    use_container_width=True
)

# ====================================================================
# 3. INTERACTIVE RELIABLE DYNAMIC DISPATCH ENGINE
# ====================================================================
def execute_external_filter(module_name, img_matrix):
    """
    Safely executes dynamic file loads while keeping internal math arrays 
    completely clean and separated.
    """
    try:
        target_file = f"{module_name}.py"
        if not os.path.exists(target_file):
            return None

        spec = importlib.util.spec_from_file_location(module_name, target_file)
        module = importlib.util.module_from_spec(spec)
        
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Handle Class-based instances (like Day 1 & Day 2) seamlessly via persistent memory state
        class_name = None
        if module_name == "day1": class_name = "Day1LevitationEngine"
        elif module_name == "day2": class_name = "Day2QuantumEngine"
        elif module_name == "cake": class_name = "CakeGlowEngine"
        
        if class_name and hasattr(module, class_name):
            state_key = f"inst_{module_name}"
            if state_key not in st.session_state:
                st.session_state[state_key] = getattr(module, class_name)()
            return st.session_state[state_key].process_frame(img_matrix)

        # Handle structural function execution layers (Day 3 through Day 8, water effect)
        if hasattr(module, "process_frame"):
            return getattr(module, "process_frame")(img_matrix)
            
        for target_fn in ["apply_filter", "process", "filter", "main"]:
            if hasattr(module, target_fn):
                return getattr(module, target_fn)(img_matrix)

        return None
    except Exception as e:
        return None

# ====================================================================
# 4. ASYNCHRONOUS PIPELINE FRAME ROUTING
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    # Pass the raw camera feed straight into your files.
    # Your files mirror the image internally, so we don't mess up their coordinates!
    img = frame.to_ndarray(format="bgr24")
    h, w, _ = img.shape

    processed_img = execute_external_filter(active_module_target, img)

    if processed_img is None:
        # Fallback interface layer if file is completely missing or empty
        cv2.putText(img, f"Active Sandbox Slot: {selected_display_name.split(':')[0]}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 2)
        cv2.putText(img, f"Awaiting script linkage injection inside {active_module_target}.py", (20, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        # Apply mirror inversion fallback display strictly to placeholder screens
        img = cv2.flip(img, 1)
    else:
        img = processed_img

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ====================================================================
# 5. MOBILE-STABILIZED WebRTC HARDWARE INTEGRATION LOOP
# ====================================================================
col_video, col_docs = st.columns([2, 1])

with col_video:
    st.markdown("#### 📽️ Live AR Canvas Feed")
    
    webrtc_streamer(
        key="vision-portal-streamer",
        video_frame_callback=process_video_frame,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
                "facingMode": "user",  # Forces mobile browsers to open front selfie camera immediately
                "frameRate": {"ideal": 30}
            },
            "audio": False
        },
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}]}
        ),
        async_processing=True
    )

with col_docs:
    st.markdown("#### 🔬 Pipeline Engine Metrics")
    st.info(f"**Target Layer Module:** `{active_module_target}.py`")
    st.metric(label="System Pipeline State", value="Active Ingress", delta="Asynchronous Hook")
    st.markdown("""
    **Core Platform Specifications:**
    *   **Architecture:** Dynamic module compilation isolation, keeping separate tracking coordinates safely contained.
    *   **Mobile Engine Layout:** Automated layout alignment styling ensuring clean rendering dimensions across iOS/Android browsers.
    *   **Isolation Architecture:** Heavy frame processing operations offloaded asynchronously to background worker loops to prevent UI stutters.
    """)

st.markdown("---")
st.markdown("🤖 *Developed under the **Vision Portal Framework Architecture Blueprint** Portfolio Module.*")