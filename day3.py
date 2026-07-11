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

# --- CORRECTED MODERN TASKS MODELS ---
model_hand = "hand_landmarker.task"
model_pose = "pose_landmarker.task"

# Auto-download modern models with corrected structural paths
if not os.path.exists(model_hand):
    print("Downloading Hand Landmarker...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", model_hand)

if not os.path.exists(model_pose):
    print("Downloading Pose Landmarker (Full)...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task", model_pose)
    print("Download complete!")

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

hand_options = HandLandmarkerOptions(base_options=BaseOptions(model_asset_path=model_hand), running_mode=VisionRunningMode.VIDEO, num_hands=1)
pose_options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model_pose), running_mode=VisionRunningMode.VIDEO)

# --- LIGHTSABER & SMOOTHING CONFIG ---
current_growth = 0.0     
speed = 0.08             
blade_color = (255, 0, 0) # BGR: Vibrant Blue

smooth_cx, smooth_cy = 0, 0
smooth_vx, smooth_vy = 0, 0
smooth_z = 0.0
alpha = 0.25  
first_frame = True

cap = cv2.VideoCapture(0)

print("\n=======================================================")
print("MODERN 3D HOLISTIC (POSE + HAND) LIGHTSABER ENGINE LIVE")
print(f"Streaming data to -> {UDP_IP}:{UDP_PORT}")
print("=======================================================\n")

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
        
        # Run modern parallel inference passes
        pose_result = pose_detector.detect_for_video(mp_image, timestamp_ms)
        hand_result = hand_detector.detect_for_video(mp_image, timestamp_ms)

        # --- 1. FIXED ROOM DEPTH & UPPER BODY ORIENTATION ---
        body_dir = "No Body Detected"
        shoulder_dist_px = 0
        
        if pose_result and pose_result.pose_landmarks:
            for pose_landmarks in pose_result.pose_landmarks:
                # Landmark 11 = Left Shoulder, Landmark 12 = Right Shoulder
                l_shoulder = pose_landmarks[11]
                r_shoulder = pose_landmarks[12]
                
                # Convert normalized coordinates into screen pixel integers
                ls_x, ls_y = int(l_shoulder.x * w), int(l_shoulder.y * h)
                rs_x, rs_y = int(r_shoulder.x * w), int(r_shoulder.y * h)
                
                # Draw structural tracking lines for your upper frame
                cv2.line(frame, (ls_x, ls_y), (rs_x, rs_y), (0, 255, 255), 3)
                cv2.circle(frame, (ls_x, ls_y), 6, (255, 255, 0), cv2.FILLED)
                cv2.circle(frame, (rs_x, rs_y), 6, (255, 255, 0), cv2.FILLED)

                # Calculate screen distance to check if you are moving closer/further
                shoulder_dist_px = int(np.sqrt((rs_x - ls_x)**2 + (rs_y - ls_y)**2))

                # Room depth orientation tracking via Z value deltas
                shoulder_depth_delta = r_shoulder.z - l_shoulder.z
                if shoulder_depth_delta > 0.03:
                    body_dir = "Facing Left"
                elif shoulder_depth_delta < -0.03:
                    body_dir = "Facing Right"
                else:
                    body_dir = "Facing Forward"

        # --- 2. HAND TRACKING & SABER GRAPHICS PIPELINE ---
        if hand_result and hand_result.hand_landmarks:
            for hand_landmarks in hand_result.hand_landmarks:
                index_k = hand_landmarks[5]        # Red Dot
                pinky_k = hand_landmarks[17]       # Green Dot
                index_tip, index_pip = hand_landmarks[8], hand_landmarks[6]
                middle_tip, middle_pip = hand_landmarks[12], hand_landmarks[10]

                ix, iy = int(index_k.x * w), int(index_k.y * h)
                px, py = int(pinky_k.x * w), int(pinky_k.y * h)

                # Grip logic trigger
                hand_is_closed = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)
                if hand_is_closed:
                    current_growth = min(1.0, current_growth + speed)
                else:
                    current_growth = max(0.0, current_growth - speed)

                # Get raw spatial frames
                raw_vx, raw_vy = ix - px, iy - py
                raw_cx, raw_cy = ix, iy
                raw_z = index_k.z  

                # Temporal signal damping
                if first_frame:
                    smooth_cx, smooth_cy = raw_cx, raw_cy
                    smooth_vx, smooth_vy = raw_vx, raw_vy
                    smooth_z = raw_z
                    first_frame = False
                else:
                    smooth_cx = int(smooth_cx * (1 - alpha) + raw_cx * alpha)
                    smooth_cy = int(smooth_cy * (1 - alpha) + raw_cy * alpha)
                    smooth_vx = smooth_vx * (1 - alpha) + raw_vx * alpha
                    smooth_vy = smooth_vy * (1 - alpha) + raw_vy * alpha
                    smooth_z = smooth_z * (1 - alpha) + raw_z * alpha

                magnitude = np.sqrt(smooth_vx**2 + smooth_vy**2)
                if magnitude > 0:
                    normalized_vx, normalized_vy = smooth_vx / magnitude, smooth_vy / magnitude
                else:
                    normalized_vx, normalized_vy = 0, -1

                # Spatial Perspective Scaling Formula (Adjusts length via Z coordinate depth)
                scale_factor = (h * 0.65) * (1.0 - (smooth_z * 2.0)) * current_growth
                target_x = int(smooth_cx + normalized_vx * scale_factor)
                target_y = int(smooth_cy + normalized_vy * scale_factor)

                # Render Blade Geometry
                if current_growth > 0:
                    z_thickness = max(0.5, 1.0 - smooth_z)
                    cv2.line(glow_mask, (smooth_cx, smooth_cy), (target_x, target_y), blade_color, int(28 * z_thickness), cv2.LINE_AA)
                    cv2.line(glow_mask, (smooth_cx, smooth_cy), (target_x, target_y), blade_color, int(12 * z_thickness), cv2.LINE_AA)
                    cv2.line(core_mask, (smooth_cx, smooth_cy), (target_x, target_y), (255, 255, 255), int(6 * z_thickness), cv2.LINE_AA)

                # Hilt diagnostic lines
                cv2.circle(frame, (ix, iy), 6, (0, 0, 255), cv2.FILLED)  
                cv2.circle(frame, (px, py), 6, (0, 255, 0), cv2.FILLED)  
                cv2.line(frame, (ix, iy), (px, py), (0, 255, 255), 2)    

                # Net data frame streaming package (Appends shoulder tracking metrics to string)
                data_string = f"{smooth_cx},{smooth_cy},{round(smooth_z, 4)},{round(current_growth, 2)},{shoulder_dist_px}"
                sock.sendto(data_string.encode(), (UDP_IP, UDP_PORT))
                cv2.putText(frame, f"Stream Data: {data_string}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            first_frame = True
            # Send default string if hand tracking parameters vanish
            sock.sendto(f"0,0,0,0.0,{shoulder_dist_px}".encode(), (UDP_IP, UDP_PORT))

        # --- 3. GRAPHICS BLENDING ENGINE ---
        glow_blur = cv2.GaussianBlur(glow_mask, (35, 35), 0)
        saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
        frame = cv2.add(frame, saber_composite)

        # Dashboard Text HUD readouts
        cv2.putText(frame, f"Saber: {'IGNITED' if current_growth > 0.3 else 'RETRACTED'}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Room Tracking: {body_dir}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow("Day 3 Challenge: Modern Tracking Engine", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()