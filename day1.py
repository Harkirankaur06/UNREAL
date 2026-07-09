import cv2
import numpy as np
import time

# Open Webcam Feed
cap = cv2.VideoCapture(0)

# State Management
is_calibrated = False
is_levitating = False

# Layout and Sizing Configuration
box_w, box_h = 160, 160
float_y = 0
target_hover_height = -80  # Keeps it locked a few real inches above your hand/head

print("🔮 UNREAL // LIVE VIEWFINDER PORTAL")
print("1. Get comfortable in front of the camera.")
print("2. Position the object inside the center targeting zone.")
print("3. Press [SPACE] ONLY when you are completely ready to isolate it.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    display_frame = frame.copy()
    key = cv2.waitKey(1) & 0xFF

    # --- DESIGNER CAMERA VIEWPORT HUD OVERLAY ---
    bracket_len = 25
    # Top-Left
    cv2.line(display_frame, (40, 40), (40 + bracket_len, 40), (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(display_frame, (40, 40), (40, 40 + bracket_len), (255, 255, 255), 2, cv2.LINE_AA)
    # Top-Right
    cv2.line(display_frame, (w - 40, 40), (w - 40 - bracket_len, 40), (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(display_frame, (w - 40, 40), (w - 40, 40 + bracket_len), (255, 255, 255), 2, cv2.LINE_AA)
    
    # Blinking Recording Light
    if int(time.time() * 2) % 2 == 0:
        cv2.circle(display_frame, (55, 65), 6, (0, 0, 255), -1, cv2.LINE_AA)
    cv2.putText(display_frame, "REC  UNREAL_CAM_01", (75, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Dynamic Center Alignment Target coordinates
    cx, cy = int(w / 2), int(h / 2)
    box_x, box_y = cx - int(box_w / 2), cy - int(box_h / 2)

    # --- PHASE 1: COMPLETELY LIVE PREVIEW & ALIGNMENT ---
    if not is_calibrated:
        # Subtle targeting bracket to help you line up your object comfortably
        cv2.rectangle(display_frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(display_frame, "ALIGN TARGET HERE & PRESS [SPACE]", (box_x - 30, box_y - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
        
        # User explicitly triggers when they are completely ready
        if key == ord(' '):
            print("\n📸 POSITION CAPTURED. Use your mouse on the popup window to cut out the object.")
            # Launch the manual selection tool on the exact frozen frame the user chose!
            bbox = cv2.selectROI("TARGET BOUNDARY ISOLATION", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("TARGET BOUNDARY ISOLATION")
            
            ox, oy, ow, oh = [int(v) for v in bbox]
            
            # Prevent empty selections from crashing the matrix
            if ow > 10 and oh > 10:
                # Execute instant high-precision silhouette extraction
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                mask = np.zeros(frame.shape[:2], np.uint8)
                
                cv2.grabCut(frame, mask, (ox, oy, ow, oh), bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                precise_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
                precise_mask = cv2.morphologyEx(precise_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
                
                # Cache the exact silhouette profile
                isolated_texture = cv2.bitwise_and(frame, frame, mask=precise_mask)
                object_crop = isolated_texture[oy:oy+oh, ox:ox+ow]
                mask_crop = precise_mask[oy:oy+oh, ox:ox+ow]
                
                is_calibrated = True
                is_levitating = True  # Instantly start floating up once selected!
                float_y = 0

    # --- PHASE 2: FLAWLESS LIVE LEVITATION & BACKGROUND RENDERING ---
    else:
        if is_levitating:
            # Smoothly climb until hitting the exact hover altitude anchor point
            if float_y > target_hover_height:
                float_y -= 4  
                
            # 1. Live Background Patching: Instant real-time inpaint healing
            live_inpainted_bg = cv2.inpaint(frame, precise_mask, 5, cv2.INPAINT_TELEA)
            display_frame = live_inpainted_bg
            
            # 2. Render Precise Silhouette float layer over the live video matrix
            current_y = oy + float_y
            if current_y > 10 and (current_y + oh) < h:
                roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask_crop))
                img_fg = cv2.bitwise_and(object_crop, object_crop, mask=mask_crop)
                
                display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                
                # Cyber stability HUD tag
                cv2.putText(display_frame, "ALT_LOCKED // SHIELD_ACTIVE", (ox, current_y + oh + 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)

        # Reset button configuration
        if key == ord('r') or key == ord('R'):
            is_calibrated = False
            is_levitating = False
            float_y = 0

    # General System Logging UI
    cv2.putText(display_frame, f"CORE: {'ELEVATION_SUSPENDED' if is_levitating else 'LIVE_CALIBRATION_PENDING'}", 
                (w - 320, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow("UNREAL - Day 1", display_frame)
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()