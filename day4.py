import cv2
import numpy as np

# Open live webcam capture
cap = cv2.VideoCapture(0)

print("Hulk Part 1: Body Recognition & Green Tint initialized.")
print("Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip horizontally for natural mirror look
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # 1. Convert to HSV to segment out the human subject from the blue wall background
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Range designed to target human skin + typical clothing tones, explicitly ignoring the blue background spectrum
    lower_human = np.array([0, 5, 20], dtype=np.uint8)
    upper_human = np.array([40, 255, 255], dtype=np.uint8)
    body_mask = cv2.inRange(hsv, lower_human, upper_human)
    
    # 2. Advanced Morphology to close gaps (combining your skin, face, and shirt into one solid silhouette)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel_close)
    body_mask = cv2.dilate(body_mask, None, iterations=2)
    
    # 3. Create the Cinematic Dark Dirty Green Tint Layer
    tint_layer = np.zeros_like(frame)
    # BGR format: A deep, muted comic-book style olive green
    tint_layer[:] = [30, 85, 40]  
    
    # Blend the green tint over the frame (50% original textures + 50% green tint)
    green_body = cv2.addWeighted(frame, 0.5, tint_layer, 0.5, 0)
    
    # 4. Smooth out the edges of the mask so the transition isn't harsh or jagged
    feathered_mask = cv2.GaussianBlur(body_mask, (35, 35), 0)
    alpha = feathered_mask[:, :, np.newaxis] / 255.0
    
    # Composite: Apply the dirty green matrix ONLY to the human silhouette area
    output_frame = (alpha * green_body + (1.0 - alpha) * frame).astype(np.uint8)
    
    # Display the result for Part 1
    cv2.imshow("Hulk Transformation - Part 1: Body Green Tint", output_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()