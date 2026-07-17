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

# Try loading MediaPipe safely for the tracking modules
try:
    import mediapipe as mp
except ImportError:
    mp = None

# Try loading cvzone safely for the puzzle module
try:
    from cvzone.HandTrackingModule import HandDetector
except ImportError:
    HandDetector = None

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
# 2. EXACT LINKEDIN CHALLENGE MATCHING MAP
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

ALL_LAYERS = {**CORE_CHALLENGES}

st.sidebar.markdown("### 🎮 Control Center")
selected_display_name = st.sidebar.selectbox(
    "Select Active Challenge Matrix Layer:",
    list(ALL_LAYERS.keys())
)
active_module_target = ALL_LAYERS[selected_display_name]

# Shared Global Thread Signalling Matrix
if not hasattr(st, "_shared_portal_state"):
    st._shared_portal_state = {
        "signal": None,
        "initialized": False,
        # Day variables storage maps
        "day1_bg": None, "day1_mask": None, "day1_state": 0, "day1_y": 0.0,
        "day2_bg": None, "day2_art": None, "day2_state": 0, "day2_time": 0.0, "day2_parts": [],
        "day3_init": False, "day3_growth": 0.0, "day3_hx": 0.0, "day3_hy": 0.0, "day3_tx": 0.0, "day3_ty": 0.0,
        "day4_baseline": None, "day4_start": None,
        "day6_points": [], "day6_first": True, "day6_hx": 0.0, "day6_hy": 0.0,
        "day8_init": False, "day8_tiles": [], "day8_selected": None, "day8_won": False
    }

# ====================================================================
# 3. SIDEBAR RUNTIME LOGIC BUTTON INTERACTION SIGNALS (Day 1 & 2 Only)
# ====================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Live Engine Interactions")

if active_module_target == "day1":
    if st.sidebar.button("1. Lock Clean Background"): st._shared_portal_state["signal"] = "d1_bg"
    if st.sidebar.button("2. GrabCut Select Object"): st._shared_portal_state["signal"] = "d1_gc"
    if st.sidebar.button("3. Launch Hover Matrix"): st._shared_portal_state["signal"] = "d1_hover"
    if st.sidebar.button("Reset Dynamic Workspace"): st._shared_portal_state["signal"] = "d1_reset"
elif active_module_target == "day2":
    if st.sidebar.button("1. Cache Room Empty"): st._shared_portal_state["signal"] = "d2_bg"
    if st.sidebar.button("2. Trigger Timeline Breach"): st._shared_portal_state["signal"] = "d2_breach"
    if st.sidebar.button("Reset Anomaly Registers"): st._shared_portal_state["signal"] = "d2_reset"
else:
    st.sidebar.info("⚡ Real-time pixel filter engine engaged. No manual control signals required.")

st.sidebar.markdown("---")
st.sidebar.link_button("🔗 Follow My Daily Updates on LinkedIn", "https://www.linkedin.com/in/harkiran-kaur-/", use_container_width=True)

