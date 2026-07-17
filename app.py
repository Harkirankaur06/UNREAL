import sys
import os

# Headless server environment stabilization guard
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import importlib.util

# ====================================================================
# 1. PREMIUM INTERFACE DESIGN (Clean Sidebar and Typography)
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
# 2. MATCHED LINKEDIN CHALLENGE INDEX MAP
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Live Challenge Progress")
st.sidebar.info("💡 Days 09-30 are dropping daily as the implementation architecture expands on LinkedIn.")
st.sidebar.link_button(
    "🔗 Follow My Daily Updates on LinkedIn", 
    "https://www.linkedin.com/in/harkiran-kaur-/",
    use_container_width=True
)

# ====================================================================
# 3. RUNTIME GLOBAL CACHE DISPATCH ENGINE
# ====================================================================
def get_or_load_module(module_name):
    state_key = f"mod_{module_name}"
    if state_key in st.session_state:
        return st.session_state[state_key]

    target_file = f"{module_name}.py"
    if not os.path.exists(target_file):
        return None

    try:
        spec = importlib.util.spec_from_file_location(module_name, target_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        engine_instance = None
        if module_name == "day1" and hasattr(module, "Day1LevitationEngine"):
            engine_instance = getattr(module, "Day1LevitationEngine")()
        elif module_name == "day2" and hasattr(module, "Day2QuantumEngine"):
            engine_instance = getattr(module, "Day2QuantumEngine")()
        elif module_name == "cake" and hasattr(module, "CakeGlowEngine"):
            engine_instance = getattr(module, "CakeGlowEngine")()

        st.session_state[state_key] = engine_instance if engine_instance else module
        return st.session_state[state_key]
    except Exception:
        return None

# ====================================================================
# 4. ASYNCHRONOUS PIPELINE FRAME ROUTING
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    h, w, _ = img.shape

    loaded_asset = get_or_load_module(active_module_target)
    processed_img = None

    if loaded_asset is not None:
        try:
            if hasattr(loaded_asset, "process_frame"):
                processed_img = loaded_asset.process_frame(img)
            else:
                for target_fn in ["process_frame", "apply_filter", "process", "filter"]:
                    if hasattr(loaded_asset, target_fn):
                        processed_img = getattr(loaded_asset, target_fn)(img)
                        break
        except Exception:
            pass

    if processed_img is None:
        cv2.putText(img, f"Active Sandbox Slot: {selected_display_name.split(':')[0]}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 240, 255), 2)
        cv2.putText(img, f"Awaiting script linkage inside {active_module_target}.py", (20, h - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    else:
        img = processed_img

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ====================================================================
# 5. WebRTC HARDWARE LOOP
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
    *   **Architecture:** Dynamic module compilation isolation, keeping separate tracking coordinates safely contained.
    *   **Hardware Interface Optimization:** Explicit video tracking constraints designed to secure stable connection authorization loops on iOS/Android mobile architectures.
    *   **Isolation Architecture:** Heavy frame processing operations offloaded asynchronously to background worker loops to prevent UI stutters.
    """)

st.markdown("---")
st.markdown("🤖 *Developed under the **Vision Portal Framework Architecture Blueprint** Portfolio Module.*")