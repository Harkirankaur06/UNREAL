import cv2
import numpy as np

def generate_animal_iris_texture(size):
    """Generates a dynamic, high-contrast marbled animal iris texture."""
    xx, yy = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
    rho = np.sqrt(xx**2 + yy**2)
    phi = np.arctan2(yy, xx)
    
    texture = np.zeros((size, size, 3), dtype=np.float32)
    texture[:, :, 0] = 0.0  
    texture[:, :, 1] = 0.55 
    texture[:, :, 2] = 1.0  
    
    fibers = np.sin(phi * 24) * np.cos(rho * 10)
    fibers = (fibers + 1) / 2.0
    
    marbled_pattern = (fibers * 0.6) + (np.random.rand(size, size) * 0.4)
    texture[:, :, 1] *= (0.4 + marbled_pattern * 0.6)
    texture[:, :, 2] *= (0.5 + marbled_pattern * 0.5)
    
    limbus_mask = 1.0 - np.clip((rho - 0.45) * 2.5, 0, 1)
    texture *= limbus_mask[:, :, np.newaxis]
    
    return np.clip(texture * 255, 0, 255).astype(np.uint8)

def main():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    if face_cascade.empty() or eye_cascade.empty():
        print("Error: Could not load cascade XML files.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # --- SUNLIGHT TRIGGER CONFIGURATION ---
    SUNLIGHT_THRESHOLD = 125

    print("Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        v_channel = hsv[:, :, 2]
        
        # --- STRICT SKIN DETECTION ---
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([20, 180, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
        # Calculate skin brightness
        skin_pixels = v_channel[skin_mask > 0]
        current_skin_brightness = np.mean(skin_pixels) if skin_pixels.size > 0 else 0

        is_sunlight_triggered = current_skin_brightness > SUNLIGHT_THRESHOLD

        output = frame.copy()

        # --- ALL EFFECTS ARE LOCKED BEHIND THE SUNLIGHT TRIGGER ---
        if is_sunlight_triggered:
            # 1. Pale Skin Glow (Only active in sunlight)
            glow_frame = frame.astype(np.float32)
            glow_frame[:, :, 0] += (skin_mask / 255.0) * 15  
            glow_frame[:, :, 1] += (skin_mask / 255.0) * 10  
            glow_frame[:, :, 2] += (skin_mask / 255.0) * 15  
            output = np.clip(glow_frame, 0, 255).astype(np.uint8)

            # 2. Sparkling Diamonds (Only active in sunlight)
            highlight_mask = cv2.inRange(v_channel, 170, 255)
            sparkle_zone = cv2.bitwise_and(skin_mask, highlight_mask)

            noise = np.random.rand(h, w)
            sparkle_pixels = (noise > 0.985).astype(np.uint8) * 255
            sparkles = cv2.bitwise_and(sparkle_pixels, sparkle_zone)
            
            sparkle_kernel = np.array([[0,1,0], [1,1,1], [0,1,0]], dtype=np.uint8)
            thick_sparkles = cv2.dilate(sparkles, sparkle_kernel, iterations=1)
            
            final_skin_sparkles = cv2.bitwise_and(thick_sparkles, skin_mask)
            output[final_skin_sparkles > 0] = [255, 255, 255]

            # 3. Fiery Animal Iris Overlay (Only calculated and drawn in sunlight)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (fx, fy, fw, fh) in faces:
                roi_gray_face = gray[fy:fy+fh, fx:fx+fw]
                roi_color_face = output[fy:fy+fh, fx:fx+fw]
                
                eyes = eye_cascade.detectMultiScale(roi_gray_face, 1.1, 4)
                for (ex, ey, ew, eh) in eyes:
                    if ey > fh * 0.45:  
                        continue
                    
                    roi_eye_gray = roi_gray_face[ey:ey+eh, ex:ex+ew]
                    roi_eye_color = roi_color_face[ey:ey+eh, ex:ex+ew]
                    
                    mean_brightness = np.mean(roi_eye_gray)
                    adaptive_thresh = min(mean_brightness * 0.65, 75)
                    
                    _, iris_mask = cv2.threshold(roi_eye_gray, adaptive_thresh, 255, cv2.THRESH_BINARY_INV)
                    iris_mask = cv2.morphologyEx(iris_mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
                    
                    border = int(ew * 0.15)
                    clean_iris_mask = np.zeros_like(iris_mask)
                    clean_iris_mask[border:-border, border:-border] = iris_mask[border:-border, border:-border]
                    
                    animal_eye_texture = generate_animal_iris_texture(ew)
                    
                    iris_indices = clean_iris_mask > 0
                    if np.any(iris_indices):
                        xx, yy = np.meshgrid(np.linspace(-1, 1, ew), np.linspace(-1, 1, eh))
                        pupil_mask = np.sqrt(xx**2 + yy**2) < 0.18
                        final_iris_pixels = cv2.bitwise_and(clean_iris_mask, cv2.bitwise_not(pupil_mask.astype(np.uint8)*255)) > 0
                        
                        roi_eye_color[final_iris_pixels] = animal_eye_texture[final_iris_pixels]

        # --- VIBRANT LIP BLUSH ---
        lower_red1, upper_red1 = np.array([0, 50, 50]), np.array([10, 255, 255])
        lower_red2, upper_red2 = np.array([170, 50, 50]), np.array([180, 255, 255])
        lip_mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        lip_zone = np.zeros_like(lip_mask)
        lip_zone[int(h*0.4):, :] = lip_mask[int(h*0.4):, :]

        output_float = output.astype(np.float32)
        output_float[:, :, 1] -= (lip_zone / 255.0) * 20  
        output_float[:, :, 2] += (lip_zone / 255.0) * (40 if is_sunlight_triggered else 15)  
        output = np.clip(output_float, 0, 255).astype(np.uint8)

        # --- HUD METER FOR REAL-TIME CALIBRATION ---
        status_text = f"Sunlight Level: {int(current_skin_brightness)} / {SUNLIGHT_THRESHOLD}"
        color = (0, 255, 0) if is_sunlight_triggered else (0, 0, 255)
        mode_text = "MODE: Diamond Skin" if is_sunlight_triggered else "MODE: Human Disguise"
        
        cv2.putText(output, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(output, mode_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("The Skin of a Killer, Bella", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()