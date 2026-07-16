import cv2
import numpy as np
import time

# Load OpenCV's structural face tracker
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Keep track of a moving average baseline for face contrast variance
neutral_variance_baseline = None
start_time = None
bg_gray = None

# ====================================================================
# STREAMLIT COMPATIBILITY HOOK (DO NOT TOUCH ORIGINAL LOGIC)
# ====================================================================
def process_frame(incoming_frame):
    global neutral_variance_baseline, start_time, bg_gray
    
    frame = cv2.flip(incoming_frame, 1)
    h, w, c = frame.shape
    
    # 1. BACKGROUND CALIBRATION STEP (Non-blocking 3-second capture mapping)
    if start_time is None:
        start_time = time.time()
        
    if time.time() - start_time < 3.0:
        bg_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)
        cv2.putText(frame, "LEARNING BACKGROUND... STAY OUT OF FRAME", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

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
        face_roi = gray_frame[y:y+fh, x:x+fw]
        _, current_variance = cv2.meanStdDev(face_roi)
        current_var_val = current_variance[0][0]
        
        if neutral_variance_baseline is None:
            neutral_variance_baseline = current_var_val
        else:
            if current_var_val <= neutral_variance_baseline * 1.05:
                neutral_variance_baseline = 0.95 * neutral_variance_baseline + 0.05 * current_var_val
        
        if current_var_val > neutral_variance_baseline * 1.08:
            is_angry = True
            
        cv2.rectangle(frame, (x, y), (x+fw, y+fh), (255, 255, 255), 1)
        break

    # 3. TRANSFORMATION CONDITION CONTROLLER
    if is_angry:
        tint_layer = np.zeros_like(frame)
        tint_layer[:] = [30, 85, 40]  # Dark olive green (BGR)
        green_body = cv2.addWeighted(frame, 0.5, tint_layer, 0.5, 0)
        
        isolated_green = cv2.bitwise_and(green_body, green_body, mask=body_mask)
        
        scale_factor = 1.20
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        
        resized_green = cv2.resize(isolated_green, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        resized_mask = cv2.resize(body_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        
        cropped_green = resized_green[start_y:start_y+h, start_x:start_x+w]
        cropped_mask = resized_mask[start_y:start_y+h, start_x:start_x+w]
        
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

    return final_output

# Local script fallback window execution guard
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("Camera warming up... Step completely out of the frame.")
    while cap.isOpened():
        ret, img_frame = cap.read()
        if not ret: break
        output = process_frame(img_frame)
        cv2.imshow("Day 4 Local Test Window", output)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()