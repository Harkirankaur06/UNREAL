import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os

# --- DOWNLOAD THE HAND LANDMARKER MODEL ---
# The modern API requires a lightweight model file (.task). 
# This block automatically downloads it to your directory if you don't have it.
model_path = "hand_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading hand tracking model file... please wait...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

# Base aliases for the modern MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Configure options for the landmarker
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,  # Optimized specifically for webcam video streams
    num_hands=1
)

# Open default webcam (0)
cap = cv2.VideoCapture(0)

print("\n=============================================")
print("Modern Tracking Engine Live! Press 'q' to exit.")
print("=============================================\n")

# Use a context manager to open the landmarker safely
with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Mirror the frame horizontally for natural orientation
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Convert BGR (OpenCV standard) to RGB (MediaPipe standard)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe modern API expects an image object and a timestamp in milliseconds
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        
        # Run the detection algorithm
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # If any hand is detected
        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # MediaPipe gives us 21 landmarks. Let's pull out the base anchors:
                # Landmark 0 = WRIST
                wrist = hand_landmarks[0]
                # Landmark 5 = INDEX_FINGER_MCP (Base knuckle of index finger)
                index_knuckle = hand_landmarks[5]

                # Convert normalized coordinates (0.0 to 1.0) into actual pixel locations
                wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                knuckle_x, knuckle_y = int(index_knuckle.x * w), int(index_knuckle.y * h)

                # Draw tracking points onto the live frame
                cv2.circle(frame, (wrist_x, wrist_y), 10, (0, 255, 0), cv2.FILLED)        # Green wrist dot
                cv2.circle(frame, (knuckle_x, knuckle_y), 10, (0, 0, 255), cv2.FILLED)    # Red knuckle dot

                # Draw a temporary vector connecting line representing the hilt orientation
                cv2.line(frame, (wrist_x, wrist_y), (knuckle_x, knuckle_y), (255, 255, 255), 3)

                # Show Z depth estimation in the window
                cv2.putText(frame, f"Z: {round(wrist.z, 2)}", (wrist_x + 15, wrist_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Render output display window
        cv2.imshow("Day 3 Challenge: Modern Tracking Engine", frame)

        # Quit cleanly when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()