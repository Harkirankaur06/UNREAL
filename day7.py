import cv2
import numpy as np

def main():
    # Start the webcam feed
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to exit the Cullen simulator.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Convert to HSV to isolate skin tones more accurately than RGB
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Broad range for human skin tones in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create a skin mask and smooth it out slightly
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)

        # 2. Isolate the highlights (V channel represents brightness)
        v_channel = hsv[:, :, 2]
        # Only sparkle on parts of the skin that are already catching light
        highlight_mask = cv2.inRange(v_channel, 160, 255) 
        sparkle_zone = cv2.bitwise_and(skin_mask, highlight_mask)

        # 3. Pale/Icy skin glow effect (boost brightness slightly where skin is detected)
        glow_frame = frame.astype(np.float32)
        # Add a subtle cold, bright boost to the skin areas
        glow_frame[:, :, 0] += (skin_mask / 255.0) * 15  # Blue channel boost
        glow_frame[:, :, 1] += (skin_mask / 255.0) * 10  # Green channel boost
        glow_frame[:, :, 2] += (skin_mask / 255.0) * 15  # Red channel boost
        glow_frame = np.clip(glow_frame, 0, 255).astype(np.uint8)

        # 4. Generate the dynamic diamond sparkle noise
        # Creating random sparse white pixels that change every single frame
        noise = np.random.rand(*frame.shape[:2])
        # Adjust 0.98 higher (e.g., 0.995) for fewer sparkles, lower for more intensity
        sparkle_pixels = (noise > 0.98).astype(np.uint8) * 255
        
        # Restrict the random sparkles strictly to the bright skin zones
        sparkles = cv2.bitwise_and(sparkle_pixels, sparkle_zone)

        # 5. Blend the sparkles into the glow frame
        # Dilating makes the tiny sparkle points slightly larger and look like "glints"
        sparkle_kernel = np.array([[0,1,0], [1,1,1], [0,1,0]], dtype=np.uint8)
        thick_sparkles = cv2.dilate(sparkles, sparkle_kernel, iterations=1)
        
        # Apply the bright white diamond specs over our glowing video frame
        output = glow_frame.copy()
        output[thick_sparkles > 0] = [255, 255, 255]

        # Display the result
        cv2.imshow("Skin of a Killer", output)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()