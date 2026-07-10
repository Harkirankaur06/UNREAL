import cv2
import numpy as np
import random
import math
import time

# Initialize Webcam
cap = cv2.VideoCapture(0)

# State Management: 0 = Candles Burning, 1 = Blown Out + Confetti Panic!
state = 0  

# Particle System Configuration for Confetti
num_particles = 120
particles = []

# Pre-generate random confetti attributes: [x, y, color, speed_y, speed_x, angle]
for _ in range(num_particles):
    particles.append({
        'x': random.randint(0, 640),
        'y': random.randint(-400, 0), # Start above screen
        'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
        'speed_y': random.uniform(3, 7),
        'speed_x': random.uniform(-2, 2),
        'size': random.randint(4, 10),
        'phase': random.uniform(0, 2 * math.pi)
    })

# Optical Flow Setup variables to track "blowing" motion
ret, prev_frame = cap.read()
if ret:
    prev_frame = cv2.flip(prev_frame, 1)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

print("=== PHANTOM CAKE ENGINE ONLINE ===")
print("Lean in and BLOW hard at the candles to trigger the celebration!")
print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1) # Mirror mode
    h, w, c = frame.shape
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    output_frame = frame.copy()
    
    # --- 1. OPTICAL FLOW MOTION DETECTION (THE BLOW) ---
    if state == 0:
        # Define a detection zone right where the candle flames sit
        # Coordinates map to the upper half center of the frame
        roi_x_start, roi_x_end = w // 2 - 80, w // 2 + 80
        roi_y_start, roi_y_end = h // 2 - 130, h // 2 - 40
        
        # Calculate pixel movement velocity between current and previous frame
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        roi_flow = flow[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        
        # Compute magnitude of velocity vector
        magnitude, _ = cv2.cartToPolar(roi_flow[..., 0], roi_flow[..., 1])
        motion_level = np.mean(magnitude)
        
        # If motion spikes above threshold, candles are blown out!
        if motion_level > 3.8:  # Adjust sensitivity if it's too easy/hard to blow
            state = 1
            
        prev_gray = gray.copy()

    # --- 2. RENDER THE INTERACTIVE CAKE LAYERS ---
    cx, cy = w // 2, h // 2 + 200 # Cake baseline position
    
    # Base Tier
    cv2.rectangle(output_frame, (cx - 110, cy), (cx + 110, cy + 80), (230, 180, 255), -1) # Frosting
    cv2.rectangle(output_frame, (cx - 110, cy), (cx + 110, cy + 80), (200, 120, 220), 3)  # Border
    
    # Top Tier
    cv2.rectangle(output_frame, (cx - 75, cy - 50), (cx + 75, cy), (255, 210, 230), -1)
    cv2.rectangle(output_frame, (cx - 75, cy - 50), (cx + 75, cy), (220, 130, 180), 3)
    
    # Candles (Static Lines)
    candle_positions = [cx - 40, cx, cx + 40]
    for candle_x in candle_positions:
        cv2.line(output_frame, (candle_x, cy - 50), (candle_x, cy - 75), (255, 255, 255), 4) # Wick
        
        # Draw flames ONLY if they haven't been blown out yet
        if state == 0:
            # Add random scaling to flicker the flame
            flicker = random.randint(-2, 2)
            cv2.ellipse(output_frame, (candle_x, cy - 85 + (flicker // 2)), (6, 10 + flicker), 
                        0, 0, 360, (0, 140, 255), -1) # Outer flame
            cv2.ellipse(output_frame, (candle_x, cy - 82), (3, 6), 
                        0, 0, 360, (0, 230, 255), -1) # Inner core

    # --- 3. STATE 1: CELEBRATION DISPERSION (CONFETTI & TEXT) ---
    if state == 1:
        # Loop through particle cloud
        for p in particles:
            p['y'] += p['speed_y']
            p['x'] += p['speed_x'] + math.sin(time.time() + p['phase']) * 1.5 # Flutter effect
            
            # Recirculate confetti to top if it hits the bottom
            if p['y'] > h:
                p['y'] = random.randint(-50, -10)
                p['x'] = random.randint(0, w)
                
            # Draw individual confetti flakes (varying shapes)
            ix, iy = int(p['x']), int(p['y'])
            if p['size'] % 2 == 0:
                cv2.circle(output_frame, (ix, iy), p['size'], p['color'], -1)
            else:
                cv2.rectangle(output_frame, (ix, iy), (ix + p['size'], iy + p['size']), p['color'], -1)

        # Dynamic glowing text effect for LinkedIn visibility
        text = "HAPPY BIRTHDAY MOM!"
        font = cv2.FONT_HERSHEY_TRIPLEX
        text_scale = 1.1
        thickness = 2
        
        # Get text sizing to center it perfectly at the top
        text_size = cv2.getTextSize(text, font, text_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 60
        
        # Periodic pulse value using sine wave
        pulse = int(abs(math.sin(time.time() * 5)) * 10)
        
        # Neon Drop Shadow Glow Effect
        cv2.putText(output_frame, text, (text_x, text_y), font, text_scale, (180, 0, 255), thickness + 6 + (pulse // 2), cv2.LINE_AA)
        cv2.putText(output_frame, text, (text_x, text_y), font, text_scale, (255, 0, 128), thickness + 2, cv2.LINE_AA)
        cv2.putText(output_frame, text, (text_x, text_y), font, text_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Render Screen Display Window
    cv2.imshow("Day 2: Phantom Birthday Cake Engine", output_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()