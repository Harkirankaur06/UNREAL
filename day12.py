import cv2
import numpy as np
import time

def draw_portal_ring(img, center, radius, color_bgr):
    """Draws a glowing, pulsing portal ring at a boundary."""
    overlay = img.copy()
    
    # Outer glow layers
    for r in range(radius + 12, radius, -2):
        cv2.circle(overlay, center, r, color_bgr, 2)
    
    # Core bright inner ring
    cv2.circle(overlay, center, radius, (255, 255, 255), 3)
    
    # Alpha blend glow onto image
    cv2.addWeighted(overlay, 0.45, img, 0.55, 0, img)

def run_portal_system(video_source=0):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    # Frame Dimensions
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define vertical 3-part grid boundaries
    col1 = w // 3          # Boundary between Left and Center
    col2 = (2 * w) // 3    # Boundary between Center and Right

    # Target Portal Centers along the dividers
    portal_left_center  = (col1, h // 2)
    portal_right_center = (col2, h // 2)

    # --- STAGE 1: BACKGROUND LEARNING ---
    print("\n--- LEARNING BACKGROUND ---")
    print("Please keep the scene clear of moving objects for 2 seconds...")
    
    bg_frames = []
    start_time = time.time()
    
    while time.time() - start_time < 2.0:
        ret, frame = cap.read()
        if not ret:
            break
        
        bg_frames.append(frame.astype(np.float32))
        
        # Countdown overlay
        remaining = max(0, 2.0 - (time.time() - start_time))
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Learning Background... {remaining:.1f}s", 
                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Portal Teleporter", display_frame)
        cv2.waitKey(1)

    # Compute static background model (median filter for noise resistance)
    background = np.median(bg_frames, axis=0).astype(np.uint8)
    bg_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)
    
    print("Background learned successfully! Portals are now ACTIVE.\n")

    # --- STAGE 2: REAL-TIME PORTAL TELEPORTATION ---
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        output = frame.copy()
        
        # 1. Isolate moving objects via Background Subtraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        frame_diff = cv2.absdiff(bg_gray, gray)
        _, motion_mask = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Clean up mask noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=1)

        # 2. Detect Object Contours
        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            if cv2.contourArea(cnt) < 1200:  # Ignore small noise
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            obj_center_x = x + bw // 2

            # Extract the isolated object using motion mask
            obj_crop = frame[y:y+bh, x:x+bw]
            mask_crop = motion_mask[y:y+bh, x:x+bw]

            # Convert 1-channel mask to 3-channel normalized alpha matte
            alpha = (mask_crop / 255.0)[:, :, np.newaxis]

            # --- CASE A: Object enters RIGHT side -> Teleport to LEFT side ---
            if obj_center_x > col2:
                # Calculate corresponding position on Left panel
                dest_x = max(0, x - col2)
                dest_y = y
                
                if dest_x + bw <= col1 and dest_y + bh <= h:
                    # 1. Clean original object out of Right side using learned background
                    output[y:y+bh, x:x+bw] = (background[y:y+bh, x:x+bw] * alpha + 
                                              output[y:y+bh, x:x+bw] * (1.0 - alpha)).astype(np.uint8)

                    # 2. Paste isolated object onto Left side
                    roi = output[dest_y:dest_y+bh, dest_x:dest_x+bw]
                    blended = (obj_crop * alpha + roi * (1.0 - alpha)).astype(np.uint8)
                    output[dest_y:dest_y+bh, dest_x:dest_x+bw] = blended

            # --- CASE B: Object enters LEFT side -> Teleport to RIGHT side ---
            elif obj_center_x < col1:
                # Calculate corresponding position on Right panel
                dest_x = min(w - bw, x + col2)
                dest_y = y
                
                if dest_x >= col2 and dest_y + bh <= h:
                    # 1. Clean original object out of Left side using learned background
                    output[y:y+bh, x:x+bw] = (background[y:y+bh, x:x+bw] * alpha + 
                                              output[y:y+bh, x:x+bw] * (1.0 - alpha)).astype(np.uint8)

                    # 2. Paste isolated object onto Right side
                    roi = output[dest_y:dest_y+bh, dest_x:dest_x+bw]
                    blended = (obj_crop * alpha + roi * (1.0 - alpha)).astype(np.uint8)
                    output[dest_y:dest_y+bh, dest_x:dest_x+bw] = blended

        # 3. Draw 3-part Vertical Dividing Lines
        cv2.line(output, (col1, 0), (col1, h), (100, 100, 100), 1, cv2.LINE_AA)
        cv2.line(output, (col2, 0), (col2, h), (100, 100, 100), 1, cv2.LINE_AA)

        # 4. Draw Glowing Portals along boundaries
        # Portal 1 (Left Boundary) -> Orange (BGR: 0, 140, 255)
        draw_portal_ring(output, portal_left_center, radius=65, color_bgr=(0, 140, 255))
        
        # Portal 2 (Right Boundary) -> Blue (BGR: 255, 165, 0)
        draw_portal_ring(output, portal_right_center, radius=65, color_bgr=(255, 165, 0))

        # Labels
        cv2.putText(output, "PORTAL 1", (col1 - 100, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2)
        cv2.putText(output, "PORTAL 2", (col2 + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)

        cv2.imshow("Portal Teleporter", output)

        # Press 'q' or 'ESC' to exit, 'r' to relearn background
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break
        elif key == ord('r'):
            return run_portal_system(video_source)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Pass '0' for live webcam feed or a video file path (e.g. "sample.mp4")
    run_portal_system(0)