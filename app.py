import sys
import os

# Headless server display stabilization configuration
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2

# ====================================================================
# 1. PREMIUM PORTAL INTERFACE DESIGN
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
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="app-title">🔮 VISION PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div><span class="badge">30-Day Web-AR & Computer Vision Challenge</span></div>', unsafe_allow_html=True)
st.markdown("---")

# ====================================================================
# 2. CHALLENGE SELECTOR MATRIX MAP
# ====================================================================
CORE_CHALLENGES = {
    "Day 1: Project Wingardium Leviosa 🛸": "day1",
    "Day 2: Project Go Home 🌀": "day2",
    "Day 3: Project Jedi ⚔️": "day3",
    "Day 4: Project Gamma 🦖": "day4",
    "Day 5: Project E.D.I.T.H. 🕶️": "day5",
    "Day 6: Project Bipity Bopity Boo ✨": "day6",
    "Day 7: Project Skin of the Killer 💎": "day7",
    "Day 8: Project Shattered Reality 🧩": "day8",
}

# Sandboxed placeholder extensions for upcoming days
for day in range(9, 31):
    CORE_CHALLENGES[f"Day {day}: Upcoming Active Challenge Slot ⏳"] = f"day{day}"

EXTRA_LAYERS = {
    "Extra: Clean Neon Cake Engine 🎂": "cake",
    "Extra: Chrono-Friction Temporal Water Mirror 🌊": "water effect"
}

ALL_LAYERS = {**CORE_CHALLENGES, **EXTRA_LAYERS}

st.sidebar.markdown("### 🎮 Control Center")
selected_display_name = st.sidebar.selectbox(
    "Select Active Challenge Matrix Layer:",
    list(ALL_LAYERS.keys())
)
active_module_target = ALL_LAYERS[selected_display_name]

# ====================================================================
# 3. STATICS STATIC IMPORT LAYER (Bypasses Reloader Failures)
# ====================================================================
def initialize_engine_instance(name):
    """
    Directly binds and instantiates modules inside the persistent state context
    to completely avoid path resolution drops on Streamlit Cloud servers.
    """
    state_key = f"engine_active_{name}"
    if state_key in st.session_state:
        return st.session_state[state_key]

    try:
        # Import target modules directly from your workspace directory root
        if name == "day1":
            import day1
            instance = day1.Day1LevitationEngine()
        elif name == "day2":
            import day2
            instance = day2.Day2QuantumEngine()
        elif name == "day3":
            import day3
            instance = day3
        elif name == "day4":
            import day4
            instance = day4
        elif name == "day5":
            import day5
            instance = day5
        elif name == "day6":
            import day6
            instance = day6
        elif name == "day7":
            import day7
            instance = day7
        elif name == "day8":
            import day8
            instance = day8
        elif name == "cake":
            import cake
            instance = cake.CakeGlowEngine()
        elif name == "water effect":
            import water_effect
            instance = water_effect
        else:
            return None

        st.session_state[state_key] = instance
        return instance
    except Exception as error_msg:
        st.sidebar.error(f"Module structural link error: {error_msg}")
        return None

# Trigger instantiation immediately
active_engine = initialize_engine_instance(active_module_target)

# ====================================================================
# 4. SIDEBAR LOGIC INTERACT BUTTONS (Day 1 & 2 Only)
# ====================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Live Engine Interactions")

if active_module_target == "day1" and active_engine:
    if st.sidebar.button("1. Lock Clean Background"):
        st.session_state["day1_signal"] = "lock_bg"
    if st.sidebar.button("2. GrabCut Select (Center Frame Bounds)"):
        st.session_state["day1_signal"] = "grabcut"
    if st.sidebar.button("3. Launch Hover Matrix"):
        st.session_state["day1_signal"] = "hover"
    if st.sidebar.button("Reset Dynamic Workspace"):
        st.session_state["day1_signal"] = "reset"

