import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os

# --- MODEL FILE CHECK ---
model_path = "hand_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading hand tracking model file...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)

# Initialize Modern API Structure
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# --- LIGHTSABER CONFIGURATION & STATES ---
current_growth = 0.0     
speed = 0.08             
blade_color = (255, 0, 0) 

# --- NEW: SMOOTHING FILTERS (Prevents Glitching) ---
# We store the previous frame positions to calculate a running average smooth lag
smooth_cx, smooth_cy = 0, 0
smooth_vx, smooth_vy = 0, 0
smooth_z = 0.0
alpha = 0.25  # Smoothing factor (Lower = smoother/slower, Higher = faster/snappier)
first_frame = True

cap = cv2.VideoCapture(0)

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        glow_mask = np.zeros((h, w, 3), dtype=np.uint8)
        core_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # Raw 3D landmarks directly from the tracking engine
                index_k = hand_landmarks[5]        
                pinky_k = hand_landmarks[17]       
                
                index_tip = hand_landmarks[8]
                index_pip = hand_landmarks[6]
                middle_tip = hand_landmarks[12]
                middle_pip = hand_landmarks[10]

                # Target coordinates in pixel space
                ix, iy = int(index_k.x * w), int(index_k.y * h)
                px, py = int(pinky_k.x * w), int(pinky_k.y * h)

                # --- TRIGGER LOGIC ---
                hand_is_closed = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)
                if hand_is_closed:
                    current_growth = min(1.0, current_growth + speed)
                else:
                    current_growth = max(0.0, current_growth - speed)

                # --- 3D VECTOR ORIENTATION MATH ---
                # Calculate direction across knuckles (raw data)
                raw_vx = ix - px
                raw_vy = iy - py
                raw_cx, raw_cy = ix, iy
                raw_z = index_k.z  # Relative depth coordinate estimation

                # --- APPLY SMOOTHING FILTER ---
                if first_frame:
                    smooth_cx, smooth_cy = raw_cx, raw_cy
                    smooth_vx, smooth_vy = raw_vx, raw_vy
                    smooth_z = raw_z
                    first_frame = False
                else:
                    # Exponential Moving Average blending formula: New = Old*(1-A) + Raw*A
                    smooth_cx = int(smooth_cx * (1 - alpha) + raw_cx * alpha)
                    smooth_cy = int(smooth_cy * (1 - alpha) + raw_cy * alpha)
                    smooth_vx = smooth_vx * (1 - alpha) + raw_vx * alpha
                    smooth_vy = smooth_vy * (1 - alpha) + raw_vy * alpha
                    smooth_z = smooth_z * (1 - alpha) + raw_z * alpha

                # Normalize the smoothed 3D direction vectors
                magnitude = np.sqrt(smooth_vx**2 + smooth_vy**2)
                if magnitude > 0:
                    normalized_vx = smooth_vx / magnitude
                    normalized_vy = smooth_vy / magnitude
                else:
                    normalized_vx, normalized_vy = 0, -1

                # --- 3D PERSPECTIVE SCALING ---
                # Base scale modified by the window height
                base_scale = h * 0.65
                
                # We calculate depth scaling. If hand points away/closer, Z changes.
                # Adding depth compensation forces the line drawing engine to adapt to perspective.
                z_depth_scalar = 1.0 - (smooth_z * 2.0)
                scale_factor = base_scale * z_depth_scalar * current_growth
                
                # Project final 3D coordinates onto the flat 2D viewport camera frame
                target_x = int(smooth_cx + normalized_vx * scale_factor)
                target_y = int(smooth_cy + normalized_vy * scale_factor)

                # --- MULTI-PASS GEOMETRIC DRAWING ---
                if current_growth > 0:
                    # Thickness scales dynamically based on spatial depth estimation
                    z_thickness = max(0.5, 1.0 - smooth_z)
                    
                    cv2.line(glow_mask, (smooth_cx, smooth_cy), (target_x, target_y), blade_color, int(28 * z_thickness), cv2.LINE_AA)
                    cv2.line(glow_mask, (smooth_cx, smooth_cy), (target_x, target_y), blade_color, int(12 * z_thickness), cv2.LINE_AA)
                    cv2.line(core_mask, (smooth_cx, smooth_cy), (target_x, target_y), (255, 255, 255), int(6 * z_thickness), cv2.LINE_AA)

        # If hand leaves frame, reset first frame toggle to avoid visual snapping jumps
        else:
            first_frame = True

        # --- IMAGE BLENDING COMPOSITE ---
        glow_blur = cv2.GaussianBlur(glow_mask, (35, 35), 0)
        saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
        frame = cv2.add(frame, saber_composite)

        # Output frame window
        cv2.imshow("Day 3 Challenge: Real-Time Lightsaber Engine", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()