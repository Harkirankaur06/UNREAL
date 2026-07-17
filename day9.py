import cv2
import numpy as np
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- AUTOMATIC ASSET DOWNLOAD FOR PYTHON 3.13 COMPATIBILITY ---
MODEL_FILE = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

if not os.path.exists(MODEL_FILE):
    print("Downloading MediaPipe model asset... please wait a moment...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
    print("Download complete!")

# Initialize the new MediaPipe Tasks Face Landmarker
base_options = python.BaseOptions(model_asset_path=MODEL_FILE)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Global persistent canvas layer for laser drawings
canvas = None

# History buffers for temporal moving average smoothing filter (kills jitter)
history_x = []
history_y = []
SMOOTH_FRAMES = 4

def process_frame(incoming_frame):
    global canvas, history_x, history_y
        
    frame = cv2.flip(incoming_frame, 1) 
    h, w, _ = frame.shape
    
    if canvas is None or canvas.shape != frame.shape:
        canvas = np.zeros_like(frame)

    # Convert standard BGR frame to RGB and wrap into MediaPipe Image format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Run inference using the modern Tasks API
    detection_result = detector.detect(mp_image)

    if detection_result.face_landmarks:
        # Pull landmarks for the primary face
        face_landmarks = detection_result.face_landmarks[0]
        
        # --- STRUCTURAL EYELID ISOLATION FILTER ---
        # Extract landmarks for Upper/Lower eyelids to check blink states
        left_up = face_landmarks[159].y
        left_down = face_landmarks[145].y
        right_up = face_landmarks[386].y
        right_down = face_landmarks[374].y
        
        # Firing condition: if vertical open distance shrinks past 0.012, eyes are closed
        eye_open_threshold = 0.012  
        if (left_down - left_up > eye_open_threshold) and (right_down - right_up > eye_open_threshold):

            # --- CORNER STONE GEOMETRIC ANCHORS ---
            # 468 = Left Iris Center, 473 = Right Iris Center, 4 = Nose Tip Pivot
            left_iris = face_landmarks[468]
            right_iris = face_landmarks[473]
            nose = face_landmarks[4]
            
            # Translate normalized floats (0.0 to 1.0) directly into pixel bounds
            lx, ly = int(left_iris.x * w), int(left_iris.y * h)
            rx, ry = int(right_iris.x * w), int(right_iris.y * h)
            nx, ny = int(nose.x * w), int(nose.y * h)

            # Compute physical structural eye midpoint
            eye_mid_x = (lx + rx) // 2
            eye_mid_y = (ly + ry) // 2

            # Proportional Head Vector calculation relative to the nose pivot point
            dx = nx - eye_mid_x
            dy = ny - (eye_mid_y + 18)

            # Screen Core Reference Center Points
            screen_center_x = w // 2
            screen_center_y = h // 2

            # Proportional gain multipliers (progressive scaling outwards from center)
            gain_x = 24.0
            gain_y = 28.0

            # Calculate tracking destination outwards from screen center
            target_x = int(screen_center_x + (dx * gain_x))
            target_y = int(screen_center_y + (dy * gain_y))

            # Push coordinate states to history queues
            history_x.append(target_x)
            history_y.append(target_y)
            if len(history_x) > SMOOTH_FRAMES:
                history_x.pop(0)
                history_y.pop(0)

            # Compute average positions to avoid random shifts
            smooth_target_x = int(np.mean(history_x))
            smooth_target_y = int(np.mean(history_y))

            # Constrain target coordinates within viewport borders
            smooth_target_x = max(0, min(w - 1, smooth_target_x))
            smooth_target_y = max(0, min(h - 1, smooth_target_y))

            # 1. Burn persistent track paths into background canvas layer
            cv2.circle(canvas, (smooth_target_x, smooth_target_y), 8, (0, 165, 255), -1)  # Outer Glow
            cv2.circle(canvas, (smooth_target_x, smooth_target_y), 4, (0, 255, 255), -1)  # Laser Core

            # 2. Render live, rigid red structural laser rods shooting directly from eye sockets
            cv2.line(frame, (lx, ly), (smooth_target_x, smooth_target_y), (0, 0, 255), 5)      
            cv2.line(frame, (lx, ly), (smooth_target_x, smooth_target_y), (200, 200, 255), 1)  
            cv2.circle(frame, (lx, ly), 5, (255, 255, 255), -1)                  
            
            cv2.line(frame, (rx, ry), (smooth_target_x, smooth_target_y), (0, 0, 255), 5)      
            cv2.line(frame, (rx, ry), (smooth_target_x, smooth_target_y), (200, 200, 255), 1)  
            cv2.circle(frame, (rx, ry), 5, (255, 255, 255), -1)                  

    # Extract layer mask to blend persistent laser canvas with real frame
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    
    bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    output_frame = cv2.add(bg, fg)

    cv2.putText(output_frame, "PYTHON 3.13 MODERN MEDIAPIPE TRACKING ACTIVE", (15, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    cv2.putText(output_frame, "Close eyes to stop | Press 'r' to wipe canvas", (15, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return output_frame

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while cap.isOpened():
        success, img_frame = cap.read()
        if not success: 
            break
            
        output = process_frame(img_frame)
        cv2.imshow("MediaPipe Python 3.13 Gaze Laser System", output)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): 
            break
        elif key == ord('r'):
            if canvas is not None:
                canvas = np.zeros_like(canvas)
            
    cap.release()
    cv2.destroyAllWindows()