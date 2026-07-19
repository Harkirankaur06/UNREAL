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
# HIGH-END LUX DARK GRAPHICS STYLING
# ====================================================================
st.set_page_config(
    page_title="UNREAL // Vision Matrix",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep obsidian neon visual layout overriding standard boring Streamlit views
st.markdown("""
    <style>
    .main {
        background: radial-gradient(circle at center, #0a0512 0%, #020105 100%);
        color: #ffffff;
    }
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    .unreal-header {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(90deg, #00ffcc, #0077ff, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        text-align: center;
    }
    .unreal-tag {
        color: #695e7c;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        text-align: center;
        margin-top: -5px;
        margin-bottom: 30px;
        letter-spacing: 4px;
        text-transform: uppercase;
    }
    /* Elegant Filter Selector Custom Plates */
    .stButton>button {
        background: rgba(255, 255, 255, 0.03);
        color: #a39bb4;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 20px;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        backdrop-filter: blur(10px);
    }
    .stButton>button:hover {
        border-color: #00ffcc;
        color: #00ffcc;
        background: rgba(0, 255, 204, 0.05);
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="unreal-header">⚡ UNREAL</h1>', unsafe_allow_html=True)
st.markdown('<p class="unreal-tag">Real-Time Core Engine Matrix</p>', unsafe_allow_html=True)

# ====================================================================
# SESSION SYSTEM LAYER
# ====================================================================
if "active_matrix" not in st.session_state:
    st.session_state.active_matrix = "day1"
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
# VIDEO FRAME PROCESSING ROUTER LAYER
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    img = cv2.flip(img, 1)
    
    # Thread-safe local proxy lookup to avoid accessing session_state items mid-render
    current_layer = st.session_state.active_matrix
    
    try:
        if current_layer == "day1": img = filter_day1(img)
        elif current_layer == "day2": img = filter_day2(img)
        elif current_layer == "day3": img = filter_day3(img)
        elif current_layer == "day4": img = filter_day4(img)
        elif current_layer == "day5": img = filter_day5(img)
        elif current_layer == "day6": img = filter_day6(img)
        elif current_layer == "day7": img = filter_day7(img)
        elif current_layer == "day8": img = filter_day8(img)
    except Exception:
        pass
        
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ====================================================================
# UNREAL CENTRAL HUB VIEWPORT MOUNT
# ====================================================================
_, center_col, _ = st.columns([1, 5, 1])

with center_col:
    # 1. CAMERA CANVAS MOUNTED AT THE TOP
    webrtc_streamer(
        key="unreal-core-streamer",
        video_frame_callback=process_video_frame,
        sendback_audio=False,
        media_stream_constraints={
            "video": True,  # Hardware-adaptive aspect ratio setup prevents browser channel blocks
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. CONTROL INTERACTION MATRIX PLATES POSITIONED DIRECTLY UNDERNEATH
    matrix_cols = st.columns(8)
    LAYERS = [
        {"id": "day1", "icon": "🛸", "label": "Leviosa"},
        {"id": "day2", "icon": "🌀", "label": "Breach"},
        {"id": "day3", "icon": "⚔️", "label": "Jedi"},
        {"id": "day4", "icon": "🦖", "label": "Gamma"},
        {"id": "day5", "icon": "🕶️", "label": "E.D.I.T.H"},
        {"id": "day6", "icon": "✨", "label": "Pixie"},
        {"id": "day7", "icon": "💎", "label": "Sparkle"},
        {"id": "day8", "icon": "🧩", "label": "Shatter"}
    ]

    for idx, lay in enumerate(LAYERS):
        with matrix_cols[idx]:
            is_active = st.session_state.active_matrix == lay["id"]
            display_text = f"{lay['icon']} {lay['label'].upper()}" if not is_active else f"🌌 {lay['label'].upper()}"
            if st.button(display_text, key=f"btn_{lay['id']}", use_container_width=True):
                st.session_state.active_matrix = lay["id"]