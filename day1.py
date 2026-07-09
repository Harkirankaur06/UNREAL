import cv2
import numpy as np

# 1. Initialize the Adaptive Background Subtractor
# history=100 means it learns quickly based on the last 100 frames
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40, detectShadows=False)

cap = cv2.VideoCapture(0)

is_levitating = False
saved_texture = None
saved_object_mask = None

float_y = 0
max_float_pixels = 180 
glow_radius = 5
glow_direction = 1

print("🔮 UNREAL: Day 1 (Live Adaptive Mode) Active!")
print("Sit still for 2 seconds to let the camera learn your background, then press [SPACE] to lift an object.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    display_frame = frame.copy()
    key = cv2.waitKey(1) & 0xFF

    # 2. Update the background model live on every single frame
    # This outputs a binary mask of what is moving/dynamic in the frame
    fg_mask = bg_subtractor.apply(frame)
    
    # Clean up small pixel noise using morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

    # --- 3. FILTER OUT SKIN AND FACES ---
    # Convert to YCrCb space to isolate skin tones
    ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    lower_skin = np.array([0, 133, 77], dtype=np.uint8)
    upper_skin = np.array([255, 173, 127], dtype=np.uint8)
    skin_mask = cv2.inRange(ycrcb_frame, lower_skin, upper_skin)
    
    # Object mask is the movement MINUS skin/face pixels
    only_object_mask = cv2.bitwise_and(fg_mask, cv2.bitwise_not(skin_mask))
    only_object_mask = cv2.erode(only_object_mask, np.ones((3,3), np.uint8), iterations=1)
    only_object_mask = cv2.dilate(only_object_mask, np.ones((5,5), np.uint8), iterations=2)

    # 4. LEVITATION STATE MACHINE
    if is_levitating:
        if abs(float_y) < max_float_pixels:
            float_y -= 5  # Float speed
        
        # Get the dynamically generated background frame from the subtractor model
        live_bg = bg_subtractor.getBackgroundImage()
        if live_bg is None:
            live_bg = frame.copy() # Fallback if model isn't fully ready
            
        display_frame = live_bg.copy()
        
        # Shift the saved object texture upward
        M = np.float32([[1, 0, 0], [0, 1, float_y]])
        shifted_mask = cv2.warpAffine(saved_object_mask, M, (w, h))
        shifted_texture = cv2.warpAffine(saved_texture, M, (w, h))
        
        # Composite object over the live generated background
        inv_shifted_mask = cv2.bitwise_not(shifted_mask)
        bg_under = cv2.bitwise_and(display_frame, display_frame, mask=inv_shifted_mask)
        fg_over = cv2.bitwise_and(shifted_texture, shifted_texture, mask=shifted_mask)
        display_frame = cv2.add(bg_under, fg_over)
        
        # Cyber Glow Box
        glow_radius += glow_direction
        if glow_radius > 12 or glow_radius < 4: glow_direction *= -1
        contours, _ = cv2.findContours(shifted_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            ox, oy, ow, oh = cv2.boundingRect(max(contours, key=cv2.contourArea))
            cv2.rectangle(display_frame, (ox-glow_radius, oy-glow_radius), 
                          (ox+ow+glow_radius, oy+oh+glow_radius), (255, 255, 0), 2)
    else:
        # STANDBY: Track the largest non-skin moving object
        contours, _ = cv2.findContours(only_object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 800: # Filter out minor noise
                ox, oy, ow, oh = cv2.boundingRect(largest_contour)
                
                # Draw target overlay box around the isolated object
                cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 0), 2)
                cv2.putText(display_frame, "LOCK ON ACTIVE", (ox, oy - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # 5. TRIGGER MAGIC OVERRIDE
    if key == ord(' ') and not is_levitating:
        contours, _ = cv2.findContours(only_object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 800:
                saved_object_mask = np.zeros_like(only_object_mask)
                cv2.drawContours(saved_object_mask, [largest_contour], -1, 255, -1)
                
                saved_texture = frame.copy()
                is_levitating = True
                float_y = 0

    if key == ord('r') or key == ord('R'):
        is_levitating = False
        float_y = 0

    # UI Details
    cv2.putText(display_frame, f"UNREAL | ADAPTIVE OVERRIDE: {'LEVITATING' if is_levitating else 'TRACKING'}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.putText(display_frame, "Press [SPACE] to launch levitation. [R] to reset.", 
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("UNREAL - Day 1", display_frame)
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()