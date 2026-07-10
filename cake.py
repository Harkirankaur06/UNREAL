import cv2
import numpy as np
import random
import math
import time

# Initialize Webcam
cap = cv2.VideoCapture(0)

# State Management: 0 = Candles Burning, 1 = Blown Out + Confetti Panic!
state = 0  

# Animation configuration for the cake sliding in from the bottom
cake_y_offset = 300.0  # Start far below the screen boundary
target_offset = 0.0
slide_speed = 6.0      # Lower value = smoother cinematic glide up

# Particle System Configuration for Confetti
num_particles = 140
particles = []

for _ in range(num_particles):
    particles.append({
        'x': random.randint(0, 640),
        'y': random.randint(-400, 0),
        'color': (random.randint(120, 255), random.randint(50, 200), random.randint(180, 255)), # Cyberpunk palette
        'speed_y': random.uniform(4, 8),
        'speed_x': random.uniform(-2.5, 2.5),
        'size': random.randint(4, 10),
        'phase': random.uniform(0, 2 * math.pi)
    })

# Optical Flow Setup variables to track "blowing" motion
ret, prev_frame = cap.read()
if ret:
    prev_frame = cv2.flip(prev_frame, 1)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

print("=== PHANTOM CAKE ENGINE LIVE V2 ===")
print("Watch the cake emerge... Then blow to celebrate!")
print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1) # Mirror mode
    h, w, c = frame.shape
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # --- 1. THE COOL CINEMATIC COLOR GRADE FILTER ---
    # We apply a custom color curve map to create a sleek film look
    # Boosting reds/magentas in highlights, deepening blues in shadows
    b, g, r = cv2.split(frame)
    
    # Create Look-Up Tables (LUT) for professional color grading curves
    lut_r = np.array([np.clip(i + 15 * math.sin(i / 32.0), 0, 255) for i in range(256)]).astype("uint8")
    lut_b = np.array([np.clip(i + 10 * math.cos(i / 64.0), 0, 255) for i in range(256)]).astype("uint8")
    
    r_graded = cv2.LUT(r, lut_r)
    b_graded = cv2.LUT(b, lut_b)
    output_frame = cv2.merge((b_graded, g, r_graded))
    
    # Add a soft cinematic vignette overlay
    kernel_x = cv2.getGaussianKernel(w, w/2)
    kernel_y = cv2.getGaussianKernel(h, h/2)
    vignette_mask = kernel_y * kernel_x.T
    vignette_mask = vignette_mask / np.max(vignette_mask)
    # Blend vignette gently
    output_frame = (output_frame * np.dstack([vignette_mask]*3 + (1.0 - vignette_mask)*0.3)).astype(np.uint8)

    # --- 2. CAKE ANIMATION SEQUENCE (SLIDE UP) ---
    if cake_y_offset > target_offset:
        cake_y_offset -= slide_speed
        if cake_y_offset < target_offset:
            cake_y_offset = target_offset

    # --- 3. OPTICAL FLOW MOTION DETECTION (THE BLOW) ---
    if state == 0 and cake_y_offset == target_offset:
        roi_x_start, roi_x_end = w // 2 - 80, w // 2 + 80
        roi_y_start, roi_y_end = h // 2 - 130, h // 2 - 40
        
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        roi_flow = flow[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        
        magnitude, _ = cv2.cartToPolar(roi_flow[..., 0], roi_flow[..., 1])
        motion_level = np.mean(magnitude)
        
        if motion_level > 4.0:  
            state = 1
            
        prev_gray = gray.copy()

    # --- 4. RENDER THE INTERACTIVE CAKE LAYERS WITH ANIMATION SHIFT ---
    # Apply the cake_y_offset dynamically to move it up from below the frame
    cx, cy = w // 2, h // 2 + 160 + int(cake_y_offset)
    
    # Base Tier
    cv2.rectangle(output_frame, (cx - 110, cy), (cx + 110, cy + 80), (240, 190, 255), -1) 
    cv2.rectangle(output_frame, (cx - 110, cy), (cx + 110, cy + 80), (210, 130, 230), 2)  
    
    # Top Tier
    cv2.rectangle(output_frame, (cx - 75, cy - 50), (cx + 75, cy), (255, 220, 240), -1)
    cv2.rectangle(output_frame, (cx - 75, cy - 50), (cx + 75, cy), (230, 140, 190), 2)
    
    # Candles
    candle_positions = [cx - 40, cx, cx + 40]
    for candle_x in candle_positions:
        cv2.line(output_frame, (candle_x, cy - 50), (candle_x, cy - 72), (255, 255, 255), 3) 
        
        if state == 0:
            flicker = random.randint(-2, 2)
            # Stylized glowing flames
            cv2.ellipse(output_frame, (candle_x, cy - 82 + (flicker // 2)), (6, 9 + flicker), 
                        0, 0, 360, (0, 130, 255), -1) 
            cv2.ellipse(output_frame, (candle_x, cy - 79), (3, 5), 
                        0, 0, 360, (0, 240, 255), -1) 

    # --- 5. CELEBRATION DISPERSION ---
    if state == 1:
        for p in particles:
            p['y'] += p['speed_y']
            p['x'] += p['speed_x'] + math.sin(time.time() + p['phase']) * 1.5 
            
            if p['y'] > h:
                p['y'] = random.randint(-50, -10)
                p['x'] = random.randint(0, w)
                
            ix, iy = int(p['x']), int(p['y'])
            if p['size'] % 2 == 0:
                cv2.circle(output_frame, (ix, iy), p['size'], p['color'], -1)
            else:
                cv2.rectangle(output_frame, (ix, iy), (ix + p['size'], iy + p['size']), p['color'], -1)

        # Dynamic glowing text effect
        text = "HAPPY BIRTHDAY MOM!"
        font = cv2.FONT_HERSHEY_TRIPLEX
        text_scale = 1.1
        thickness = 2
        
        text_size = cv2.getTextSize(text, font, text_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 60
        
        pulse = int(abs(math.sin(time.time() * 5)) * 10)
        
        # Dual overlay text depth for neon flare finish
        cv2.putText(output_frame, text, (text_x, text_y), font, text_scale, (255, 0, 128), thickness + 5 + (pulse // 2), cv2.LINE_AA)
        cv2.putText(output_frame, text, (text_x, text_y), font, text_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Render Display Window
    cv2.imshow("Day 2: Phantom Birthday Cake Engine v2", output_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()