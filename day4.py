import cv2
import numpy as np
import time

# Open live webcam capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Camera warming up... Step out of the frame.")

# 1. VISIBLE BACKGROUND CALIBRATION STEP (3-Second Countdown Loop)
start_time = time.time()
bg_frame = None

while time.time() - start_time < 3.0:
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = cv2.flip(frame, 1)
    bg_frame = frame.copy() 
    
    cv2.putText(bg_frame, "LEARNING BACKGROUND... STAY OUT OF FRAME", (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Hulk Part 2: Body Enlarger Engine", bg_frame)
    cv2.waitKey(1)

# Process master baseline background frame
bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)

print("\nBackground successfully learned! Step into the frame.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # 2. ISOLATE THE HUMAN BODY SILHOUETTE
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    
    frame_delta = cv2.absdiff(bg_gray, gray_frame)
    _, body_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
    
    # Clean up the mask holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel)
    body_mask = cv2.dilate(body_mask, None, iterations=2)
    
    # 3. CREATE THE GREEN HULK MUTATION MATRIX
    tint_layer = np.zeros_like(frame)
    tint_layer[:] = [30, 85, 40]  # Dark olive green (BGR)
    green_body = cv2.addWeighted(frame, 0.5, tint_layer, 0.5, 0)
    
    # Separate the green body from the current camera stream
    isolated_green = cv2.bitwise_and(green_body, green_body, mask=body_mask)
    
    # 4. ENLARGE THE SILHOUETTE MATRIX ONLY
    # Calculate scale factors (1.20 = 20% larger body size)
    scale_factor = 1.20
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    
    # Resize both the green body and its corresponding mask matrix uniformly
    resized_green = cv2.resize(isolated_green, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    resized_mask = cv2.resize(body_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    
    # Crop the enlarged matrices back down to standard camera bounds from the center
    start_x = (new_w - w) // 2
    start_y = (new_h - h) // 2
    
    cropped_green = resized_green[start_y:start_y+h, start_x:start_x+w]
    cropped_mask = resized_mask[start_y:start_y+h, start_x:start_x+w]
    
    # 5. OVERLAY THE ENLARGED GREEN HULK BACK ONTO THE UNWARPED ROOM
    # Use the static background frame as our clean background base
    output_frame = frame.copy() 
    
    # Smooth the edges of the scaled mask to eliminate sharp pixel outlines
    feathered_mask = cv2.GaussianBlur(cropped_mask, (21, 21), 0)
    alpha = feathered_mask[:, :, np.newaxis] / 255.0
    
    # Merge the clean background frame with the scaled, cropped green body
    final_output = (alpha * cropped_green + (1.0 - alpha) * output_frame).astype(np.uint8)
    
    cv2.imshow("Hulk Part 2: Body Enlarger Engine", final_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()