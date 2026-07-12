import cv2
import numpy as np

# Open live webcam capture
cap = cv2.VideoCapture(0)

# Calibrate initial frame briefly
for _ in range(20):
    ret, frame = cap.read()
if not ret:
    print("Camera error.")
    exit()

def apply_hulk_body_warp(img, mask):
    """Expands coordinates outward strictly inside the isolated body mask bounds."""
    h, w = img.shape[:2]
    flex_x, flex_y = np.meshgrid(np.arange(w), np.arange(h))
    flex_x = flex_x.astype(np.float32)
    flex_y = flex_y.astype(np.float32)
    
    # Calculate center of mass of the human silhouette
    M = cv2.moments(mask)
    if M["m00"] > 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = w // 2, h // 2

    dx = flex_x - cx
    dy = flex_y - cy
    distance = np.sqrt(dx**2 + dy**2)
    
    # Muscle bulking variables
    radius = max(w, h) // 2.2
    intensity = 0.4  # Pushes the body silhouette outward
    
    warp_mask = (distance < radius) & (mask > 0)
    
    if np.any(warp_mask):
        factor = 1.0 - (distance / radius) * intensity
        factor = np.clip(factor, 0.4, 1.0)
        
        flex_x[warp_mask] = cx + dx[warp_mask] * factor[warp_mask]
        flex_y[warp_mask] = cy + dy[warp_mask] * factor[warp_mask]
        
    return cv2.remap(img, flex_x, flex_y, cv2.INTER_LINEAR)

print("\nCinematic Hulk Engine Active. Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # 1. Target Human Detection (Using HSV to isolate skin and nearby tones cleanly)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Broadened skin hue detection range that filters out blue wall background textures
    lower_human = np.array([0, 15, 30], dtype=np.uint8)
    upper_human = np.array([25, 170, 255], dtype=np.uint8)
    body_mask = cv2.inRange(hsv, lower_human, upper_human)
    
    # Clean up small holes in the body mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel)
    body_mask = cv2.dilate(body_mask, None, iterations=2)
    
    # 2. Generate Cinematic Hulk Green Skin Matrix Mutation
    green_mutated = frame.copy()
    green_mutated[:, :, 0] = cv2.multiply(green_mutated[:, :, 0], 0.1)  # Drop Blue
    green_mutated[:, :, 2] = cv2.multiply(green_mutated[:, :, 2], 0.1)  # Drop Red
    green_mutated[:, :, 1] = cv2.addWeighted(green_mutated[:, :, 1], 2.2, 0, 0, 20)  # Boost Green
    
    # 3. Controlled Clothing Tears (No more fullscreen static)
    # Create distinct horizontal shred patterns that only occur on the body silhouette
    tear_mask = np.zeros((h, w), dtype=np.uint8)
    # Generate jagged lines relative to frame height
    for i in range(int(h * 0.4), int(h * 0.9), 45):  
        # Draw explicit horizontal rip gashes across the center torso region
        cv2.line(tear_mask, (int(w * 0.25), i), (int(w * 0.75), i + 10), 255, 12)
        cv2.line(tear_mask, (int(w * 0.3), i + 15), (int(w * 0.7), i + 22), 255, 6)

    # Intersect shred gashes strictly over your silhouette
    active_tears = cv2.bitwise_and(body_mask, tear_mask)
    
    # Force the ripped areas to black (simulating shredded fabric edges)
    green_mutated[active_tears > 0] = [10, 10, 10]
    
    # Smooth the transformation transition edges
    feathered_mask = cv2.GaussianBlur(body_mask, (31, 31), 0)
    alpha = feathered_mask[:, :, np.newaxis] / 255.0
    
    # Apply green skin morphing strictly to your body
    chroma_frame = (alpha * green_mutated + (1.0 - alpha) * frame).astype(np.uint8)
    
    # 4. Bulk and distort ONLY your silhouette area
    buff_output = apply_hulk_body_warp(chroma_frame, body_mask)
    
    # Render Window Display
    cv2.imshow("Day 4: Calibrated Hulk Muscle Engine", buff_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()