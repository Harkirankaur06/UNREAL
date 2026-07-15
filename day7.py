import cv2
import numpy as np

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to exit the mirror.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Mirror the camera view
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # --- SKIN DETECTION & DIAMOND GLOW ---
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Pale, cold skin glow effect (applied only over detected skin)
        glow_frame = frame.astype(np.float32)
        glow_frame[:, :, 0] += (skin_mask / 255.0) * 15  # Blue
        glow_frame[:, :, 1] += (skin_mask / 255.0) * 10  # Green
        glow_frame[:, :, 2] += (skin_mask / 255.0) * 15  # Red
        glow_frame = np.clip(glow_frame, 0, 255).astype(np.uint8)

        # --- SPARKLING DIAMOND EFFECT ---
        v_channel = hsv[:, :, 2]
        highlight_mask = cv2.inRange(v_channel, 160, 255) 
        sparkle_zone = cv2.bitwise_and(skin_mask, highlight_mask)

        # Generate sparse sparkling particles
        noise = np.random.rand(h, w)
        sparkle_pixels = (noise > 0.985).astype(np.uint8) * 255
        sparkles = cv2.bitwise_and(sparkle_pixels, sparkle_zone)

        # Cross-shaped kernel to create diamond-like star glints
        sparkle_kernel = np.array([[0,1,0], [1,1,1], [0,1,0]], dtype=np.uint8)
        thick_sparkles = cv2.dilate(sparkles, sparkle_kernel, iterations=1)
        
        # Apply white diamonds onto the glowing frame
        output = glow_frame.copy()
        output[thick_sparkles > 0] = [255, 255, 255]

        # --- VIBRANT LIP BLUSH ---
        # Look for reddish tones in the lower half of the frame where lips usually are
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        lip_mask = cv2.bitwise_or(mask_red1, mask_red2)
        
        # Restrict lip color matching to the lower 60% of the screen to avoid matching eyes/hair
        lip_zone = np.zeros_like(lip_mask)
        lip_zone[int(h*0.4):, :] = lip_mask[int(h*0.4):, :]

        # Tint the lips a richer, vibrant pinkish-red
        output_float = output.astype(np.float32)
        output_float[:, :, 1] -= (lip_zone / 255.0) * 20  # Pull back green to make it punchier
        output_float[:, :, 2] += (lip_zone / 255.0) * 40  # Boost Red
        output = np.clip(output_float, 0, 255).astype(np.uint8)        

        # Render the final mirror window
        cv2.imshow("The Skin of a Killer, Bella", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()