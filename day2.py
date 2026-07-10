import cv2
import numpy as np
import random
import time

# --- CONFIGURATION ---
# Define the coordinates [ymin, ymax, xmin, xmax] of the background object you want to float.
# Adjust these numbers based on where your object sits in your webcam frame!
OBJ_ROI = [200, 350, 150, 300] 
# ---------------------

cap = cv2.VideoCapture(0)

# Give the webcam a moment to warm up and capture a clean background
time.sleep(1)
ret, background_template = cap.read()

# States: 0 = Normal, 1 = Breach (Glitches + Floating), 2 = Snap Drop
state = 0  

# Physics variables
y_offset = 0.0
float_speed = 0.8       # Slow upward drift
gravity = 1.5           # Heavy downward acceleration
drop_velocity = 0.0
is_dropping = False

print("=== SPIDER-VERSE BREACH INITIALIZED ===")
print("Press SPACEBAR to trigger the Breach (Glitch & Float).")
print("Press SPACEBAR again to trigger the Snap Drop.")
print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    h, w, _ = frame.shape
    output_frame = frame.copy()

    # ----------------------------------------------------
    # STATE 1: THE BREACH (Color Glitch + Body Glitch + Float)
    # ----------------------------------------------------
    if state == 1 or (state == 2 and is_dropping):
        
        # --- 1. SPIDER-VERSE COLOR GLITCH (Chromatic Aberration) ---
        b, g, r = cv2.split(frame)
        shift_amount = random.randint(8, 15)
        
        # Shift Red channel left, Blue channel right, leave Green static
        r_shifted = np.roll(r, -shift_amount, axis=1)
        b_shifted = np.roll(b, shift_amount, axis=1)
        glitch_frame = cv2.merge((b_shifted, g, r_shifted))
        
        # Remap colors heavily toward Spider-Verse neon pinks and purples
        # Boost reds/blues and suppress greens slightly for that comic print look
        glitch_frame[:, :, 2] = cv2.add(glitch_frame[:, :, 2], 40) # Amplify Pink/Red
        glitch_frame[:, :, 0] = cv2.add(glitch_frame[:, :, 0], 20) # Amplify Blue/Purple
        
        # --- 2. BODY GLITCH (Horizontal Slicing) ---
        # Apply slice displacement to random horizontal bands
        num_slices = random.randint(3, 7)
        for _ in range(num_slices):
            slice_y = random.randint(0, h - 30)
            slice_h = random.randint(10, 30)
            slice_shift = random.randint(-25, 25)
            
            glitch_frame[slice_y:slice_y+slice_h, :] = np.roll(
                glitch_frame[slice_y:slice_y+slice_h, :], slice_shift, axis=1
            )
        
        output_frame = glitch_frame.copy()

        # --- 3. ZERO-G DRIFT PHYSICS ---
        ymin, ymax, xmin, xmax = OBJ_ROI
        obj_h, obj_w = ymax - ymin, xmax - xmin
        
        # Patch the original object location using our clean background template
        output_frame[ymin:ymax, xmin:xmax] = background_template[ymin:ymax, xmin:xmax]
        
        if state == 1:
            # Slowly float upwards
            y_offset -= float_speed
            # Keep it from floating entirely off the top screen boundary
            if ymin + int(y_offset) < 10:
                y_offset = float(-ymin + 10)
        elif state == 2 and is_dropping:
            # Apply gravitational acceleration
            drop_velocity += gravity
            y_offset += drop_velocity
            
            # Check if it hit the ground (original position)
            if y_offset >= 0:
                y_offset = 0
                state = 0 # Return entirely to normal room state
                is_dropping = False

        # Calculate new floating coordinates safely inside frame boundaries
        new_ymin = max(0, ymin + int(y_offset))
        new_ymax = min(h, ymax + int(y_offset))
        
        # If the object layer moves, slice out its pixels from the original frame and overlay it
        if new_ymax > new_ymin:
            obj_pixels = frame[ymin:ymax, xmin:xmax]
            # Resize or slice adjust if clipped at the top boundary
            cropped_h = new_ymax - new_ymin
            output_frame[new_ymin:new_ymax, xmin:xmax] = obj_pixels[0:cropped_h, :]

    # ----------------------------------------------------
    # STATE 0: NORMAL ROOM
    # ----------------------------------------------------
    else:
        # Just display the normal live camera feed
        pass

    # Draw a subtle guide box when in setup/normal mode so you know where your object is
    if state == 0:
        cv2.rectangle(output_frame, (OBJ_ROI[2], OBJ_ROI[0]), (OBJ_ROI[3], OBJ_ROI[1]), (0, 255, 120), 1)
        cv2.putText(output_frame, "Target Object Space", (OBJ_ROI[2], OBJ_ROI[0]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 120), 1)

    # Render frame
    cv2.imshow("Day 2: Multiverse Breach Engine", output_frame)
    
    # Key listener
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '): # SPACEBAR
        if state == 0:
            state = 1 # Trigger breach
            y_offset = 0.0
            print("-> BREACH ACTIVE! Reality is breaking down...")
        elif state == 1:
            state = 2 # Trigger drop
            is_dropping = True
            drop_velocity = 0.0
            print("-> SNAP EVENT! Gravity re-engaging...")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()