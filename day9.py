import cv2
import numpy as np
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- AUTOMATIC ASSET DOWNLOAD ---
MODEL_FILE = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

if not os.path.exists(MODEL_FILE):
    print("Downloading MediaPipe model asset... please wait...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)

base_options = python.BaseOptions(model_asset_path=MODEL_FILE)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

# Persistent layers
canvas = None
calibrated = False
base_dx = 0.0
base_dy = 0.0

# Moving average smoothing queue
history_x, history_y = [], []
SMOOTH_FRAMES = 6

def process_frame(incoming_frame):
    global canvas, history_x, history_y, calibrated, base_dx, base_dy
        
    frame = cv2.flip(incoming_frame, 1) 
    h, w, _ = frame.shape
    
    if canvas is None or canvas.shape != frame.shape:
        canvas = np.zeros_like(frame)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    # Fallback to screen center if not calibrated yet
    screen_center_x = w // 2
    screen_center_y = h // 2
    smooth_target_x, smooth_target_y = screen_center_x, screen_center_y

    if detection_result.face_landmarks:
        face_landmarks = detection_result.face_landmarks[0]
        
        # --- BLINK DETECTION WITH BACKUP LAYER ---
        left_up, left_down = face_landmarks[159].y, face_landmarks[145].y
        right_up, right_down = face_landmarks[386].y, face_landmarks[374].y
        
        if (left_down - left_up > 0.01) and (right_down - right_up > 0.01):
            
            # --- STABLE STRUCTURAL EYE CORNERS (GLARE PROOF) ---
            # Using structural eye midpoints instead of volatile irises
            lx = int(((face_landmarks[33].x + face_landmarks[133].x) / 2) * w)
            ly = int(((face_landmarks[33].y + face_landmarks[133].y) / 2) * h)
            rx = int(((face_landmarks[362].x + face_landmarks[263].x) / 2) * w)
            ry = int(((face_landmarks[362].y + face_landmarks[263].y) / 2) * h)
            
            # Nose Tip Anchor
            nx = int(face_landmarks[4].x * w)
            ny = int(face_landmarks[4].y * h)

            eye_mid_x = (lx + rx) // 2
            eye_mid_y = (ly + ry) // 2

            # Normalize calculation against forward distance scale (interpupillary distance)
            ipd = max(1.0, np.hypot(rx - lx, ry - ly))

            # Calculate raw structural look vector ratios
            raw_dx = (nx - eye_mid_x) / ipd
            raw_dy = (ny - eye_mid_y) / ipd

            # Safe initial lock guard
            if not calibrated:
                # Lasers remain at center until 'c' is hit
                dx, dy = 0.0, 0.0
            else:
                dx = raw_dx - base_dx
                dy = raw_dy - base_dy

            # Controlled gain adjustments
            gain_x = 1200.0  
            gain_y = 1400.0  

            # Compute relative offsets from true center screen coordinates
            target_x = int(screen_center_x + (dx * gain_x))
            target_y = int(screen_center_y + (dy * gain_y))

            # Append states to trailing filter window
            history_x.append(target_x)
            history_y.append(target_y)
            if len(history_x) > SMOOTH_FRAMES:
                history_x.pop(0)
                history_y.pop(0)

            smooth_target_x = int(np.mean(history_x))
            smooth_target_y = int(np.mean(history_y))
            smooth_target_x = max(0, min(w - 1, smooth_target_x))
            smooth_target_y = max(0, min(h - 1, smooth_target_y))

            # Only burn canvas and draw rods if calibration has been completed successfully
            if calibrated:
                cv2.circle(canvas, (smooth_target_x, smooth_target_y), 8, (0, 165, 255), -1) 
                cv2.circle(canvas, (smooth_target_x, smooth_target_y), 4, (0, 255, 255), -1) 

                cv2.line(frame, (lx, ly), (smooth_target_x, smooth_target_y), (0, 0, 255), 5)      
                cv2.line(frame, (lx, ly), (smooth_target_x, smooth_target_y), (200, 200, 255), 1)  
                cv2.circle(frame, (lx, ly), 5, (255, 255, 255), -1)                  
                
                cv2.line(frame, (rx, ry), (smooth_target_x, smooth_target_y), (0, 0, 255), 5)      
                cv2.line(frame, (rx, ry), (smooth_target_x, smooth_target_y), (200, 200, 255), 1)  
                cv2.circle(frame, (rx, ry), 5, (255, 255, 255), -1)                  
        else:
            # Clear historical queues when tracking drops out during blinks
            history_x.clear()
            history_y.clear()

    # Alpha composite blend channels
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    
    bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    output_frame = cv2.add(bg, fg)

    if not calibrated:
        cv2.putText(output_frame, "LOOK AT CENTER AND PRESS 'c' TO INITIALIZE", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    else:
        cv2.putText(output_frame, "LASER SYSTEM LOCKED AND ACTIVE", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
    cv2.putText(output_frame, "Press 'c' to reset center | 'r' to wipe canvas", (15, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Save tracking variables globally to handle hotkey key triggers inside the frame function
    process_frame.latest_raw_dx = locals().get('raw_dx', 0.0)
    process_frame.latest_raw_dy = locals().get('raw_dy', 0.0)

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
        elif key == ord('c'):
            # Manually trigger calibration lock only when looking forward perfectly
            if hasattr(process_frame, 'latest_raw_dx'):
                base_dx = process_frame.latest_raw_dx
                base_dy = process_frame.latest_raw_dy
                calibrated = True
                history_x.clear()
                history_y.clear()
        elif key == ord('r'):
            if canvas is not None:
                canvas = np.zeros_like(canvas)
            
    cap.release()
    cv2.destroyAllWindows()