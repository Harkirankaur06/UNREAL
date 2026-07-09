import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)

# State Variables
background_captured = False
is_levitating = False
bg_frame = None

# Levitation Physics
float_y = 0
max_float_inches = 150 # Pixels equivalent to a few inches
glow_radius = 5
glow_direction = 1

print("🔮 UNREAL: Day 1 Initialization...")
print("STEP 1: Please move out of the camera frame. Press [B] to capture the clean background.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    display_frame = frame.copy()
    key = cv2.waitKey(1) & 0xFF

    # ---- STEP 1: CAPTURE BACKGROUND ----
    if key == ord('b') or key == ord('B'):
        # Take a high-quality static snapshot of the empty room
        bg_frame = frame.copy()
        background_captured = True
        print("✅ Background learned successfully! Step into the frame.")
        print("STEP 2: Hold your hand open with an object. Press [SPACE] to levitate.")

    if background_captured:
        # ---- STEP 2: MOTION / HAND ISOLATION MATRICES ----
        # Find exactly what is different between the current frame and the empty room
        diff = cv2.absdiff(frame, bg_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, binary_mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Clean up the noise using morphological closing
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        # ---- STEP 3: LEVITATION MECHANICS ----
        if is_levitating:
            # 1. Float translation tracking
            if abs(float_y) < max_float_inches:
                float_y -= 4  # Moves up 4 pixels per frame
            
            # 2. Create the output canvas starting with the clean learned background
            display_frame = bg_frame.copy()
            
            # 3. Create shifted coordinates for the floating element
            M = np.float32([[1, 0, 0], [0, 1, float_y]])
            shifted_mask = cv2.warpAffine(object_mask, M, (w, h))
            shifted_texture = cv2.warpAffine(object_texture, M, (w, h))
            
            # 4. Composite the shifted object back over the clean background
            inv_shifted_mask = cv2.bitwise_not(shifted_mask)
            bg_under = cv2.bitwise_and(display_frame, display_frame, mask=inv_shifted_mask)
            fg_over = cv2.bitwise_and(shifted_texture, shifted_texture, mask=shifted_mask)
            display_frame = cv2.add(bg_under, fg_over)
            
            # 5. Neon Energy Boundary Box
            glow_radius += glow_direction
            if glow_radius > 12 or glow_radius < 4:
                glow_direction *= -1
            
            # Find boundaries of the floating mask to wrap it in a glowing aura
            contours, _ = cv2.findContours(shifted_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                ox, oy, ow, oh = cv2.boundingRect(max(contours, key=cv2.contourArea))
                cv2.rectangle(display_frame, (ox-glow_radius, oy-glow_radius), 
                              (ox+ow+glow_radius, oy+oh+glow_radius), (255, 255, 0), 2)
                
        else:
            # Standby: Highlight everything the camera thinks is your hand + object
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 1000:
                    # Draw a dynamic bounding box tightly tracking the object in your hand
                    ox, oy, ow, oh = cv2.boundingRect(largest_contour)
                    cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 0), 2)
                    cv2.putText(display_frame, "READY FOR UNREAL OVERRIDE", (ox, oy - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Trigger Event
        if key == ord(' ') and not is_levitating:
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest_contour) > 1000:
                    # Snap the precise contours and texture arrays at this exact millisecond
                    ox, oy, ow, oh = cv2.boundingRect(largest_contour)
                    
                    # Create a localized mask for just the active item/hand cluster
                    object_mask = np.zeros_like(binary_mask)
                    cv2.drawContours(object_mask, [largest_contour], -1, 255, -1)
                    
                    object_texture = frame.copy()
                    is_levitating = True
                    float_y = 0

    # Reset System
    if key == ord('r') or key == ord('R'):
        is_levitating = False
        float_y = 0

    # Render HUD Details
    cv2.putText(display_frame, f"UNREAL | MATRIX STATE: {'LEVITATING' if is_levitating else 'INITIALIZED' if background_captured else 'CALIBRATING BG'}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    if not background_captured:
        cv2.putText(display_frame, "Step out of frame and press [B] to learn the background.", 
                    (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    else:
        cv2.putText(display_frame, "Press [SPACE] to launch levitation sequence. [R] to reset.", 
                    (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("UNREAL - Day 1", display_frame)
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()