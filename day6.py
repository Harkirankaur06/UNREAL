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
LIFETIME = 5.0  # Time in seconds for the sketch to remain visible

# Tracking smoothing
smoothed_x, smoothed_y = 0, 0
alpha = 0.7  # Higher value means faster tracking response

cap = cv2.VideoCapture(0)
frame_timestamp = 0

print("Solid Sparkle Wand Active! Canvas persists for 5 seconds.")
print("Press 'c' to clear canvas, 'q' to quit.")

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        current_time = time.time()
        
        # 1. MediaPipe Frame Processing
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_timestamp += 1
        detection_result = landmarker.detect_for_video(mp_image, frame_timestamp)
        
        # 2. Extract and Smooth Index Tip Position
        if detection_result.hand_landmarks:
            hand_landmarks = detection_result.hand_landmarks[0]
            index_tip = hand_landmarks[8]
            
            raw_x, raw_y = int(index_tip.x * w), int(index_tip.y * h)
            
            if smoothed_x == 0 and smoothed_y == 0:
                smoothed_x, smoothed_y = raw_x, raw_y
            else:
                smoothed_x = int(alpha * raw_x + (1 - alpha) * smoothed_x)
                smoothed_y = int(alpha * raw_y + (1 - alpha) * smoothed_y)
            
            # Store point with current timestamp
            drawing_points.append(((smoothed_x, smoothed_y), current_time))
            
            # Glowing core at the finger tip point
            cv2.circle(frame, (smoothed_x, smoothed_y), 5, (255, 255, 255), -1)
            cv2.circle(frame, (smoothed_x, smoothed_y), 12, (0, 215, 255), 2)
        else:
            # Add a None marker if the finger leaves the screen so lines don't cross gaps
            if len(drawing_points) > 0 and drawing_points[-1] is not None:
                drawing_points.append(None)

        # 3. Clean out points older than 5 seconds
        drawing_points = [pt for pt in drawing_points if pt is None or (current_time - pt[1] < LIFETIME)]
        
        # 4. RENDER ENGINE: Draw Solid Line Segments First
        for i in range(1, len(drawing_points)):
            if drawing_points[i - 1] is None or drawing_points[i] is None:
                continue
                
            pt1, time1 = drawing_points[i - 1]
            pt2, time2 = drawing_points[i]
            
            # Fade calculation based on age
            age = current_time - time2
            life_ratio = max(0, (LIFETIME - age) / LIFETIME)
            
            # Dynamic line width that gets thinner as it gets older
            thickness = int(4 * life_ratio) + 1
            
            # Draw the continuous solid core line (Magical cyan/white base line)
            cv2.line(frame, pt1, pt2, (255, 255, 200), thickness)
            
        # 5. RENDER ENGINE: Layer Sparkles Over the Line
        for i in range(len(drawing_points)):
            if drawing_points[i] is None:
                continue
                
            pt_coords, pt_time = drawing_points[i]
            age = current_time - pt_time
            life_ratio = max(0, (LIFETIME - age) / LIFETIME)
            
            # Old lines generate fewer particles
            if random.random() < 0.6 * life_ratio:
                for _ in range(random.randint(1, 3)):
                    offset_x = random.randint(-10, 10)
                    offset_y = random.randint(-10, 10)
                    sparkle_pos = (pt_coords[0] + offset_x, pt_coords[1] + offset_y)
                    
                    p_radius = random.randint(1, 3) if life_ratio > 0.4 else 1
                    
                    # Sparkle colors: Gold, Pixie Blue, Shimmering White
                    color = random.choice([
                        (0, 220, 255),    
                        (255, 235, 160),  
                        (255, 255, 255)   
                    ])
                    
                    cv2.circle(frame, sparkle_pos, p_radius, color, -1)
                    
        # Head-Up Display Text Overlay
        cv2.putText(frame, "Day 6: Disney Solid Sparkle Canvas", (20, 40), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
        cv2.imshow("Disney Wand Canvas", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            drawing_points.clear()
        elif key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()