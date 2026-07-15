import cv2
import numpy as np

def generate_animal_iris_texture(size):
    """Generates a dynamic, high-contrast marbled animal iris texture."""
    # Create center-based coordinates
    xx, yy = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
    rho = np.sqrt(xx**2 + yy**2)
    phi = np.arctan2(yy, xx)
    
    # 1. Base vibrant orange-gold layer
    texture = np.zeros((size, size, 3), dtype=np.float32)
    texture[:, :, 0] = 0.0  # Blue
    texture[:, :, 1] = 0.55 # Green/Gold mix
    texture[:, :, 2] = 1.0  # Pure bright Red/Orange
    
    # 2. Add structural animal iris fibers (radial patterns)
    # Using high-frequency sine waves to simulate a predatory eye structure
    fibers = np.sin(phi * 24) * np.cos(rho * 10)
    fibers = (fibers + 1) / 2.0
    
    # 3. Add marbled noise variance
    random_noise = np.random.rand(size, size)
    marbled_pattern = (fibers * 0.6) + (random_noise * 0.4)
    
    # Modulate channels with the texture pattern
    texture[:, :, 1] *= (0.4 + marbled_pattern * 0.6)
    texture[:, :, 2] *= (0.5 + marbled_pattern * 0.5)
    
    # 4. Vignette / Dark outer ring (Limbus ring seen in wild animals)
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

    print("Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # --- SKIN DETECTION & DIAMOND GLOW ---
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        glow_frame = frame.astype(np.float32)
        glow_frame[:, :, 0] += (skin_mask / 255.0) * 15  
        glow_frame[:, :, 1] += (skin_mask / 255.0) * 10  
        glow_frame[:, :, 2] += (skin_mask / 255.0) * 15  
        glow_frame = np.clip(glow_frame, 0, 255).astype(np.uint8)

        # --- SPARKLING DIAMOND EFFECT ---
        v_channel = hsv[:, :, 2]
        highlight_mask = cv2.inRange(v_channel, 160, 255) 
        sparkle_zone = cv2.bitwise_and(skin_mask, highlight_mask)

        noise = np.random.rand(h, w)
        sparkles = cv2.bitwise_and((noise > 0.985).astype(np.uint8) * 255, sparkle_zone)
        thick_sparkles = cv2.dilate(sparkles, np.array([[0,1,0], [1,1,1], [0,1,0]], dtype=np.uint8), iterations=1)
        
        output = glow_frame.copy()
        output[thick_sparkles > 0] = [255, 255, 255]

        # --- VIBRANT LIP BLUSH ---
        lower_red1, upper_red1 = np.array([0, 50, 50]), np.array([10, 255, 255])
        lower_red2, upper_red2 = np.array([170, 50, 50]), np.array([180, 255, 255])
        lip_mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        lip_zone = np.zeros_like(lip_mask)
        lip_zone[int(h*0.4):, :] = lip_mask[int(h*0.4):, :]

        output_float = output.astype(np.float32)
        output_float[:, :, 1] -= (lip_zone / 255.0) * 20  
        output_float[:, :, 2] += (lip_zone / 255.0) * 40  
        output = np.clip(output_float, 0, 255).astype(np.uint8)

        # --- ADAPTIVE ANIMAL IRIS OVERLAY ---
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (fx, fy, fw, fh) in faces:
            roi_gray_face = gray[fy:fy+fh, fx:fx+fw]
            roi_color_face = output[fy:fy+fh, fx:fx+fw]
            
            eyes = eye_cascade.detectMultiScale(roi_gray_face, 1.1, 4)
            for (ex, ey, ew, eh) in eyes:
                if ey > fh * 0.45:  # Skip false tracking points low on face
                    continue
                
                roi_eye_gray = roi_gray_face[ey:ey+eh, ex:ex+ew]
                roi_eye_color = roi_color_face[ey:ey+eh, ex:ex+ew]
                
                # ADAPTIVE CAPTURE: Find the baseline average darkness *inside* this specific eye box
                mean_brightness = np.mean(roi_eye_gray)
                # Set an adaptive cutoff point relative to the local illumination
                adaptive_thresh = min(mean_brightness * 0.65, 75)
                
                _, iris_mask = cv2.threshold(roi_eye_gray, adaptive_thresh, 255, cv2.THRESH_BINARY_INV)
                iris_mask = cv2.morphologyEx(iris_mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
                
                # Exclude frame borders of the box to prevent picking up upper skin shadows/creases
                border = int(ew * 0.15)
                clean_iris_mask = np.zeros_like(iris_mask)
                clean_iris_mask[border:-border, border:-border] = iris_mask[border:-border, border:-border]
                
                # Generate custom high-res textured animal eye tailored to the size of the box
                animal_eye_texture = generate_animal_iris_texture(ew)
                
                # Mask out and map the texture onto the eye
                iris_indices = clean_iris_mask > 0
                if np.any(iris_indices):
                    # Keep a natural small black pupil window right in the center core
                    xx, yy = np.meshgrid(np.linspace(-1, 1, ew), np.linspace(-1, 1, eh))
                    pupil_mask = np.sqrt(xx**2 + yy**2) < 0.18
                    
                    # Apply texture only where iris is detected, skipping the inner pupil center
                    final_iris_pixels = cv2.bitwise_and(clean_iris_mask, cv2.bitwise_not(pupil_mask.astype(np.uint8)*255)) > 0
                    
                    roi_eye_color[final_iris_pixels] = animal_eye_texture[final_iris_pixels]

        cv2.imshow("Skin of a Killer, Bella", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()