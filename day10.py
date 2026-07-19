import cv2
import numpy as np
from ultralytics import YOLO
import random
import time

# Load both segmentation and pose tracking models
seg_model = YOLO('yolov8n-seg.pt')
pose_model = YOLO('yolov8n-pose.pt')

cap = cv2.VideoCapture(0)

is_snapped = False
snap_progress = 0.0
particles = []

captured_frame = None
captured_mask = None
background_frame = None

# --- STEP 1: LEARN THE BACKGROUND ---
print("\n[STEP 1] Calibrating background. Please STEP OUT OF THE FRAME for 3 seconds...")
time.sleep(1)

calibrating = True
start_time = time.time()
while calibrating and cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    
    elapsed = time.time() - start_time
    countdown = 3 - int(elapsed)
    
    display_frame = frame.copy()
    if countdown > 0:
        cv2.putText(display_frame, f"CALIBRATING BACKGROUND IN {countdown}...", (30, 60), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    else:
        background_frame = frame.copy()
        calibrating = False
        
    cv2.imshow('Thanos Snap Engine', display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("[STEP 2] Background learned! STEP INTO THE FRAME.")
print("RAISE YOUR HAND ABOVE YOUR SHOULDER to trigger the disintegration visually!")

# --- STEP 2: LIVE FEED & VISUAL GESTURE TRIGGER ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Process gesture detection if we haven't snapped yet
    if not is_snapped:
        pose_results = pose_model(frame, verbose=False)
        
        if pose_results[0].keypoints is not None and len(pose_results[0].keypoints.data) > 0:
            # Get keypoint arrays
            # YOLO Keypoint indexes: 5=L_Shoulder, 6=R_Shoulder, 9=L_Wrist, 10=R_Wrist
            keypoints = pose_results[0].keypoints.data[0].cpu().numpy()
            
            if len(keypoints) > 10:
                l_shoulder_y = keypoints[5][1]
                r_shoulder_y = keypoints[6][1]
                l_wrist_y = keypoints[9][1]
                r_wrist_y = keypoints[10][1]
                
                # Check confidence metrics to avoid random noise triggers
                l_shoulder_conf = keypoints[5][2]
                r_shoulder_conf = keypoints[6][2]
                l_wrist_conf = keypoints[9][2]
                r_wrist_conf = keypoints[10][2]
                
                # In pixel graphics, 0 is at the very top. Wrist Y < Shoulder Y means your hand is RAISED.
                left_raised = (l_wrist_y < l_shoulder_y) and (l_wrist_conf > 0.5) and (l_shoulder_conf > 0.5)
                right_raised = (r_wrist_y < r_shoulder_y) and (r_wrist_conf > 0.5) and (r_shoulder_conf > 0.5)
                
                if left_raised or right_raised:
                    print("💥 VISUAL GESTURE DETECTED! Commencing disintegration...")
                    is_snapped = True

    # Processing the disintegration sequence
    if is_snapped:
        if captured_frame is None:
            captured_frame = frame.copy()
            seg_results = seg_model(frame, verbose=False)
            captured_mask = np.zeros((h, w), dtype=np.uint8)
            
            if seg_results[0].masks is not None:
                for result in seg_results[0]:
                    if int(result.boxes.cls[0]) == 0:  # Class 0 = person
                        seg_mask = result.masks.data[0].cpu().numpy()
                        captured_mask = (cv2.resize(seg_mask, (w, h)) > 0.5).astype(np.uint8) * 255
                        break
        
        if captured_frame is not None:
            snap_progress += 0.018  # Disintegration speed
            if snap_progress > 1.0:
                snap_progress = 1.0
                
            output_frame = frame.copy()
            threshold_x = int(w * snap_progress)
            
            # Optimized block scan
            for y in range(0, h, 5):
                for x in range(0, w, 5):
                    if captured_mask[y, x] > 0:
                        if x < threshold_x:
                            if random.random() > 0.15 and x > (threshold_x - 70):
                                if random.random() > 0.88 and len(particles) < 300:
                                    particles.append({
                                        'x': x, 'y': y,
                                        'vx': random.randint(3, 7),
                                        'vy': random.randint(-5, -1),
                                        'color': captured_frame[y, x].tolist(),
                                        'life': 30
                                    })
                            # Seamlessly overlay the background frame
                            output_frame[y:y+5, x:x+5] = background_frame[y:y+5, x:x+5]
                        else:
                            output_frame[y:y+5, x:x+5] = captured_frame[y:y+5, x:x+5]
            
            # Draw drifting particles
            for p in particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= 1
                if 0 <= p['x'] < w and 0 <= p['y'] < h and p['life'] > 0:
                    cv2.circle(output_frame, (int(p['x']), int(p['y'])), 2, p['color'], -1)
                else:
                    particles.remove(p)
                    
            cv2.imshow('Thanos Snap Engine', output_frame)
        else:
            cv2.imshow('Thanos Snap Engine', frame)
    else:
        # Standard tracking screen loop
        display_frame = frame.copy()
        cv2.putText(display_frame, "POSE SYSTEM ACTIVE: RAISE HAND", (30, 60), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Thanos Snap Engine', display_frame)
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        is_snapped = False
        snap_progress = 0.0
        captured_frame = None
        captured_mask = None
        particles = []
        print("System reset. Awaiting visual gesture trigger...")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()