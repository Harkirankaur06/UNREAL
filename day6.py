import cv2
import numpy as np
import random
from collections import deque

# Define the color bounds for your wand (Example: Bright Blue)
lower_color = np.array([90, 50, 70])
upper_color = np.array([128, 255, 255])

# Store the points of the drawing trail
points = deque(maxlen=60)  # Shorter length keeps the sparkles fresh and fading

# Initialize webcam
cap = cv2.VideoCapture(0)

print("Sparkle Wand Active! Press 'c' to clear, 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    # Flip the frame for a mirror effect
    frame = cv2.flip(frame, 1)
    
    # Pre-process frame for color tracking
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        
        if M["m00"] > 0 and radius > 10:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            points.appendleft(center)
            
            # Draw a bright glowing core at the tip of the wand
            cv2.circle(frame, center, 8, (255, 255, 255), -1)
            cv2.circle(frame, center, 14, (0, 255, 255), 2)
    else:
        points.appendleft(None)
        
    # --- SPARKLE ENGINE ---
    # Loop through the tracked points history to generate particles
    for i in range(len(points)):
        if points[i] is None:
            continue
            
        # As points get older (further back in history), they sparkle less
        fade_factor = (len(points) - i) / len(points)
        
        if random.random() < 0.4 * fade_factor:  # Control density of sparkles
            # Generate 2-4 small sparkle particles per active point
            for _ in range(random.randint(2, 4)):
                # Randomize offset so particles scatter slightly around the wand path
                offset_x = random.randint(-15, 15)
                offset_y = random.randint(-15, 15)
                sparkle_pos = (points[i][0] + offset_x, points[i][1] + offset_y)
                
                # Dynamic particle sizing
                p_radius = random.randint(1, 4)
                
                # Pick a magical color palette (Gold, Cyan, White)
                color = random.choice([
                    (0, 215, 255),   # Gold/Yellow
                    (255, 255, 100), # Cyan/Magic Blue
                    (255, 255, 255)  # Pure white core
                ])
                
                # Draw the individual sparkle particle
                cv2.circle(frame, sparkle_pos, p_radius, color, -1)

    # HUD UI Text overlay
    cv2.putText(frame, "Day 6: Magic Sparkle Wand", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.imshow("Wand Canvas", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        points.clear()
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()