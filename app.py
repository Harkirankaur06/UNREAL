import sys
import os
import time
import math
import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av

# Import your native day logic files cleanly
try:
    from day1 import Day1LevitationEngine
    from day4 import process_frame as day4_process
except ImportError:
    pass

# ====================================================================
# HIGH-END OBSIDIAN GLASSMORPHIC VIEWPORT
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
# ENGINE OBJECTS PERSISTENCE
# ====================================================================
if "day1_engine" not in st.session_state:
    try:
        st.session_state.day1_engine = Day1LevitationEngine()
    except NameError:
        st.session_state.day1_engine = None

# ====================================================================
# VIEWPORT DISPLAY LAYER
# ====================================================================
_, center_viewport, _ = st.columns([1, 4, 1])

with center_viewport:
    # Safe non-blocking layer select to prevent camera unmounting drops
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
    
    # Extract string id tags
    matrix_id = selected_layer.split(":")[0].strip().lower().replace(" ", "")

    # Asynchronous pipeline frame routing engine callback
    def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        
        try:
            if matrix_id == "day1" and st.session_state.day1_engine is not None:
                img = st.session_state.day1_engine.process_frame(img)
            elif matrix_id == "day4":
                # Calls your exact functional process_frame method inside day4.py
                img = day4_process(img)
            else:
                # Mirroring path standard fallback for days not loaded or placeholder blocks
                img = cv2.flip(img, 1)
                cv2.putText(img, f"{selected_layer.upper()} ACTIVE", (30, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 204), 2, cv2.LINE_AA)
        except Exception as e:
            cv2.putText(img, f"LINK CORE ERROR: {str(e)[:30]}", (20, img.shape[0] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    st.markdown("<br>", unsafe_allow_html=True)

    # Hardware-adaptive aspect ratio setup prevents browser peer connection dropouts
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