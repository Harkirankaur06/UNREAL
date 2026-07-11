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
saber_on = False        # Is the saber supposed to be active?
ready_for_toggle = True  # Prevents rapid flickering while holding the gesture
current_growth = 0.0     # Percentage of extension (0.0 to 1.0)
speed = 0.08             # Growth animation step size per frame
blade_color = (255, 0, 0) # BGR Format: Vibrant Blue (Change to (0, 0, 255) for Sith Red!)

cap = cv2.VideoCapture(0)

print("\n=======================================================")
print("FLASH A QUICK THUMBS UP TO TOGGLE THE SABER ON / OFF")
print("Once ignited, hold your fist closed and swing it around!")
print("Press 'q' to exit the engine.")
print("=======================================================\n")

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Mirror the frame horizontally for natural orientation
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
                # Core Hilt Anchors
                wrist = hand_landmarks[0]          # Base of the grip
                knuckle = hand_landmarks[5]        # Top of the grip (where blade emits)

                # Finger Tracking Anchors for Gestures
                thumb_tip = hand_landmarks[4]
                index_tip = hand_landmarks[8]
                index_pip = hand_landmarks[6]
                middle_tip = hand_landmarks[12]
                middle_pip = hand_landmarks[10]

                # Convert normalized positions into screen pixel space
                x1, y1 = int(wrist.x * w), int(wrist.y * h)
                x2, y2 = int(knuckle.x * w), int(knuckle.y * h)

                # --- 1. THE THUMBS-UP TOGGLE LATCH ---
                # Curl check: Are the main fingers curled into the palm?
                fingers_curled = (index_tip.y > index_pip.y) and (middle_tip.y > middle_pip.y)
                # Position check: Is the thumb sticking upwards relative to the hand knuckle?
                thumb_up = thumb_tip.y < knuckle.y 

                # Handle the switch logic
                if thumb_up and fingers_curled:
                    if ready_for_toggle:
                        saber_on = not saber_on    # Invert state (True becomes False, vice versa)
                        ready_for_toggle = False   # Lock the trigger
                else:
                    ready_for_toggle = True        # Unlock once hand moves away from gesture

                # --- 2. SMOOTH LERP GROWTH ENGINE ---
                if saber_on:
                    current_growth = min(1.0, current_growth + speed)
                else:
                    current_growth = max(0.0, current_growth - speed)

                # --- 3. DIRECTIONAL VECTOR MATH (3D SPACE PROJECTION) ---
                vx = x2 - x1
                vy = y2 - y1
                
                # Calculate coordinates where the blade tip terminates based on current growth
                target_x = int(x2 + vx * 3.5 * current_growth)
                target_y = int(y2 + vy * 3.5 * current_growth)

                # --- 4. MULTI-PASS GEOMETRIC DRAWING ---
                if current_growth > 0:
                    # Scale factor adjusts line thickness dynamically using Z depth estimation
                    z_scale = 1.0 + abs(wrist.z)
                    
                    # Pass A: Thick glow outline profile
                    cv2.line(glow_mask, (x2, y2), (target_x, target_y), blade_color, int(28 * z_scale), cv2.LINE_AA)
                    
                    # Pass B: Secondary mid-tier core glow line
                    cv2.line(glow_mask, (x2, y2), (target_x, target_y), blade_color, int(12 * z_scale), cv2.LINE_AA)
                    
                    # Pass C: Intense White Plasma Core line
                    cv2.line(core_mask, (x2, y2), (target_x, target_y), (255, 255, 255), int(6 * z_scale), cv2.LINE_AA)

                # Optional: Overlay physical interface indicators
                cv2.circle(frame, (x1, y1), 8, (0, 255, 0), cv2.FILLED)  # Green Wrist dot
                cv2.circle(frame, (x2, y2), 8, (0, 0, 255), cv2.FILLED)  # Red Knuckle dot

        # --- 5. IMAGE PROCESSING BLENDING COMPOSITE ---
        # Blur the colored mask passes heavily using a spatial Gaussian filter
        glow_blur = cv2.GaussianBlur(glow_mask, (35, 35), 0)
        
        # Additively merge the diffuse colored blur with the solid white core mask
        saber_composite = cv2.addWeighted(glow_blur, 1.0, core_mask, 1.0, 0)
        
        # Add the completed saber rendering right on top of your live webcam frame
        frame = cv2.add(frame, saber_composite)

        # UI Text Overlays
        status_text = "IGNITED" if saber_on else "RETRACTED"
        cv2.putText(frame, f"Saber Control: {status_text}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Render output stream window
        cv2.imshow("Day 3 Challenge: Real-Time Lightsaber Engine", frame)

        # Drop cleanly if 'q' is hit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()