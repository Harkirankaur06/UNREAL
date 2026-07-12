import cv2
import numpy as np
import time

# Load OpenCV's built-in structural face and eye feature trackers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

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
    cv2.imshow("Hulk Part 3: Expression Trigger Engine", bg_frame)
    cv2.waitKey(1)

# Process master baseline background frame
bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)

print("\nBackground successfully learned! Step into the frame.")
print("Frown/Scowl at the camera to trigger the Hulk transformation!")

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
    
    # 2. ANGER DETECTION ENGINE (Track Eyebrow/Eye Compression)
    # Detect the face box coordinates first
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    
    is_angry = False
    
    for (x, y, fw, fh) in faces:
        # Isolate the upper half of the face where the eyes and brows reside
        upper_face_y = y + int(fh * 0.15)
        upper_face_h = int(fh * 0.45)
        face_roi_gray = gray_frame[upper_face_y:upper_face_y+upper_face_h, x:x+fw]
        
        # Detect eyes within the upper face zone
        eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=4, minSize=(15, 15))
        
        # If eyes are found, track their vertical position relative to the top of the brow region
        if len(eyes) >= 2:
            # Calculate the average Y position of both eyes inside the face region
            avg_eye_y = sum([ey + (eh // 2) for (ex, ey, ew, eh) in eyes]) / len(eyes)
            
            # The closer the eyes look to the top bounding box of the face, the more the brow is furrowed.
            # A lower normalized distance indicates an angry scowl.
            ang_ratio = avg_eye_y / fh
            
            # Threshold calibration: standard neutral is ~0.35+. Lower numbers = deep frown.
            if ang_ratio < 0.28:
                is_angry = True
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
        
        # Add a visual warning status effect on screen
        cv2.putText(final_output, "HULK STATE: ACTIVE", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        # If your face is relaxed, show the standard human video stream with no transformations
        final_output = frame.copy()
        cv2.putText(final_output, "HULK STATE: CALM", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow("Hulk Part 3: Expression Trigger Engine", final_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()