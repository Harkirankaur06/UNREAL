import cv2
import numpy as np
from ultralytics import YOLO
import random

# Load the official lightweight YOLOv8 segmentation model
model = YOLO('yolov8n-seg.pt')

cap = cv2.VideoCapture(0)

snapped = False
snap_progress = 0.0
captured_frame = None
captured_mask = None
particles = []

print("Press 's' to trigger the Thanos Snap! Press 'r' to reset. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    if snapped:
        if captured_frame is None:
            captured_frame = frame.copy()
            # Run inference to detect the person
            results = model(frame, verbose=False)
            
            # Create an empty black mask layer
            captured_mask = np.zeros((h, w), dtype=np.uint8)
            
            # Extract the human segmentation mask if detected
            if results[0].masks is not None:
                for result in results[0]:
                    # Class 0 is 'person' in YOLO
                    if int(result.boxes.cls[0]) == 0:
                        # Resize YOLO's low-res mask to perfectly fit our camera frame
                        seg_mask = result.masks.data[0].cpu().numpy()
                        captured_mask = (cv2.resize(seg_mask, (w, h)) > 0.5).astype(np.uint8) * 255
                        break
        
        if captured_frame is not None:
            snap_progress += 0.02
            if snap_progress > 1.0:
                snap_progress = 1.0
            
            output_frame = frame.copy()
            threshold_x = int(w * snap_progress)
            
            # Fast pixel erosion loop using vectorized step
            for y in range(0, h, 5):
                for x in range(0, w, 5):
                    if captured_mask[y, x] > 0:
                        if x < threshold_x:
                            if random.random() > 0.2 and x > (threshold_x - 60):
                                if random.random() > 0.85 and len(particles) < 200:
                                    particles.append({
                                        'x': x, 'y': y,
                                        'vx': random.randint(2, 6),
                                        'vy': random.randint(-4, -1),
                                        'color': captured_frame[y, x].tolist(),
                                        'life': 25
                                    })
                                cv2.rectangle(output_frame, (x, y), (x+5, y+5), (0, 0, 0), -1)
                        else:
                            output_frame[y:y+5, x:x+5] = captured_frame[y:y+5, x:x+5]
            
            # Update particles
            for p in particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= 1
                if 0 <= p['x'] < w and 0 <= p['y'] < h and p['life'] > 0:
                    cv2.circle(output_frame, (int(p['x']), int(p['y'])), 2, p['color'], -1)
                else:
                    particles.remove(p)
                    
            cv2.imshow('Thanos Snap (Python 3.13 Native)', output_frame)
        else:
            cv2.imshow('Thanos Snap (Python 3.13 Native)', frame)
    else:
        cv2.imshow('Thanos Snap (Python 3.13 Native)', frame)
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        snapped = True
    elif key == ord('r'):
        snapped = False
        snap_progress = 0.0
        captured_frame = None
        captured_mask = None
        particles = []
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()