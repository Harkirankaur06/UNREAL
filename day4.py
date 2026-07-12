import cv2
import numpy as np
import time

# Open live webcam capture
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Camera warming up... Get ready to step out of the frame.")

# 1. VISIBLE BACKGROUND CALIBRATION STEP (3-Second Countdown Loop)
start_time = time.time()
bg_frame = None

while time.time() - start_time < 3.0:
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    bg_frame = frame.copy() # Keeps saving the latest clean frame as the camera adjusts
    
    # Show a live preview window so you can see if you are out of the frame
    cv2.putText(bg_frame, "LEARNING BACKGROUND... STAY OUT OF FRAME", (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Hulk Part 1: Background Subtraction Layer", bg_frame)
    cv2.waitKey(1)

# Process the final baseline background frame captured at the end of the 3 seconds
bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)

print("\nBackground successfully learned! Step into the frame.")

# 2. MAIN CONVERSION LOOP
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Compare live frame to the learned background matrix
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    
    # Calculate difference between the learned empty room and you
    frame_delta = cv2.absdiff(bg_gray, gray_frame)
    _, body_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
    
    # Clean up the silhouette mask holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel)
    body_mask = cv2.dilate(body_mask, None, iterations=2)
    
    # Create the cinematic dark dirty green tint layer
    tint_layer = np.zeros_like(frame)
    tint_layer[:] = [30, 85, 40]  # Dark olive green (BGR)
    
    # Blend tint over original textures
    green_body = cv2.addWeighted(frame, 0.5, tint_layer, 0.5, 0)
    
    # Smooth edges
    feathered_mask = cv2.GaussianBlur(body_mask, (31, 31), 0)
    alpha = feathered_mask[:, :, np.newaxis] / 255.0
    
    # Apply green tint strictly to the moving body shape silhouette
    output_frame = (alpha * green_body + (1.0 - alpha) * frame).astype(np.uint8)
    
    cv2.imshow("Hulk Part 1: Background Subtraction Layer", output_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()