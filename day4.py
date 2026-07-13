import cv2
import numpy as np
import time

# Load OpenCV's structural face tracker
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open live webcam capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Camera warming up... Step completely out of the frame.")

# 1. BACKGROUND CALIBRATION STEP (3-Second Countdown Loop)
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
    cv2.imshow("Hulk Part 3: Robust Expression Trigger Engine", bg_frame)
    cv2.waitKey(1)

# Process master baseline background frame
bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)

print("\nBackground successfully learned! Step into the frame.")
print("Frown, scowl, or tense up your face to trigger the Hulk transformation!")

# Keep track of a moving average baseline for face contrast variance
neutral_variance_baseline = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Isolate the human silhouette using background subtraction
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    
    frame_delta = cv2.absdiff(bg_gray, gray_frame)
    _, body_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel)
    body_mask = cv2.dilate(body_mask, None, iterations=2)
    
    # 2. ROBUST FACIAL CONTRACTION DETECTOR
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    
    is_angry = False
    
    for (x, y, fw, fh) in faces:
        # Extract the exact face pixel bounding box matrix
        face_roi = gray_frame[y:y+fh, x:x+fw]
        
        # Calculate standard deviation/variance of pixel intensity in the face region
        # When you furrow your brows and squint, deep shadow lines create sharp localized texture changes
        _, current_variance = cv2.meanStdDev(face_roi)
        current_var_val = current_variance[0][0]
        
        # Dynamically establish your normal face baseline in the first few active frames
        if neutral_variance_baseline is None:
            neutral_variance_baseline = current_var_val
        else:
            # Smoothly update baseline over time when face is resting
            if current_var_val <= neutral_variance_baseline * 1.05:
                neutral_variance_baseline = 0.95 * neutral_variance_baseline + 0.05 * current_var_val
        
        # TRIGGER MECHANISM: If contrast variance jumps by more than 8% relative to baseline, 
        # it registers the dynamic shadow mask of an intense frown/scowl expression.
        if current_var_val > neutral_variance_baseline * 1.08:
            is_angry = True
            
        # Optional: Draw a subtle indicator box around your face just to confirm tracking is working
        cv2.rectangle(frame, (x, y), (x+fw, y+fh), (255, 255, 255), 1)
        break

    # 3. TRANSFORMATION CONDITION CONTROLLER
    if is_angry:
        # Create the Green Hulk Mutation Matrix
        tint_layer = np.zeros_like(frame)
        tint_layer[:] = [30, 85, 40]  # Dark olive green (BGR)
        green_body = cv2.addWeighted(frame, 0.5, tint_layer, 0.5, 0)
        
        isolated_green = cv2.bitwise_and(green_body, green_body, mask=body_mask)
        
        # Enlarge the silhouette matrix by 20%
        scale_factor = 1.20
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        
        resized_green = cv2.resize(isolated_green, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        resized_mask = cv2.resize(body_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        
        cropped_green = resized_green[start_y:start_y+h, start_x:start_x+w]
        cropped_mask = resized_mask[start_y:start_y+h, start_x:start_x+w]
        
        # Overlay the enlarged green body onto the normal background frame base
        output_frame = frame.copy() 
        feathered_mask = cv2.GaussianBlur(cropped_mask, (21, 21), 0)
        alpha = feathered_mask[:, :, np.newaxis] / 255.0
        
        final_output = (alpha * cropped_green + (1.0 - alpha) * output_frame).astype(np.uint8)
        
        cv2.putText(final_output, "HULK STATE: ACTIVE", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        final_output = frame.copy()
        cv2.putText(final_output, "HULK STATE: CALM", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow("Hulk Part 3: Robust Expression Trigger Engine", final_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()