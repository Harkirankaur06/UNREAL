import cv2
import numpy as np
import math
import time

def draw_animated_portal(img, center, rx, ry, color_bgr, frame_count=0):
    """Renders a sleek, animated portal overlay on top of the live video."""
    overlay = img.copy()
    cx, cy = center
    num_pts = 60
    pts = []
    
    for i in range(num_pts):
        theta = (2 * math.pi / num_pts) * i
        # Organic wave pulse effect
        wave = 5 * math.sin(theta * 5 + frame_count * 0.15)
        x = cx + (rx + wave) * math.cos(theta)
        y = cy + (ry + wave / 2) * math.sin(theta)
        pts.append([int(x), int(y)])
        
    pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
    
    # Outer Glowing Ring
    cv2.polylines(overlay, [pts_arr], True, color_bgr, 12, cv2.LINE_AA)
    # Bright Inner Core Edge
    cv2.polylines(overlay, [pts_arr], True, (255, 255, 255), 3, cv2.LINE_AA)
    
    # Blend glowing edges onto camera frame
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

def run_realtime_teleporter(video_source=0):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # --- STEP 1: LEARN CLEAN BACKGROUND (2 SECONDS) ---
    print("\n--- LEARNING BACKGROUND ---")
    print("Please keep the camera clear of moving objects for 2 seconds...")
    bg_frames = []
    start_time = time.time()
    
    while time.time() - start_time < 2.0:
        ret, frame = cap.read()
        if not ret: break
        bg_frames.append(frame.astype(np.float32))
        
        remaining = max(0, 2.0 - (time.time() - start_time))
        disp = frame.copy()
        cv2.putText(disp, f"Step out of frame... {remaining:.1f}s", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.imshow("Real-Time Teleporter", disp)
        cv2.waitKey(1)

    # Median background frame
    bg = np.median(bg_frames, axis=0).astype(np.uint8)
    bg_gray = cv2.GaussianBlur(cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    print("Background acquired! Portals are LIVE.\n")

    # --- PORTAL POSITIONS ---
    p1_center = (int(w * 0.3), int(h * 0.5))  # Portal 1 (Entrance - Orange)
    p2_center = (int(w * 0.7), int(h * 0.5))  # Portal 2 (Exit - Blue)
    rx, ry = 70, 130                           # Portal Dimensions

    # X-boundary where slicing occurs
    p1_boundary_x = p1_center[0]
    offset_x = p2_center[0] - p1_center[0]
    offset_y = p2_center[1] - p1_center[1]

    frame_count = 0

    print("Move your hand or an object into Portal 1 (Left) in real time!")
    print("Press 'q' or 'ESC' to exit, or 'r' to recalibrate background.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1

        output = frame.copy()

        # 1. Motion/Foreground Detection
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
        diff = cv2.absdiff(bg_gray, gray)
        _, fg_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
        # Clean noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)

        # 2. CREATE REAL-TIME PORTAL SLICES
        # Part A: What is OUTSIDE Portal 1 (keep normal live feed)
        # Part B: What enters PAST Portal 1 boundary line -> erase from Portal 1, teleport to Portal 2
        
        # Create mask for the region entering past Portal 1 boundary (X > p1_boundary_x)
        teleport_region_mask = fg_mask.copy()
        teleport_region_mask[:, :p1_boundary_x] = 0  # Ignore anything to the left of Portal 1 center

        # Create soft Alpha Matte for smooth edge blending
        alpha_blur = cv2.GaussianBlur(teleport_region_mask, (15, 15), 0)
        alpha = (alpha_blur / 255.0)[:, :, np.newaxis]

        # A. ERASE object inside Portal 1 (Blend in the clean background)
        output = (bg * alpha + output * (1.0 - alpha)).astype(np.uint8)

        # B. SHIFT & PROJECT object out of Portal 2
        # Shift the extracted live object slice by the offset between portals
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        shifted_frame = cv2.warpAffine(frame, M, (w, h))
        shifted_alpha = cv2.warpAffine(alpha, M, (w, h))[:, :, np.newaxis]

        # Composite the shifted live object emerging from Portal 2
        output = (shifted_frame * shifted_alpha + output * (1.0 - shifted_alpha)).astype(np.uint8)

        # 3. DRAW LIVE PORTALS OVERLAY
        # Entrance (Orange) & Exit (Blue)
        draw_animated_portal(output, p1_center, rx, ry, (30, 160, 255), frame_count)
        draw_animated_portal(output, p2_center, rx, ry, (255, 200, 50), frame_count)

        # On-screen Labels
        cv2.putText(output, "PORTAL 1 (ENTRANCE)", (p1_center[0] - 110, p1_center[1] - ry - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 160, 255), 2)
        cv2.putText(output, "PORTAL 2 (EXIT)", (p2_center[0] - 80, p2_center[1] - ry - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 50), 2)

        cv2.imshow("Real-Time Teleporter", output)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            break
        elif key == ord('r'):
            return run_realtime_teleporter(video_source)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_realtime_teleporter(0)