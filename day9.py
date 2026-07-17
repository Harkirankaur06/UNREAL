import cv2
import numpy as np

# Load built-in OpenCV Haar Cascades to avoid broken MediaPipe 3.13 dependencies
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# State tracking persistence registers across frame calls
canvas = None
laser_activated = True

# ====================================================================
# STREAMLIT COMPATIBILITY HOOK
# ====================================================================
def process_frame(incoming_frame):
    global canvas, laser_activated
        
    frame = cv2.flip(incoming_frame, 1) 
    h, w, _ = frame.shape
    
    if canvas is None or canvas.shape != frame.shape:
        canvas = np.zeros_like(frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) > 0 and laser_activated:
        # Process the largest detected face
        fx, fy, fw, fh = max(faces, key=lambda rect: rect[2] * rect[3])
        face_roi_gray = gray[fy:fy+fh, fx:fx+fw]
        
        # Detect eyes within the boundaries of the face
        eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))
        
        # We need exactly 2 eyes detected to reliably track and shoot laser vectors
        if len(eyes) >= 2:
            # Sort eyes left-to-right based on their global coordinates
            detected_eyes = []
            for (ex, ey, ew, eh) in eyes:
                eye_center_x = fx + ex + ew // 2
                eye_center_y = fy + ey + eh // 2
                detected_eyes.append((eye_center_x, eye_center_y))
            
            detected_eyes = sorted(detected_eyes, key=lambda p: p[0])[:2]
            (lx, ly), (rx, ry) = detected_eyes[0], detected_eyes[1]

            # Calculate target point on screen where beams converge
            target_x = int((lx + rx) / 2)
            target_y = int((ly + ry) / 2)

            # Etch persistent glowing burn strokes onto the permanent canvas layer
            cv2.circle(canvas, (target_x, target_y), 8, (0, 165, 255), -1)  # Outer Glow (Orange)
            cv2.circle(canvas, (target_x, target_y), 4, (0, 255, 255), -1)  # Core (Yellow)

            # Render the continuous structural laser vectors extending from eyes
            cv2.line(frame, (lx, ly), (target_x, target_y), (0, 0, 255), 4)
            cv2.circle(frame, (lx, ly), 6, (255, 255, 255), -1)
            
            cv2.line(frame, (rx, ry), (target_x, target_y), (0, 0, 255), 4)
            cv2.circle(frame, (rx, ry), 6, (255, 255, 255), -1)

    # Segment and composite canvas drawings cleanly onto live frame
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    
    bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    output_frame = cv2.add(bg, fg)

    cv2.putText(output_frame, "SUPERMAN MODE: Move eyes/head to etch canvas!", (15, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(output_frame, "Press 'r' to wipe the etchings cleanly", (15, 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return output_frame

# Local script fallback window execution guard
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while cap.isOpened():
        success, img_frame = cap.read()
        if not success: break
        output = process_frame(img_frame)
        cv2.imshow("Superman Laser Cam Simulation", output)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('r'):
            if canvas is not None:
                canvas = np.zeros_like(canvas)
    cap.release()
    cv2.destroyAllWindows()