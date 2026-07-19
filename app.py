import sys
import os
import time
import math
import random
import numpy as np
import cv2

# Headless server environment stabilization guard
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av

# ====================================================================
# UNREAL CYBER HUD MINIMALIST VISUAL STYLING
# ====================================================================
st.set_page_config(
    page_title="UNREAL // Vision Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark obsidian, zero-fluff layout targeting high-performance viewport rendering
st.markdown("""
    <style>
    .main {
        background: #050508;
        color: #ffffff;
    }
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    .unreal-header {
        font-family: 'Courier New', monospace;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 6px;
        color: #00ffcc;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
    }
    /* Clean glassmorphic container for select matrix */
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        text-align: center;
        color: #52525b;
        font-family: monospace;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="unreal-header">⚡ UNREAL ENGINE</h1>', unsafe_allow_html=True)
st.markdown('<p>// CORE REAL-TIME AR ARRAYS AVAILABLE</p>', unsafe_allow_html=True)

# ====================================================================
# SESSION MATRIX STORAGE
# ====================================================================
if "day6_nodes" not in st.session_state:
    st.session_state.day6_nodes = []
if "day8_grid" not in st.session_state:
    st.session_state.day8_grid = list(range(9))
    random.shuffle(st.session_state.day8_grid)

# ====================================================================
# REAL-TIME DYNAMIC AR COMPUTE MATRIX FILTERS
# ====================================================================
def filter_day1(img):
    h, w, _ = img.shape
    out = img.copy()
    offset = int(35 * math.sin(time.time() * 5))
    cy, cx = h // 2, w // 2
    cv2.circle(out, (cx, cy + offset), 75, (255, 0, 127), -1)
    cv2.circle(out, (cx, cy + offset), 65, (255, 255, 255), -1)
    cv2.putText(out, "LEVITATION ENGINE ACTIVE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 127), 2, cv2.LINE_AA)
    return out

def filter_day2(img):
    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lines = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    neon_sketch = cv2.cvtColor(lines, cv2.COLOR_GRAY2BGR)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (w // 2, h // 2), 170, 255, -1)
    output = neon_sketch.copy()
    output[mask > 0] = img[mask > 0]
    cv2.circle(output, (w // 2, h // 2), 170, (0, 255, 204), 3, cv2.LINE_AA)
    cv2.putText(output, "TIMELINE BREACH", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 204), 2, cv2.LINE_AA)
    return output

def filter_day3(img):
    h, w, _ = img.shape
    out = img.copy()
    cv2.line(out, (w // 2, h - 20), (w // 2, h - 300), (0, 102, 255), 24, cv2.LINE_AA)
    cv2.line(out, (w // 2, h - 20), (w // 2, h - 300), (255, 255, 255), 8, cv2.LINE_AA)
    cv2.putText(out, "LIGHTSABER CORE LINKED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 102, 255), 2, cv2.LINE_AA)
    return out

def filter_day4(img):
    h, w, _ = img.shape
    tint = np.zeros_like(img)
    tint[:] = [15, 75, 25] 
    mutated_blend = cv2.addWeighted(img, 0.4, tint, 0.6, 0)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask, (w // 4, h // 5), (3 * w // 4, 4 * h // 5), 255, -1)
    out = np.where(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) > 0, mutated_blend, img)
    cv2.putText(out, "GAMMA RADIATION ACTIVE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    return out

def filter_day5(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hud = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    h, w, _ = hud.shape
    cv2.rectangle(hud, (30, 30), (w - 30, h - 30), (0, 255, 255), 1, cv2.LINE_AA)
    cv2.line(hud, (w // 2 - 30, h // 2), (w // 2 + 30, h // 2), (0, 255, 255), 1)
    cv2.line(hud, (w // 2, h // 2 - 30), (w // 2, h // 2 + 30), (0, 255, 255), 1)
    cv2.putText(hud, "E.D.I.T.H OVERRIDE: TARGET ACQUIRED", (50, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
    return hud

def filter_day6(img):
    h, w, _ = img.shape
    out = img.copy()
    t = time.time()
    nx = int(w // 2 + 180 * math.sin(t * 4.0))
    ny = int(h // 2 + 100 * math.cos(t * 2.5))
    st.session_state.day6_nodes.append(((nx, ny), t))
    st.session_state.day6_nodes = [n for n in st.session_state.day6_nodes if t - n[1] < 1.8]
    for i in range(1, len(st.session_state.day6_nodes)):
        p1 = st.session_state.day6_nodes[i-1][0]
        p2 = st.session_state.day6_nodes[i][0]
        cv2.line(out, p1, p2, (255, 0, 255), 4, cv2.LINE_AA)
    cv2.putText(out, "PIXIE DUST TRAIL", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2, cv2.LINE_AA)
    return out

def filter_day7(img):
    h, w, _ = img.shape
    out = img.copy()
    sparkle_map = (np.random.rand(h, w) > 0.988) * 255
    out[sparkle_map > 0] = [255, 255, 255]
    cv2.putText(out, "DIAMOND SKIN SPARKLE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    return out

def filter_day8(img):
    h, w, _ = img.shape
    th, tw = h // 3, w // 3
    out = np.zeros_like(img)
    for index, mapping in enumerate(st.session_state.day8_grid):
        sr, sc = index // 3, index % 3
        dr, dc = mapping // 3, mapping % 3
        out[dr*th:(dr+1)*th, dc*tw:(dc+1)*tw] = img[sr*th:(sr+1)*th, sc*tw:(sc+1)*tw]
        cv2.rectangle(out, (dc*tw, dr*th), ((dc+1)*tw, (dr+1)*th), (20, 20, 20), 1)
    cv2.putText(out, "REALITY MATRIX SHATTERED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 0, 255), 2, cv2.LINE_AA)
    return out

# ====================================================================
# STABLE AR INTERFACE CANVAS INTERACTION LAYER
# ====================================================================
_, center_col, _ = st.columns([1, 4, 1])

with center_col:
    # Minimalist interactive selector replacing buttons to stop the component unmounting crash
    selected_layer = st.selectbox(
        label="[ SELECT ACTIVE MATRIX ARRAY LAYER ]",
        options=["Day 1: Leviosa🛸", "Day 2: Breach🌀", "Day 3: Jedi⚔️", "Day 4: Gamma🦖", "Day 5: E.D.I.T.H🕶️", "Day 6: Pixie✨", "Day 7: Sparkle💎", "Day 8: Shatter🧩"],
        label_visibility="visible"
    )
    
    # Internal text mapping key parser
    layer_map = {
        "Day 1: Leviosa🛸": "day1", "Day 2: Breach🌀": "day2", "Day 3: Jedi⚔️": "day3", 
        "Day 4: Gamma🦖": "day4", "Day 5: E.D.I.T.H🕶️": "day5", "Day 6: Pixie✨": "day6", 
        "Day 7: Sparkle💎": "day7", "Day 8: Shatter🧩": "day8"
    }
    active_matrix = layer_map[selected_layer]

    # Asynchronous pipeline frame routing engine callback
    def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1) # Built-in mirroring
        
        try:
            if active_matrix == "day1": img = filter_day1(img)
            elif active_matrix == "day2": img = filter_day2(img)
            elif active_matrix == "day3": img = filter_day3(img)
            elif active_matrix == "day4": img = filter_day4(img)
            elif active_matrix == "day5": img = filter_day5(img)
            elif active_matrix == "day6": img = filter_day6(img)
            elif active_matrix == "day7": img = filter_day7(img)
            elif active_matrix == "day8": img = filter_day8(img)
        except Exception:
            pass
            
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