elif active_module_target == "day2" and active_engine:
    if st.sidebar.button("1. Cache Room Empty"):
        st.session_state["day2_signal"] = "lock_bg"
    if st.sidebar.button("2. Trigger Breach (Start Anomaly)"):
        st.session_state["day2_signal"] = "anomaly"
    if st.sidebar.button("Reset Anomaly Registers"):
        st.session_state["day2_signal"] = "reset"

else:
    st.sidebar.info("⚡ Real-time pixel processing layer engaged. No manual control signals required.")

st.sidebar.markdown("---")
st.sidebar.link_button(
    "🔗 Follow My Daily Updates on LinkedIn", 
    "https://www.linkedin.com/in/harkiran-kaur-/",
    use_container_width=True
)

# ====================================================================
# 5. HIGH-SPEED FRAME CONTEXT HANDLING OVERRIDE
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    h, w, _ = img.shape

    if active_engine is not None:
        try:
            # Handle manual state machine injections for Day 1
            if active_module_target == "day1":
                sig = st.session_state.get("day1_signal", None)
                if sig == "lock_bg":
                    active_engine.trigger_bg_lock(img)
                    st.session_state["day1_signal"] = None
                elif sig == "grabcut":
                    active_engine.trigger_grabcut_init(img, (w // 4, h // 4, w // 2, h // 2))
                    st.session_state["day1_signal"] = None
                elif sig == "hover":
                    active_engine.trigger_hover()
                    st.session_state["day1_signal"] = None
                elif sig == "reset":
                    active_engine.trigger_reset()
                    st.session_state["day1_signal"] = None
                
                img = active_engine.process_frame(img)

            # Handle manual state machine injections for Day 2
            elif active_module_target == "day2":
                sig = st.session_state.get("day2_signal", None)
                if sig == "lock_bg":
                    active_engine.lock_clean_background(img)
                    st.session_state["day2_signal"] = None
                elif sig == "anomaly":
                    active_engine.trigger_anomaly()
                    st.session_state["day2_signal"] = None
                elif sig == "reset":
                    active_engine.trigger_reset()
                    st.session_state["day2_signal"] = None
                
                img = active_engine.process_frame(img)

            # Route Cake engine class instance parameters
            elif active_module_target == "cake":
                img = active_engine.process_frame(img)

            # Route functional code frames straight to global execution channels
            else:
                for hook_fn in ["process_frame", "apply_filter", "process", "filter"]:
                    if hasattr(active_engine, hook_fn):
                        img = getattr(active_engine, hook_fn)(img)
                        break
        except Exception as runtime_error:
            # Prevent frame loop breakage on errors: write trace debug to output canvas
            cv2.putText(img, f"RUNTIME ENG ERR: {str(runtime_error)[:30]}", (20, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

    else:
        # Code asset file path check backup prompt screen
        cv2.putText(img, f"PORTAL LAYER: {selected_display_name.split(':')[0]}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 2)
        cv2.putText(img, f"Awaiting code deployment for mapping keyword '{active_module_target}.py'", (20, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ====================================================================
# 6. WebRTC CANVAS MOUNT ENGINE LAYER WITH NATIVE RECORDER
# ====================================================================
col_video, col_docs = st.columns([2, 1])

with col_video:
    st.markdown("#### 📽️ Live AR Canvas Feed")
    webrtc_streamer(
        key="vision-portal-streamer",
        video_frame_callback=process_video_frame,
        sendback_audio=False,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
                "facingMode": "user",
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
    *   **Architecture:** Explicit component mapping structure built to guarantee bulletproof cloud application runtimes.
    *   **State Machine Bridges:** Context variables and interactions safely isolated behind side-panel buttons strictly on designated challenge scopes.
    *   **Zero-Lag Capture Architecture:** High frame rate rendering profiles allowing effortless local screen captures or desktop media generation.
    """)

st.markdown("---")
st.markdown("🤖 *Developed under the **Vision Portal Framework Architecture Blueprint** Portfolio Module.*")