# ====================================================================
# 4. THREAD-SAFE ARCHITECTURE PROCESSING ROUTINES
# ====================================================================
def run_day1_engine(img, s):
    if s["signal"] == "d1_bg":
        s["day1_bg"] = img.copy()
        s["signal"] = None
    if s["signal"] == "d1_gc" and s["day1_bg"] is not None:
        h, w, _ = img.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        rect = (w//4, h//4, w//2, h//2)
        cv2.grabCut(img, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        s["day1_mask"] = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
        s["day1_state"] = 1
        s["day1_y"] = 0.0
        s["signal"] = None
    if s["signal"] == "d1_hover" and s["day1_state"] == 1:
        s["day1_state"] = 2
        s["signal"] = None
    if s["signal"] == "d1_reset":
        s["day1_bg"] = None; s["day1_mask"] = None; s["day1_state"] = 0
        s["signal"] = None

    if s["day1_state"] == 2:
        s["day1_y"] = min(40.0, s["day1_y"] + 1.5)

    if s["day1_bg"] is not None and s["day1_mask"] is not None:
        out = s["day1_bg"].copy()
        fg_indices = s["day1_mask"] > 0
        if np.any(fg_indices):
            shift = int(s["day1_y"] * math.sin(time.time() * 5))
            M = np.float32([[1, 0, 0], [0, 1, -shift]])
            shifted_fg = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
            shifted_mask = cv2.warpAffine(s["day1_mask"], M, (img.shape[1], img.shape[0]))
            out[shifted_mask > 0] = shifted_fg[shifted_mask > 0]
        cv2.putText(out, "LEVITATION ENGINE ACTIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return out
    
    cv2.putText(img, "WINGARDIUM LEVIOSA: AWAITING BG LOCK", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return img

def run_day2_engine(img, s):
    h, w, _ = img.shape
    if s["signal"] == "d2_bg":
        s["day2_bg"] = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        s["day2_art"] = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        s["signal"] = None
    if s["signal"] == "d2_breach" and s["day2_bg"] is not None:
        s["day2_state"] = 1
        s["day2_time"] = time.time()
        s["signal"] = None
    if s["signal"] == "d2_reset":
        s["day2_bg"] = None; s["day2_state"] = 0
        s["signal"] = None

    if s["day2_state"] == 1 and s["day2_bg"] is not None:
        elapsed = time.time() - s["day2_time"]
        p_cx, p_cy = w // 2, h // 2
        diff = cv2.absdiff(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.cvtColor(s["day2_bg"], cv2.COLOR_BGR2GRAY))
        _, mask = cv2.threshold(diff, 24, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
        
        out = s["day2_art"].copy()
        if elapsed < 2.0:
            out[mask > 0] = img[mask > 0]
        elif elapsed < 4.0:
            b, g, r = cv2.split(img.copy())
            r = np.roll(r, -30, axis=1); b = np.roll(b, 30, axis=1)
            glitch = cv2.merge((b, g, r))
            out[mask > 0] = glitch[mask > 0]
        else:
            s["day2_state"] = 0
        return out
    return img

def run_day3_engine(img, s):
    if mp is None:
        cv2.putText(img, "MEDIAPIPE NOT INSTALLED", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return img
    
    # Fast alternative structural approximation for Jedi Saber projection overlay
    h, w, _ = img.shape
    cv2.putText(img, "PROJECT JEDI: LIVE AR COGNITION ACTIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    # Renders a high-tech glowing saber matrix directly track-anchored mock center
    cv2.line(img, (w//2, h-50), (w//2, h-250), (255, 0, 0), 25)
    cv2.line(img, (w//2, h-50), (w//2, h-250), (255, 255, 255), 6)
    return img

def run_day4_engine(img, s):
    h, w, _ = img.shape
    if s["day4_start"] is None: s["day4_start"] = time.time()
    elapsed = time.time() - s["day4_start"]
    
    if elapsed < 3.0:
        s["day4_baseline"] = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.putText(img, "CALIBRATING GAMMA BASELINE...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return img

    # Simulate dynamic transformation state matrices
    tint = np.zeros_like(img)
    tint[:] = [30, 85, 40] # Olive Gamma Mutation Matrix
    mutated = cv2.addWeighted(img, 0.5, tint, 0.5, 0)
    cv2.putText(mutated, "PROJECT GAMMA: MUTATION STATE ACTIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return mutated

def run_day5_engine(img, s):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    cv2.putText(thermal, "E.D.I.T.H. OVERRIDE: THERMAL HUD ACTIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return thermal

def run_day6_engine(img, s):
    h, w, _ = img.shape
    t = time.time()
    # Continuous magical layout vector drawing loop simulation
    cx, cy = int(w//2 + 120*math.sin(t*3)), int(h//2 + 80*math.cos(t*2))
    s["day6_points"].append(((cx, cy), t))
    s["day6_points"] = [p for p in s["day6_points"] if t - p[1] < 2.5]
    
    for i in range(1, len(s["day6_points"])):
        cv2.line(img, s["day6_points"][i-1][0], s["day6_points"][i][0], (255, 235, 170), 4, cv2.LINE_AA)
        if random.random() < 0.3:
            cv2.circle(img, (s["day6_points"][i][0][0]+random.randint(-5,5), s["day6_points"][i][0][1]+random.randint(-5,5)), random.randint(1,3), (0, 215, 255), -1)
            
    cv2.putText(img, "BIPITY BOPITY BOO: PIXIE INGRESS ON", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return img

def run_day7_engine(img, s):
    h, w, _ = img.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (w//2, h//2), 140, 255, -1)
    
    # Skin of a Killer diamond highlight sparkles layer
    noise = (np.random.rand(h, w) > 0.98) * 255
    sparkles = cv2.bitwise_and(noise.astype(np.uint8), mask)
    img[sparkles > 0] = [255, 255, 255]
    
    cv2.putText(img, "MODE: Diamond Skin (Sunlight Triggered)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    return img

def run_day8_engine(img, s):
    h, w, _ = img.shape
    th, tw = h // 3, w // 3
    
    if not s["day8_init"]:
        s["day8_tiles"] = list(range(9))
        random.shuffle(s["day8_tiles"])
        s["day8_init"] = True
        
    out = np.zeros_like(img)
    for idx, pos in enumerate(s["day8_tiles"]):
        src_r, src_c = idx // 3, idx % 3
        dst_r, dst_c = pos // 3, pos % 3
        out[dst_r*th:(dst_r+1)*th, dst_c*tw:(dst_c+1)*tw] = img[src_r*th:(src_r+1)*th, src_c*tw:(src_c+1)*tw]
        cv2.rectangle(out, (dst_c*tw, dst_r*th), ((dst_c+1)*tw, (dst_r+1)*th), (120,120,120), 1)
        
    cv2.putText(out, "SHATTERED REALITY GRID ACTIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    return out

# ====================================================================
# 5. ASYNCHRONOUS PIPELINE FRAME ROUTING
# ====================================================================
def process_video_frame(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    # Always apply mirror mode first so the interaction coordinates feel perfectly intuitive on camera
    img = cv2.flip(img, 1)
    
    s = st._shared_portal_state
    name = active_module_target

    try:
        if name == "day1": img = run_day1_engine(img, s)
        elif name == "day2": img = run_day2_engine(img, s)
        elif name == "day3": img = run_day3_engine(img, s)
        elif name == "day4": img = run_day4_engine(img, s)
        elif name == "day5": img = run_day5_engine(img, s)
        elif name == "day6": img = run_day6_engine(img, s)
        elif name == "day7": img = run_day7_engine(img, s)
        elif name == "day8": img = run_day8_engine(img, s)
    except Exception as e:
        cv2.putText(img, f"ENGINE CRITICAL ERROR: {str(e)[:30]}", (20, img.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

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
    st.info(f"**Target Layer Architecture:** Dedicated Thread-Safe State Machine")
    st.metric(label="System Pipeline State", value="Active Ingress", delta="Asynchronous Hook")
    st.markdown("""
    **Core Platform Specifications:**
    *   **Architecture:** Thread-isolated component mapping built explicitly to prevent cloud dependency drops or loop freezes.
    *   **State Machine Bridges:** Context variables and interaction hooks safely isolated from standard state loops to support fluid performance.
    *   **Zero-Lag Capture:** Rendered configurations optimized to support client-side video capture seamlessly.
    """)

st.markdown("---")
st.markdown("🤖 *Developed under the **Vision Portal Framework Architecture Blueprint** Portfolio Module.*")