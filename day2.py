import cv2
import numpy as np
import random
import time

cap = cv2.VideoCapture(0)

# Allow camera to adjust and capture a clean background for patching
time.sleep(1)
ret, background_cache = cap.read()

# State Management: 0 = Setup, 1 = Float/Distort, 2 = Gravitational Drop
state = 0  
y_offset = 0.0
float_speed = 0.6
gravity = 1.8
drop_velocity = 0.0
is_dropping = False

print("=== REFINE SPIDER-VERSE BREACH ===")
print("Press SPACEBAR to make detected objects distort and float.")
print("Press SPACEBAR again to crash them down.")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    h, w, _ = frame.shape
    output_frame = frame.copy()
    
    # --- 1. OBJECT SELECTION via HSV COLOR MASKING ---
    # This example isolates vibrant/colorful objects. 
    # Adjust thresholds to target specific colors in your room!
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_color = np.array([0, 100, 100])    # Broad bright colors
    upper_color = np.array([179, 255, 255])
    object_mask = cv2.inRange(hsv, lower_color, upper_color)
    
    # Clean mask noise
    kernel = np.ones((5, 5), np.uint8)
    object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_CLOSE, kernel)
    object_mask = cv2.dilate(object_mask, kernel, iterations=1)

    # --- 2. THE DISTORTION & FLOAT ENGINE ---
    if state == 1 or (state == 2 and is_dropping):
        # Create a blank canvas for object distortions
        distorted_objects_layer = np.zeros_like(frame)
        
        # Calculate isolated chromatic distortion for objects ONLY
        b, g, r = cv2.split(frame)
        shift = random.randint(6, 12)
        r_shifted = np.roll(r, -shift, axis=1)
        b_shifted = np.roll(b, shift, axis=1)
        glitched_pixels = cv2.merge((b_shifted, g, r_shifted))
        
        # Spiderverse color tinting (strictly on the glitched pixels)
        glitched_pixels[:, :, 2] = cv2.add(glitched_pixels[:, :, 2], 35) # Red boost
        glitched_pixels[:, :, 0] = cv2.add(glitched_pixels[:, :, 0], 15) # Blue boost
        
        # Apply local horizontal slice distortions within the object mask boundaries
        num_slices = random.randint(2, 5)
        for _ in range(num_slices):
            slice_y = random.randint(0, h - 20)
            slice_h = random.randint(5, 20)
            slice_shift = random.randint(-15, 15)
            glitched_pixels[slice_y:slice_y+slice_h, :] = np.roll(
                glitched_pixels[slice_y:slice_y+slice_h, :], slice_shift, axis=1
            )
            
        # Extract only the distorted objects using the mask
        cv2.copyTo(glitched_pixels, object_mask, distorted_objects_layer)
        
        # Physics updates for floating
        if state == 1:
            y_offset -= float_speed
        elif state == 2 and is_dropping:
            drop_velocity += gravity
            y_offset += drop_velocity
            if y_offset >= 0:
                y_offset = 0
                state = 0
                is_dropping = False
                
        # --- 3. SEAMLESS BACKGROUND PATCHING ---
        # Wherever an object was, fill the live frame with the clean background template
        background_patch = cv2.bitwise_and(background_cache, background_cache, mask=object_mask)
        inverse_mask = cv2.bitwise_not(object_mask)
        clean_live_room = cv2.bitwise_and(frame, frame, mask=inverse_mask)
        
        # Merge live room with background filler patches
        output_frame = cv2.add(clean_live_room, background_patch)
        
        # Translate the distorted objects layer dynamically along the Y axis
        M = np.float32([[1, 0, 0], [0, 1, y_offset]])
        floating_objects = cv2.warpAffine(distorted_objects_layer, M, (w, h))
        
        # Overlay floating objects cleanly on top of the patched room
        floating_mask = cv2.cvtColor(floating_objects, cv2.COLOR_BGR2GRAY)
        _, floating_mask = cv2.threshold(floating_mask, 1, 255, cv2.THRESH_BINARY)
        
        inverse_floating_mask = cv2.bitwise_not(floating_mask)
        output_frame = cv2.bitwise_and(output_frame, output_frame, mask=inverse_floating_mask)
        output_frame = cv2.add(output_frame, floating_objects)

    else:
        # State 0: Setup mode, display a subtle green glow around tracked objects
        contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(output_frame, contours, -1, (0, 255, 120), 1)

    cv2.imshow("Day 2: Localized Multiverse Breach", output_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        if state == 0:
            state = 1
            y_offset = 0.0
            print("-> Object anomaly activated. Bracing for drift...")
        elif state == 1:
            state = 2
            is_dropping = True
            drop_velocity = 0.0
            print("-> Gravity restored. Drop initiated...")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()