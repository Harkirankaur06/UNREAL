import sys
import os
import time
import math
import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import urllib.request

# Headless server environment stabilization guard
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# ====================================================================
# MEMORY-SAFE RESOURCE CACHING INITIALIZATION
# ====================================================================
@st.cache_resource
def bootstrap_environment():
    """Runs exactly once on startup to protect server RAM and patch environment."""
    HAAR_CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    XML_FILE = "haarcascade_frontalface_default.xml"

    if not os.path.exists(XML_FILE):
        try:
            urllib.request.urlretrieve(HAAR_CASCADE_URL, XML_FILE)
        except Exception:
            pass

    # Patch the cv2 object environment once globally to prevent Day 4 dependency crashes
    if not hasattr(cv2, 'data'):
        class DummyData:
            haarcascades = ""
        cv2.data = DummyData()
    elif not hasattr(cv2.data, 'haarcascades'):
        cv2.data.haarcascades = ""

    cv2.data.haarcascades = "./" if os.path.exists(XML_FILE) else ""
    return True

# Trigger the single-run setup allocation
bootstrap_environment()

# Dynamic runtime import mapping to access your separate day files cleanly
try:
    from day1 import Day1LevitationEngine
except ImportError:
    Day1LevitationEngine = None

try:
    from day4 import process_frame as day4_process
except ImportError:
    day4_process = None

# ====================================================================
# UNREAL ULTRA-CLEAN VIEWPORT STYLING
# ====================================================================
st.set_page_config(
    page_title="UNREAL ENGINE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {
        background: #030305;
        color: #ffffff;
    }
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    .unreal-title {
        font-family: 'Courier New', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 8px;
        color: #00ffcc;
        text-align: center;
        margin-bottom: 0px;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
    }
    .unreal-sub {
        text-align: center;
        color: #4b4b54;
        font-family: monospace;
        font-size: 0.8rem;
        letter-spacing: 2px;
        margin-bottom: 25px;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="unreal-title">⚡ UNREAL</h1>', unsafe_allow_html=True)
st.markdown('<p class="unreal-sub">// CORE PIPELINE INGRESS REGISTER</p>', unsafe_allow_html=True)

# ====================================================================
# PERSISTENT CLASS OBJECT ENGINE INSTANTIATION
# ====================================================================
if "day1_engine" not in st.session_state and Day1LevitationEngine is not None:
    try:
        st.session_state.day1_engine = Day1LevitationEngine()
    except Exception:
        st.session_state.day1_engine = None

# ====================================================================
# CENTRAL VIEWPORT LAYER
# ====================================================================
_, center_viewport, _ = st.columns([1, 4, 1])

with center_viewport:
    # A clear, clean layer selector that routes inputs without dropping connections
    selected_layer = st.selectbox(
        label="[ CHOOSE CORE MATRIX TARGET ]",
        options=[
            "Day 1: Project Wingardium Leviosa 🛸",
            "Day 2: Project Go Home 🌀",
            "Day 3: Project Jedi ⚔️",
            "Day 4: Project Gamma 🦖",
            "Day 5: Project E.D.I.T.H. 🕶️",
            "Day 6: Project Bipity Bopity Boo ✨",
            "Day 7: Project Skin of the Killer 💎",
            "Day 8: Project Shattered Reality 🧩"
        ]
    )
    
    matrix_id = selected_layer.split(":")[0].strip().lower().replace(" ", "")

    # Main non-blocking processing callback engine thread
    def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        
        try:
            # Day 1 Route: Safely feeds image matrix into your class structure
            if matrix_id == "day1" and st.session_state.get("day1_engine") is not None:
                img = st.session_state.day1_engine.process_frame(img)
                
            # Day 4 Route: Feeds image matrix straight to your day4 function
            elif matrix_id == "day4" and day4_process is not None:
                img = day4_process(img)
                
            # Standard Mirror Visual Fallback for unlinked slots
            else:
                img = cv2.flip(img, 1)
                cv2.putText(img, f"{selected_layer.upper()} ACTIVE", (30, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 204), 2, cv2.LINE_AA)
        except Exception as e:
            cv2.putText(img, f"LINK CORE ERROR: {str(e)[:30]}", (20, img.shape[0] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    st.markdown("<br>", unsafe_allow_html=True)

    # WebRTC canvas pipeline utilizing browser-stable connection handshakes
    webrtc_streamer(
        key="unreal-core-streamer",
        video_frame_callback=process_video_frame,
        sendback_audio=False,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        rtc_configuration=RTCConfiguration(
            {"iceServers": [
                {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]},
                {"urls": ["stun:stun2.l.google.com:19302", "stun:stun3.l.google.com:19302"]}
            ]}
        ),
        async_processing=True
    ) 