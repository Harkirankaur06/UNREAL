import cv2
import numpy as np
from ultralytics import YOLO
import time
import math

# Load the vision engines natively supported by Python 3.13
seg_model = YOLO('yolov8n-seg.pt')
pose_model = YOLO('yolov8n-pose.pt')

cap = cv2.VideoCapture(0)

background_frame = None
ripple_centers = []  # List to track active touch points [(x, y, time_elapsed), ...]

# --- STEP 1: LEARN THE BACKGROUND ---
print("\n[STEP 1] Calibrating empty room background. Please STEP OUT OF THE FRAME for 3 seconds...")
time.sleep(1)

calibrating = True
start_time = time.time()
while calibrating and cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    
    elapsed = time.time() - start_time
    countdown = 3 - int(elapsed)
    
    display_frame = frame.copy()
    if countdown > 0:
        cv2.putText(display_frame, f"CALIBRATING CHROME LAB IN {countdown}...", (30, 60), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    else:
        background_frame = frame.copy()
        calibrating = False
        
    cv2.imshow('T-1000 Liquid Metal Engine', display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

print("[STEP 2] Calibration Complete! Step into the frame.")
print("Touch your body with either hand to disrupt the liquid chrome lattice structure.")

# --- STEP 2: METALLIC TEXTURING & INTERACTIVE RIPPLE DISPLACEMENT ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # 1. RUN DETECTION IN PARALLEL
    seg_results = seg_model(frame, verbose=False)
    pose_results = pose_model(frame, verbose=False)
    
    # Generate empty layout structures
    body_mask = np.zeros((h, w), dtype=np.uint8)
    fingertips = []
    
    # Extract structural body mask from segmentation model
    if seg_results[0].masks is not None:
        for result in seg_results[0]:
            if int(result.boxes.cls[0]) == 0:  # Human class tag
                seg_mask = result.masks.data[0].cpu().numpy()
                body_mask = (cv2.resize(seg_mask, (w, h)) > 0.5).astype(np.uint8) * 255
                break
                
    # Extract skeletal tracking nodes for left and right wrists/fingertips
    if pose_results[0].keypoints is not None and len(pose_results[0].keypoints.data) > 0:
        keypoints = pose_results[0].keypoints.data[0].cpu().numpy()
        if len(keypoints) > 10:
            # Index 9 = Left Wrist, Index 10 = Right Wrist (serving as touch pointers)
            if keypoints[9][2] > 0.5: fingertips.append((int(keypoints[9][0]), int(keypoints[9][1])))
            if keypoints[10][2] > 0.5: fingertips.append((int(keypoints[10][0]), int(keypoints[10][1])))

    # 2. CHECK FOR BODY INTERSECTION TOUCH EVENTS
    for tx, ty in fingertips:
        if 0 <= tx < w and 0 <= ty < h:
            # If the tracking point sits inside your body mask silhouette
            if body_mask[ty, tx] > 0:
                # Add a new ripple trigger event with local time tracker
                # Distance threshold protects the array from overflowing too fast
                if not any(math.hypot(tx - r[0], ty - r[1]) < 25 for r in ripple_centers):
                    ripple_centers.append([tx, ty, 0.0])

    # 3. COMPOSITE LIQUID METAL RIPPLE EFFECTS
    # Default window displays the background frame
    output_frame = background_frame.copy() if background_frame is not None else frame.copy()
    
    if np.any(body_mask > 0):
        # A. CHROME TEXTURE SHADER GENERATION
        # Convert your body feed into high-contrast grayscale
        gray_body = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Solarization loop: Creates extreme metallic specular highlights
        chrome_gray = np.where(gray_body < 128, gray_body * 2, 255 - ((gray_body - 128) * 2))
        chrome_gray = cv2.GaussianBlur(chrome_gray.astype(np.uint8), (5, 5), 0)
        
        # Remap single grayscale channel into 3-channel BGR liquid chrome texture
        chrome_texture = cv2.merge([
            cv2.equalizeHist(chrome_gray), # Deep lowlights
            cv2.add(chrome_gray, 30),      # Ambient glow midtones
            cv2.add(chrome_gray, 60)       # Direct chrome peaks
        ])
        
        # B. RIPPLE MATHEMATICAL DISPLACEMENT MAP
        # Create map matrices to shift individual pixel lookups dynamically
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        
        # Advance clock parameters for active ripples
        active_ripples = []
        for r in ripple_centers:
            cx, cy, t = r
            t += 0.4  # Velocity speed of the wave spreading out
            if t < 25.0:  # Life decay parameter threshold
                active_ripples.append([cx, cy, t])
                
                # Math shader: Calculate vector distance of every pixel to the drop source point
                dx_matrix = map_x - cx
                dy_matrix = map_y - cy
                dist_matrix = np.sqrt(dx_matrix**2 + dy_matrix**2)
                
                # Apply sine-wave offset equations to create localized visual shifting
                # Frequency set by division factor, amplitude modulated by time dampening
                wave = np.sin(dist_matrix / 6.0 - t) * (12.0 / (t + 1.0))
                
                # Mask out calculation zones so distortions only apply inside active radial bounds
                ripple_mask = (dist_matrix < (t * 12.0)) & (dist_matrix > 0)
                map_x[ripple_mask] += (dx_matrix[ripple_mask] / dist_matrix[ripple_mask]) * wave[ripple_mask]
                map_y[ripple_mask] += (dy_matrix[ripple_mask] / dist_matrix[ripple_mask]) * wave[ripple_mask]
                
        ripple_centers = active_ripples
        
        # Warp the chrome skin texture using the compiled displacement map
        displaced_chrome = cv2.remap(chrome_texture, map_x, map_y, cv2.INTER_LINEAR)
        
        # C. MASK OVERLAY & BLENDING
        # Cut the final displaced chrome out utilizing the human mask
        chrome_body = cv2.bitwise_and(displaced_chrome, displaced_chrome, mask=body_mask)
        bg_cutout = cv2.bitwise_and(output_frame, output_frame, mask=cv2.bitwise_not(body_mask))
        
        # Fuse the reflective metallic figure into the static environment
        output_frame = cv2.add(chrome_body, bg_cutout)
        
    cv2.imshow('T-1000 Liquid Metal Engine', output_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        ripple_centers = []
        print("Lattice pattern stabilized. All ripples dissolved.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()