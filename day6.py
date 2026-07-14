import cv2
import numpy as np
from collections import deque

# Define the color bounds for your wand (Example: Bright Blue)
# If using a green object, try lower=[35, 50, 50], upper=[85, 255, 255]
lower_color = np.array([90, 50, 70])
upper_color = np.array([128, 255, 255])

# Store the points of the drawing trail (max 500 points for memory)
points = deque(maxlen=500)

# Initialize webcam
cap = cv2.VideoCapture(0)

print("Wand Tracker Active! Hold up your colored object to start drawing.")
print("Press 'c' to clear the canvas, or 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    # Flip the frame horizontally so it acts like a mirror (easier to navigate!)
    frame = cv2.flip(frame, 1)
    
    # Blur to reduce noise and convert to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Create a binary mask for the targeted color
    mask = cv2.inRange(hsv, lower_color, upper_color)
    
    # Clean up the edges of the mask
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    # Find outlines (contours) of the colored object
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    
    # Only proceed if at least one contour is found
    if len(contours) > 0:
        # Find the largest contour (assumed to be your wand)
        c = max(contours, key=cv2.contourArea)
        
        # Calculate the minimum enclosing circle around it
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        
        # Calculate moments to find the exact center of mass
        M = cv2.moments(c)
        if M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            # Only track if the object is reasonably close/large enough
            if radius > 10:
                # Draw a glowing circle around the tip of the wand
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                # Draw the tracking point center
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                
                # Append the coordinate to our drawing trail list
                points.appendleft(center)
    else:
        # If the wand leaves the screen, add a None break so lines don't wrap weirdly
        points.appendleft(None)
        
    # Draw the trail on the frame
    for i in range(1, len(points)):
        if points[i - 1] is None or points[i] is None:
            continue
            
        # Draw a line segment between consecutive points (Neon Green Line)
        # You can gradually decrease thickness to give a "fading tail" effect
        thickness = int(np.sqrt(len(points) / float(i + 1)) * 2.5)
        cv2.line(frame, points[i - 1], points[i], (0, 255, 0), thickness)
        
    # HUD UI Text overlay
    cv2.putText(frame, "Day 6: Magic Wand Air-Doodler", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Display feed
    cv2.imshow("Wand Canvas", frame)
    
    key = cv2.waitKey(1) & 0xFF
    # Press 'c' to clear the drawing canvas
    if key == ord('c'):
        points.clear()
    # Press 'q' to exit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()