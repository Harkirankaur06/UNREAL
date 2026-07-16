import cv2
import mediapipe as mp
import numpy as np
import random
import os
import time
import urllib.request

# --- DETECTOR SETUP ---
model_hand = "hand_landmarker.task"
if not os.path.exists(model_hand):
    print("Downloading Hand Landmarker...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", model_hand)

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_hand), 
    running_mode=VisionRunningMode.VIDEO, 
    num_hands=1
)

# --- DISNEY TRAIL TRACKING STATE REGISTER ---
drawing_points = []
LIFETIME = 5.0  # Trail persistence duration (5 seconds)

smooth_hx, smooth_hy = 0.0, 0.0
alpha = 0.20  
first_frame = True

# ====================================================================
# STREAMLIT COMPATIBILITY HOOK (DO NOT TOUCH ORIGINAL LOGIC)
# ====================================================================
def process_frame(incoming_frame):
    global smooth_hx, smooth_hy, first_frame, drawing_points
    
    if not hasattr(process_frame, "hand_detector"):
        process_frame.hand_detector = HandLandmarker.create_from_options(hand_options)
        
    frame = cv2.flip(incoming_frame, 1)
    h, w, c = frame.shape
    current_time = time.time()
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    timestamp_ms = int(time.time() * 1000)
    
    hand_result = process_frame.hand_detector.detect_for_video(mp_image, timestamp_ms)
    
    hand_seen = False
    hx_raw, hy_raw = 0.0, 0.0

    if hand_result and hand_result.hand_landmarks and len(hand_result.hand_landmarks) > 0:
        hand_seen = True
        for hand_landmarks in hand_result.hand_landmarks:
            wrist = hand_landmarks[0]
            index_k = hand_landmarks[5]        
            pinky_k = hand_landmarks[17]       

            hx_raw = index_k.x * w
            hy_raw = index_k.y * h

            if first_frame:
                smooth_hx, smooth_hy = hx_raw, hy_raw
                first_frame = False
            else:
                smooth_hx = smooth_hx * (1 - alpha) + hx_raw * alpha
                smooth_hy = smooth_hy * (1 - alpha) + hy_raw * alpha

        drawing_points.append(((int(smooth_hx), int(smooth_hy)), current_time))
        
        cv2.circle(frame, (int(wrist.x * w), int(wrist.y * h)), 6, (255, 0, 0), cv2.FILLED)   
        cv2.circle(frame, (int(smooth_hx), int(smooth_hy)), 6, (0, 0, 255), cv2.FILLED)      
        cv2.circle(frame, (int(pinky_k.x * w), int(pinky_k.y * h)), 6, (0, 255, 0), cv2.FILLED) 
        cv2.line(frame, (int(smooth_hx), int(smooth_hy)), (int(pinky_k.x * w), int(pinky_k.y * h)), (0, 255, 255), 2)
        cv2.line(frame, (int(wrist.x * w), int(wrist.y * h)), (int(smooth_hx), int(smooth_hy)), (255, 255, 255), 2)
    else:
        if not first_frame:
            drawing_points.append(((int(smooth_hx), int(smooth_hy)), current_time))
            cv2.circle(frame, (int(smooth_hx), int(smooth_hy)), 6, (0, 0, 255), cv2.FILLED)

    drawing_points = [pt for pt in drawing_points if (current_time - pt[1] < LIFETIME)]
    
    for i in range(1, len(drawing_points)):
        pt1, time1 = drawing_points[i - 1]
        pt2, time2 = drawing_points[i]
        age = current_time - time2
        life_ratio = max(0, (LIFETIME - age) / LIFETIME)
        thickness = int(5 * life_ratio) + 1
        cv2.line(frame, pt1, pt2, (255, 255, 200), thickness, cv2.LINE_AA)
        
    for i in range(len(drawing_points)):
        pt_coords, pt_time = drawing_points[i]
        age = current_time - pt_time
        life_ratio = max(0, (LIFETIME - age) / LIFETIME)
        
        if random.random() < 0.4 * life_ratio:
            for _ in range(random.randint(1, 2)):
                offset_x = random.randint(-8, 8)
                offset_y = random.randint(-8, 8)
                sparkle_pos = (pt_coords[0] + offset_x, pt_coords[1] + offset_y)
                p_radius = random.randint(1, 2)
                color = random.choice([(0, 215, 255), (255, 235, 170), (255, 255, 255)])
                cv2.circle(frame, sparkle_pos, p_radius, color, -1, cv2.LINE_8)

    cv2.putText(frame, "Day 6: True Disney Sparkle Trail Pipeline", (20, 40), 
                cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return frame

# Local script fallback window execution guard
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while cap.isOpened():
        success, img_frame = cap.read()
        if not success: continue
        output = process_frame(img_frame)
        cv2.imshow("Disney Wand Canvas", output)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            drawing_points.clear()
            first_frame = True
        elif key == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()