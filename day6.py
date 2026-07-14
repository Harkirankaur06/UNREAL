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

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_hand),
    running_mode=VisionRunningMode.VIDEO
)

# Active sparkle trails list stores: ((x, y), creation_time)
drawing_points = []
LIFETIME = 5.0  # Duration in seconds for the sketch to stay visible

# Coordinate smoothing variables to prevent jitters
smoothed_x, smoothed_y = 0, 0
alpha = 0.65  # Smoothing factor (closer to 1 = faster response, closer to 0 = smoother trail)

cap = cv2.VideoCapture(0)
frame_timestamp = 0

print("Exact Disney Wand Tracker Active! Drawing trail persists for 5 seconds.")
print("Press 'c' to clear canvas, 'q' to quit.")

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        current_time = time.time()
        
        # 1. MediaPipe Video Tracking Input
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_timestamp += 1
        detection_result = landmarker.detect_for_video(mp_image, frame_timestamp)
        
        # 2. Extract Precise Index Fingertip
        if detection_result.hand_landmarks:
            hand_landmarks = detection_result.hand_landmarks[0]
            index_tip = hand_landmarks[8]  # Absolute index finger tip landmark
            
            raw_x, raw_y = int(index_tip.x * w), int(index_tip.y * h)
            
            # Linear interpolation smoothing formula to steady the pixel tracking point
            if smoothed_x == 0 and smoothed_y == 0:
                smoothed_x, smoothed_y = raw_x, raw_y
            else:
                smoothed_x = int(alpha * raw_x + (1 - alpha) * smoothed_x)
                smoothed_y = int(alpha * raw_y + (1 - alpha) * smoothed_y)
            
            # Append the precise coordinate along with its exact creation time
            drawing_points.append(((smoothed_x, smoothed_y), current_time))
            
            # Shimmering focal point directly at the precise tracking tip
            cv2.circle(frame, (smoothed_x, smoothed_y), 5, (255, 255, 255), -1)
            cv2.circle(frame, (smoothed_x, smoothed_y), 10, (0, 215, 255), 1)

        # 3. Time-Based Filter Engine (Drop any trail pixels older than 5 seconds)
        drawing_points = [pt for pt in drawing_points if current_time - pt[1] < LIFETIME]
        
        # 4. Magical Sparkle Engine Renderer
        for i in range(len(drawing_points)):
            pt_coords, pt_time = drawing_points[i]
            age = current_time - pt_time
            
            # Calculate remaining life ratio (starts at 1.0, fades down to 0.0 near 5s mark)
            life_ratio = (LIFETIME - age) / LIFETIME
            
            # Generate sparkles based on age; older parts of the sketch sparkle less intensely
            if random.random() < 0.5 * life_ratio:
                for _ in range(random.randint(2, 4)):
                    offset_x = random.randint(-12, 12)
                    offset_y = random.randint(-12, 12)
                    sparkle_pos = (pt_coords[0] + offset_x, pt_coords[1] + offset_y)
                    
                    p_radius = random.randint(1, 3) if life_ratio > 0.3 else 1
                    
                    # Classic Pixie Dust color palette selection
                    color = random.choice([
                        (0, 220, 255),    # Magical Gold
                        (255, 235, 160),  # Pixie Blue
                        (255, 255, 255)   # Shimmering White
                    ])
                    
                    cv2.circle(frame, sparkle_pos, p_radius, color, -1)
                    
        # Head-Up Display text overlay
        cv2.putText(frame, f"Day 6: Disney 5s Sparkle Canvas", (20, 40), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
        cv2.imshow("Disney Wand Canvas", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            drawing_points.clear()
        elif key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()