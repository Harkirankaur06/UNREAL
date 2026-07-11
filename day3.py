import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os

# --- MODEL FILE CHECK ---
model_path = "hand_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading hand tracking model file... please wait...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

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
current_growth = 0.0     # Percentage of extension (0.0 to 1.0)
speed = 0.08             # Growth animation step size per frame
blade_color = (255, 0, 0) # BGR Format: Vibrant Blue

cap = cv2.VideoCapture(0)

print("\n=======================================================")
print("GROW ALONG THE FIST PIPELINE LIVE")
print("Close your fist to ignite the blade out of your index knuckle!")
print("Press 'q' to exit.")
print("=======================================================\n")

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Create blank graphic buffers for image processing layers
        glow_mask = np.zeros((h, w, 3), dtype=np.uint8)
        core_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Process the frame through the tracking model
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # Pinky to Index Knuckle tracking anchors
                index_k = hand_landmarks[5]        # Index Knuckle (Red Dot)
                pinky_k = hand_landmarks[17]       # Pinky Knuckle (Green Dot)
                
                # Finger tracking anchors for the grip detection
                index_tip = hand_landmarks[8]
                index_pip = hand_landmarks[6]
                middle_tip = hand_landmarks[12]
                middle_pip = hand_landmarks[10]

                # Convert normalized positions into screen pixel space
                ix, iy = int(index_k.x * w), int(index_k.y * h)
                px, py = int(pinky_k.x * w), int(pinky_k.y * h)

                # --- TRIGGER LOGIC ---
                hand_is_closed = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)

                if hand_is_closed:
                    current_growth = min(1.0, current_growth + speed)
                else:
                    current_growth = max(0.0, current_growth - speed)

                # --- GROW ALONG THE FIST DIRECTION MATH ---
                # Vector running straight from pinky (green) to index (red)
                vx = ix - px
                y_vector = iy - py
                
                # Normalize the vector so tilt/distance doesn't change the final blade length
                magnitude = np.sqrt(vx**2 + y_vector**2)
                if magnitude > 0:
                    vx /= magnitude
                    y_vector /= magnitude

                # Base of the saber is now anchored directly at the index knuckle (red dot)
                cx, cy = ix, iy
                
                # Scale the blade relative to screen height
                scale_factor = (h * 0.65) * current_growth
                
                # Project the blade tip straight out along your fist's alignment
                target_x = int(cx + vx * scale_factor)
                target_y = int(cy + y_vector * scale_factor)

                # --- MULTI-PASS GEOMETRIC DRAWING ---
                if current_growth > 0:
                    z_scale = 1.0 + abs(index_k.z)
                    
                    # Pass A: Thick outer neon glow profile
                    cv2.line(glow_mask, (cx, cy), (target_x, target_y), blade_color, int(28 * z_scale), cv2.LINE_AA)
                    
                    # Pass B: Secondary mid-tier intensive core glow
                    cv2.line(glow_mask, (cx, cy), (target_x, target_y), blade_color, int(12 * z_scale), cv2.LINE_AA)
                    
                    # Pass C: Luminous White Core Line
                    cv2.line(core_mask, (cx, cy), (target_x, target_y), (255, 255, 255), int(6 * z_scale), cv2.LINE_AA)

                # Overlay interface lines to visualize your knuckle tracking axis
                cv2.circle(frame, (ix, iy), 6, (0, 0, 255), cv2.FILLED)  # Red Index Knuckle
                cv2.circle(frame, (px, py), 6, (0, 255, 0), cv2.FILLED)  # Green Pinky Knuckle
                cv2.line(frame, (ix, iy), (px, py), (0, 255, 255), 2)    # Yellow Knuckle Line

        # --- IMAGE PROCESSING BLENDING COMPOSITE ---
        glow_blur = cv2.GaussianBlur(glow_mask, (35, 35), 0)
        saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
        frame = cv2.add(frame, saber_composite)

        # UI State Overlay Text
        status_text = "IGNITED" if current_growth > 0.3 else "RETRACTED"
        cv2.putText(frame, f"Saber Control: {status_text}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Day 3 Challenge: Real-Time Lightsaber Engine", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()