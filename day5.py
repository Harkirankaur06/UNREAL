import cv2

# Load the pre-trained Haar Cascades from OpenCV
# Note: These XML files are built directly into the cv2 library
eye_glass_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)

print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Track if glasses are detected in the current frame
    glasses_detected = False

    # 1. Detect faces first to narrow down the search area (improves speed and accuracy)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

    for (x, y, w, h) in faces:
        # Region of Interest (ROI) for the face area
        roi_gray = gray[y:y+h, x:x+w]
        
        # 2. Look for eyes with glasses specifically inside the face region
        glasses = eye_glass_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=3)
        
        if len(glasses) > 0:
            glasses_detected = True
            # Optional: Draw subtle rectangles around the glasses/eyes to show it's working
            for (gx, gy, gw, gh) in glasses:
                cv2.rectangle(frame[y:y+h, x:x+w], (gx, gy), (gx+gw, gy+gh), (0, 255, 0), 2)
            break 

    # 3. Apply conditional logic based on detection
    if not glasses_detected:
        # Active: Apply Thermal Vision
        display_frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        cv2.putText(display_frame, "GLASSES DETECTED: THERMAL MODE", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    else:
        # Passive: Keep normal feed
        display_frame = frame
        cv2.putText(display_frame, "NORMAL MODE", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Day 5: Smart Thermal Toggle', display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()