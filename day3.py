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
saber_ignited = False     

# --- 3D TEMPORAL SMOOTHING STATE TRACKERS ---
smooth_hx, smooth_hy = 0.0, 0.0
smooth_tx, smooth_ty = 0.0, 0.0
smooth_z_scale = 1.0
alpha = 0.20  
first_frame = True
hand_seen = False  

BASE_SHOULDER_WIDTH = 200.0
max_knuckle_reference_dist = 1.0

# NEW: Dynamic Tracking Variables for Overlap Analysis
overlap_state = "Normal"

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
        shoulder_dist_px = int(BASE_SHOULDER_WIDTH)
        
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

        target_z_scale = max(0.3, min(2.5, shoulder_dist_px / BASE_SHOULDER_WIDTH))

        # 3D Spatial Pipeline
        if hand_result and hand_result.hand_landmarks:
            hand_seen = True
            for hand_landmarks in hand_result.hand_landmarks:
                wrist = hand_landmarks[0]
                index_k = hand_landmarks[5]        
                pinky_k = hand_landmarks[17]       
                index_tip, index_pip = hand_landmarks[8], hand_landmarks[6]
                middle_tip, middle_pip = hand_landmarks[12], hand_landmarks[10]

                hand_is_closed = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)
                saber_ignited = True if hand_is_closed else False

                hx_raw = index_k.x * w
                hy_raw = index_k.y * h

                # Knuckle screen distances
                ix_px, iy_px = index_k.x * w, index_k.y * h
                px_px, py_px = pinky_k.x * w, pinky_k.y * h
                current_knuckle_dist = np.sqrt((ix_px - px_px)**2 + (iy_px - py_px)**2)

                if current_knuckle_dist > max_knuckle_reference_dist:
                    max_knuckle_reference_dist = current_knuckle_dist

                foreshortening_factor = max(0.15, min(1.0, current_knuckle_dist / max_knuckle_reference_dist))

                # --- NEW: CORE OVERLAP LOGIC HANDLING ---
                # Detect structural proximity on the 2D plane (Overlap Check)
                is_overlapping = current_knuckle_dist < 18.0  # Threshold gap in pixels

                if is_overlapping:
                    if pinky_k.z < index_k.z:
                        # Green is closer to the screen than Red
                        overlap_state = "Green Overlaps Red"
                    else:
                        # Red is closer to the screen than Green
                        overlap_state = "Red Overlaps Green"
                else:
                    overlap_state = "Normal"

                # Knuckle Vector direction mapping
                v3d_x = index_k.x - pinky_k.x
                v3d_y = index_k.y - pinky_k.y

                mag_2d = np.sqrt(v3d_x**2 + v3d_y**2)
                if mag_2d > 0:
                    v3d_x, v3d_y = v3d_x / mag_2d, v3d_y / mag_2d
                else:
                    v3d_x, v3d_y = 0, -1

                current_growth = min(1.0, current_growth + speed) if saber_ignited else max(0.0, current_growth - speed)

                raw_blade_len_px = h * 0.65 * current_growth * target_z_scale * foreshortening_factor
                tx_raw = hx_raw + (v3d_x * raw_blade_len_px)
                ty_raw = hy_raw + (v3d_y * raw_blade_len_px)

                if first_frame:
                    smooth_hx, smooth_hy = hx_raw, hy_raw
                    smooth_tx, smooth_ty = tx_raw, ty_raw
                    smooth_z_scale = target_z_scale
                    first_frame = False
                else:
                    smooth_hx = smooth_hx * (1 - alpha) + hx_raw * alpha
                    smooth_hy = smooth_hy * (1 - alpha) + hy_raw * alpha
                    smooth_tx = smooth_tx * (1 - alpha) + tx_raw * alpha
                    smooth_ty = smooth_ty * (1 - alpha) + ty_raw * alpha
                    smooth_z_scale = smooth_z_scale * (1 - alpha) + target_z_scale * alpha

                data_string = f"{round(smooth_hx,2)},{round(smooth_hy,2)},{round(smooth_z_scale,4)},{round(current_growth,2)},{shoulder_dist_px}"
                sock.sendto(data_string.encode(), (UDP_IP, UDP_PORT))

                # Diagnostic overlays
                cv2.circle(frame, (int(wrist.x * w), int(wrist.y * h)), 6, (255, 0, 0), cv2.FILLED) 
                cv2.circle(frame, (int(hx_raw), int(hy_raw)), 6, (0, 0, 255), cv2.FILLED)          
                cv2.circle(frame, (int(pinky_k.x * w), int(pinky_k.y * h)), 6, (0, 255, 0), cv2.FILLED) 
                cv2.line(frame, (int(hx_raw), int(hy_raw)), (int(pinky_k.x * w), int(pinky_k.y * h)), (0, 255, 255), 2)
                cv2.line(frame, (int(wrist.x * w), int(wrist.y * h)), (int(hx_raw), int(hy_raw)), (255, 255, 255), 2)
        else:
            if not saber_ignited:
                current_growth = max(0.0, current_growth - speed)
            v_dx = smooth_tx - smooth_hx
            v_dy = smooth_ty - smooth_hy
            mag_smooth = np.sqrt(v_dx**2 + v_dy**2)
            if mag_smooth > 0:
                v_dx, v_dy = v_dx / mag_smooth, v_dy / mag_smooth
            else:
                v_dx, v_dy = 0, -1
            
            decayed_len = h * 0.65 * current_growth * smooth_z_scale
            smooth_tx = smooth_hx + (v_dx * decayed_len)
            smooth_ty = smooth_hy + (v_dy * decayed_len)
            
            data_string = f"{round(smooth_hx,2)},{round(smooth_hy,2)},{round(smooth_z_scale,4)},{round(current_growth,2)},{shoulder_dist_px}"
            sock.sendto(data_string.encode(), (UDP_IP, UDP_PORT))

        # --- CONDITION-BASED VOLUMETRIC RENDERING ---
        if hand_seen and current_growth > 0:
            # Condition 1: Green overlaps Red -> Completely skip rendering loop to hide saber
            if overlap_state == "Green Overlaps Red":
                pass 
                
            # Condition 2: Red overlaps Green -> Render as a singular concentrated dot point
            elif overlap_state == "Red Overlaps Green":
                dot_radius = int(18 * smooth_z_scale)
                cv2.circle(glow_mask, (int(smooth_hx), int(smooth_hy)), dot_radius * 2, blade_color, -1, cv2.LINE_AA)
                cv2.circle(core_mask, (int(smooth_hx), int(smooth_hy)), int(dot_radius * 0.4), (255, 255, 255), -1, cv2.LINE_AA)

            # Condition 3: Normal state -> Render full volumetric 12-segment geometry
            else:
                num_segments = 12
                projected_points = []
                radii = []

                v_dx = smooth_tx - smooth_hx
                v_dy = smooth_ty - smooth_hy
                mag_smooth = np.sqrt(v_dx**2 + v_dy**2)
                if mag_smooth > 0:
                    v_dx, v_dy = v_dx / mag_smooth, v_dy / mag_smooth
                else:
                    v_dx, v_dy = 0, -1

                total_len = np.sqrt((smooth_tx - smooth_hx)**2 + (smooth_ty - smooth_hy)**2)

                for i in range(num_segments + 1):
                    step = (i / num_segments) * total_len
                    scr_x = int(smooth_hx + v_dx * step)
                    scr_y = int(smooth_hy + v_dy * step)
                    projected_points.append((scr_x, scr_y))
                    
                    taper_factor = 1.0 - (i / num_segments) * 0.4
                    seg_rad = int(14 * smooth_z_scale * taper_factor)
                    radii.append(max(2, seg_rad))

                for i in range(num_segments):
                    pt1 = projected_points[i]
                    pt2 = projected_points[i+1]
                    rad = radii[i]
                    cv2.line(glow_mask, pt1, pt2, blade_color, rad * 2, cv2.LINE_AA)
                    cv2.line(core_mask, pt1, pt2, (255, 255, 255), max(1, int(rad * 0.3)), cv2.LINE_AA)

            # High-Speed downscaled Glow Shader step integration
            small_glow = cv2.resize(glow_mask, (w // 4, h // 4), interpolation=cv2.INTER_LINEAR)
            small_blur = cv2.GaussianBlur(small_glow, (9, 9), 0)
            glow_blur = cv2.resize(small_blur, (w, h), interpolation=cv2.INTER_LINEAR)
            
            saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
            frame = cv2.add(frame, saber_composite)

        # Performance State Readouts
        cv2.putText(frame, f"Overlap State: {overlap_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.imshow("Day 3: True 3D Space Projection Pipeline", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()