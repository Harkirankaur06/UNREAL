import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import importlib.util
import os
import sys

# ====================================================================
# 1. PREMIUM INTERFACE DESIGN (Mobile-Responsive Layout)
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
    iframe, video {
        border-radius: 12px;
        border: 1px solid #3d2b7a;
        max-width: 100% !important;
        height: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="app-title">🔮 VISION PORTAL</h1>', unsafe_allow_html=True)
st.markdown('<div><span class="badge">30-Day Web-AR & Computer Vision Challenge</span></div>', unsafe_allow_html=True)
st.markdown("---")

# ====================================================================
# 2. EXACT LINKEDIN CHALLENGE MATCHING MATRIX
# ====================================================================
CORE_CHALLENGES = {
    "Day 1: Continuous Live Isolation Studio 🛸": "day1",
    "Day 2: Quantum Collapse Anomaly / Timeline Breach 🌀": "day2",
    "Day 3: True 3D Space Projection Saber Pipeline ⚔️": "day3",
    "Day 4: Robust Expression Trigger / Hulk Mutation Matrix 🦖": "day4",
    "Day 5: Smart Thermal Toggle / Stark HUD Active 🕶️": "day5",
    "Day 6: Disney Sparkle Wand / Pixie Dust Trail Pipeline ✨": "day6",
    "Day 7: Twilight Vampire Skin / Sunlight Shimmer Trigger 💎": "day7",
    "Day 8: Live Cam Swap Grid Puzzle Game 🧩": "day8",
}

# Auto-generate placeholders for the upcoming sandbox challenge spaces
for day in range(9, 31):
    CORE_CHALLENGES[f"Day {day}: Upcoming Sandbox Active Slot ⏳"] = f"day{day}"

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
# 3. RUNTIME GLOBAL CACHE LOAD MANAGER (Fixes Script Crashes)
# ====================================================================
def get_or_load_module(module_name):
    """
    Safely imports the standalone files once per selection and caches their 
    execution states so tracking matrices do not drop between frames.
    """
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

        # Dynamic Engine Instance Factory mapping (Day 1, 2 & Cake rely on classes)
        engine_instance = None
        if module_name == "day1" and hasattr(module, "Day1LevitationEngine"):
            engine_instance = getattr(module, "Day1LevitationEngine")()
        elif module_name == "day2" and hasattr(module, "Day2QuantumEngine"):
            engine_instance = getattr(module, "Day2QuantumEngine")()
        elif module_name == "cake" and hasattr(module, "CakeGlowEngine"):
            engine_instance = getattr(module, "CakeGlowEngine")()

        # Save class engine reference or fall back straight to function references
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

    # Retrieve cached execution handle context
    loaded_asset = get_or_load_module(active_module_target)
    processed_img = None

    if loaded_asset is not None:
        try:
            # Route 1: Class-based frame mutation loops (.process_frame)
            if hasattr(loaded_asset, "process_frame"):
                processed_img = loaded_asset.process_frame(img)
            # Route 2: Global function-based hook loops (process_frame/apply_filter)
            else:
                for target_fn in ["process_frame", "apply_filter", "process", "filter"]:
                    if hasattr(loaded_asset, target_fn):
                        processed_img = getattr(loaded_asset, target_fn)(img)
                        break
        except Exception:
            pass

    if processed_img is None:
        # Fallback layer screen if target script asset is missing or empty
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