import cv2

# Load built-in OpenCV Haar Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def process_frame(incoming_frame):
    frame = cv2.flip(incoming_frame, 1) 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) > 0:
        fx, fy, fw, fh = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # Draw face bounding box
        cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (255, 0, 0), 2)
        
        # --- NOSTRIL ELIMINATION FILTER ---
        # Crop only the UPPER HALF of the face region (where eyes actually live)
        upper_face_h = int(fh * 0.55)
        face_roi_gray = gray[fy : fy + upper_face_h, fx : fx + fw]
        
        # Detect eyes strictly within the upper face zone
        eyes = eye_cascade.detectMultiScale(
            face_roi_gray, 
            scaleFactor=1.05, 
            minNeighbors=14,   # Increased value filters out accidental small textures
            minSize=(40, 40)   # Increased minimum size so tiny nostril shadows don't trigger
        )
        
        for (ex, ey, ew, eh) in eyes:
            eye_x = fx + ex
            eye_y = fy + ey
            
            cv2.rectangle(frame, (eye_x, eye_y), (eye_x + ew, eye_y + eh), (0, 255, 0), 2)
            
            center_x = eye_x + ew // 2
            center_y = eye_y + eh // 2
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)

        cv2.putText(frame, f"Detected Eyes Open: {len(eyes)}", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "No Face Detected", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return frame

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while cap.isOpened():
        success, img_frame = cap.read()
        if not success: 
            break
            
        output = process_frame(img_frame)
        cv2.imshow("Filtered Eye Detection", output)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
            
    cap.release()
    cv2.destroyAllWindows()