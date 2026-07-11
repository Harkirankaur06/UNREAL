import cv2
import mediapipe as mp
import numpy as np
import socket
import urllib.request
import os

# --- NETWORK CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- MODERN TASKS MODELS ---
model_hand = "hand_landmarker.task"
model_pose = "pose_landmarker.task"

if not os.path.exists(model_hand):
    print("Downloading Hand Landmarker...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", model_hand)

if not os.path.exists(model_pose):
    print("Downloading Pose Landmarker (Full)...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task", model_pose)

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

hand_options = HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=model_hand), running_mode=VisionRunningMode.VIDEO, num_hands=1)
pose_options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model_pose), running_mode=VisionRunningMode.VIDEO)

# --- LIGHTSABER CONFIGURATION ---
current_growth = 0.0     
speed = 0.08             
blade_color = (255, 0, 0) # BGR: Blue

# --- 3D TEMPORAL SMOOTHING STATE TRACKERS ---
smooth_hx, smooth_hy, smooth_hz = 0.0, 0.0, 0.0
smooth_tx, smooth_ty, smooth_tz = 0.0, 0.0, 0.0
alpha = 0.20  
first_frame = True

cap = cv2.VideoCapture(0)

with HandLandmarker.create_from_options(hand_options) as hand_detector, \
     PoseLandmarker.create_from_options(pose_options) as pose_detector:
     
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
        
        pose_result = pose_detector.detect_for_video(mp_image, timestamp_ms)
        hand_result = hand_detector.detect_for_video(mp_image, timestamp_ms)

        # Torso Horizon Tracker
        body_dir = "No Body Detected"
        shoulder_dist_px = 0
        if pose_result and pose_result.pose_landmarks:
            for pose_landmarks in pose_result.pose_landmarks:
                l_shoulder = pose_landmarks[11]
                r_shoulder = pose_landmarks[12]
                ls_x, ls_y = int(l_shoulder.x * w), int(l_shoulder.y * h)
                rs_x, rs_y = int(r_shoulder.x * w), int(r_shoulder.y * h)
                cv2.line(frame, (ls_x, ls_y), (rs_x, rs_y), (0, 255, 255), 2)
                shoulder_dist_px = int(np.sqrt((rs_x - ls_x)**2 + (rs_y - ls_y)**2))
                
                if (r_shoulder.z - l_shoulder.z) > 0.03: body_dir = "Facing Left"
                elif (r_shoulder.z - l_shoulder.z) < -0.03: body_dir = "Facing Right"
                else: body_dir = "Facing Forward"

        # 3D Spatial Pipeline
        if hand_result and hand_result.hand_landmarks:
            for hand_landmarks in hand_result.hand_landmarks:
                wrist = hand_landmarks[0]
                index_k = hand_landmarks[5]        # Red Dot (Hilt Base)
                pinky_k = hand_landmarks[17]       # Green Dot
                index_tip, index_pip = hand_landmarks[8], hand_landmarks[6]
                middle_tip, middle_pip = hand_landmarks[12], hand_landmarks[10]

                # Switch Check (Closed Fist Trigger)
                hand_is_closed = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)
                current_growth = min(1.0, current_growth + speed) if hand_is_closed else max(0.0, current_growth - speed)

                # Base Hilt Coordinates
                hx_raw, hy_raw, hz_raw = index_k.x * w, index_k.y * h, index_k.z
                
                # --- FIXED: DIRECT VECTOR MATH ALONG FIST TRACK LINE ---
                # Raw directional path vector in 3D: Pinky directly to Index Knuckle
                v3d_x = index_k.x - pinky_k.x
                v3d_y = index_k.y - pinky_k.y
                v3d_z = index_k.z - pinky_k.z

                # Normalize the 3D Vector components to keep distances stable
                mag_3d = np.sqrt(v3d_x**2 + v3d_y**2 + v3d_z**2)
                if mag_3d > 0:
                    v3d_x, v3d_y, v3d_z = v3d_x / mag_3d, v3d_y / mag_3d, v3d_z / mag_3d

                # Project coordinates forward based on screen scale variables
                raw_blade_len_px = h * 0.65 * current_growth
                tx_raw = hx_raw + (v3d_x * raw_blade_len_px)
                ty_raw = hy_raw + (v3d_y * raw_blade_len_px)
                tz_raw = hz_raw + (v3d_z * 0.5) 

                # Temporal Damping Pass
                if first_frame:
                    smooth_hx, smooth_hy, smooth_hz = hx_raw, hy_raw, hz_raw
                    smooth_tx, smooth_ty, smooth_tz = tx_raw, ty_raw, tz_raw
                    first_frame = False
                else:
                    smooth_hx = smooth_hx * (1 - alpha) + hx_raw * alpha
                    smooth_hy = smooth_hy * (1 - alpha) + hy_raw * alpha
                    smooth_hz = smooth_hz * (1 - alpha) + hz_raw * alpha
                    
                    smooth_tx = smooth_tx * (1 - alpha) + tx_raw * alpha
                    smooth_ty = smooth_ty * (1 - alpha) + ty_raw * alpha
                    smooth_tz = smooth_tz * (1 - alpha) + tz_raw * alpha

                # Perspective Scaling Projection Transforms
                focal_factor = 2.0 
                scale_h = 1.0 / (1.0 + (smooth_hz * focal_factor))
                scale_t = 1.0 / (1.0 + (smooth_tz * focal_factor))
                
                render_hx = int(w / 2 + (smooth_hx - w / 2) * scale_h)
                render_hy = int(h / 2 + (smooth_hy - h / 2) * scale_h)
                render_tx = int(w / 2 + (smooth_tx - w / 2) * scale_t)
                render_ty = int(h / 2 + (smooth_ty - h / 2) * scale_t)

                thickness_base = int(max(6, 24 * scale_h))

                # Render Blade Geometry
                if current_growth > 0:
                    cv2.line(glow_mask, (render_hx, render_hy), (render_tx, render_ty), blade_color, thickness_base, cv2.LINE_AA)
                    cv2.line(core_mask, (render_hx, render_hy), (render_tx, render_ty), (255, 255, 255), int(thickness_base * 0.25), cv2.LINE_AA)

                # Diagnostic anchors
                cv2.circle(frame, (int(index_k.x * w), int(index_k.y * h)), 6, (0, 0, 255), cv2.FILLED)  
                cv2.circle(frame, (int(pinky_k.x * w), int(pinky_k.y * h)), 6, (0, 255, 0), cv2.FILLED)  
                cv2.line(frame, (int(index_k.x * w), int(index_k.y * h)), (int(pinky_k.x * w), int(pinky_k.y * h)), (0, 255, 255), 2)

                # Package data to transmit over network stack
                data_string = f"{round(smooth_hx,2)},{round(smooth_hy,2)},{round(smooth_hz,4)},{round(current_growth,2)},{shoulder_dist_px}"
                sock.sendto(data_string.encode(), (UDP_IP, UDP_PORT))
        else:
            first_frame = True
            sock.sendto(f"0,0,0,0.0,{shoulder_dist_px}".encode(), (UDP_IP, UDP_PORT))

        # Composite Blending
        glow_blur = cv2.GaussianBlur(glow_mask, (35, 35), 0)
        saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
        frame = cv2.add(frame, saber_composite)

        cv2.putText(frame, f"Room Alignment: {body_dir}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.imshow("Day 3: True 3D Space Projection Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()