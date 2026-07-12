import cv2
import numpy as np

# Open live webcam capture
cap = cv2.VideoCapture(0)

print("Step completely out of the frame for 2 seconds to calibrate the environment background...")
for _ in range(30):
    ret, bg_frame = cap.read()
if not ret:
    print("Camera error.")
    exit()

bg_frame = cv2.flip(bg_frame, 1)
bg_gray = cv2.cvtColor(bg_frame, cv2.COLOR_BGR2GRAY)
bg_gray = cv2.GaussianBlur(bg_gray, (21, 21), 0)

def apply_hulk_body_warp(img, mask):
    """
    Applies a vertical and horizontal expansion vector grid 
    exclusively inside the isolated human body silhouette area.
    """
    h, w = img.shape[:2]
    
    # Generate X and Y coordinate grids
    flex_x, flex_y = np.meshgrid(np.arange(w), np.arange(h))
    flex_x = flex_x.astype(np.float32)
    flex_y = flex_y.astype(np.float32)
    
    # Calculate moments of the body mask to find the center of mass of the torso
    M = cv2.moments(mask)
    if M["m00"] > 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = w // 2, h // 2

    # Calculate spatial distance from the center of body mass
    dx = flex_x - cx
    dy = flex_y - cy
    distance = np.sqrt(dx**2 + dy**2)
    
    # Set the scale of physical body bulking expansion
    radius = max(w, h) // 2
    intensity = 0.45  # Higher values expand the muscle tissue further
    
    # Strictly limit the expansion mapping only to pixels belonging to the body mask
    warp_mask = (distance < radius) & (mask > 0)
    
    if np.any(warp_mask):
        # Push coordinate vectors outward toward the edges of the mask bounds
        factor = 1.0 - (distance / radius) * intensity
        factor = np.clip(factor, 0.2, 1.0)
        
        flex_x[warp_mask] = cx + dx[warp_mask] * factor[warp_mask]
        flex_y[warp_mask] = cy + dy[warp_mask] * factor[warp_mask]
        
    return cv2.remap(img, flex_x, flex_y, cv2.INTER_LINEAR)

print("\nHulk Body Engine initialized. Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # 1. Background Subtraction to grab the strict body silhouette
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    frame_delta = cv2.absdiff(bg_gray, gray_frame)
    _, body_mask = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
    
    # Clean up the silhouette mask using structural closing morph operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel)
    body_mask = cv2.dilate(body_mask, None, iterations=3)
    
    # 2. Generate the Hulk Green Skin Matrix Mutation
    green_mutated = frame.copy()
    # Heavily depress red and blue light channels
    green_mutated[:, :, 0] = cv2.multiply(green_mutated[:, :, 0], 0.1)  # Drop Blue
    green_mutated[:, :, 2] = cv2.multiply(green_mutated[:, :, 2], 0.1)  # Drop Red
    # Over-amplify the green channel for a radioactive hue look
    green_mutated[:, :, 1] = cv2.addWeighted(green_mutated[:, :, 1], 2.5, 0, 0, 15)
    
    # 3. Simulate Clothing Tears
    # Create a procedurally generated noise texture mask to chop lines through the frame
    noise = np.random.randint(0, 255, (h, w), dtype=np.uint8)
    _, tear_strips = cv2.threshold(noise, 240, 255, cv2.THRESH_BINARY)
    tear_strips = cv2.dilate(tear_strips, np.ones((3, 15), np.uint8), iterations=1) # Horizontal tears
    
    # Where tear lines hit the body mask, force pixels black/dark to look like ripped rags
    clothes_tear_mask = cv2.bitwise_and(body_mask, tear_strips)
    green_mutated[clothes_tear_mask > 0] = [15, 15, 15] 

    # Feather the transition edges of the body mask so it doesn't look cut out
    feathered_mask = cv2.GaussianBlur(body_mask, (21, 21), 0)
    alpha = feathered_mask[:, :, np.newaxis] / 255.0
    
    # Apply the green mutation only inside the bounds of the human shape mask
    chroma_frame = (alpha * green_mutated + (1.0 - alpha) * frame).astype(np.uint8)
    
    # 4. Inflate and distort ONLY the body silhouette area
    buff_output = apply_hulk_body_warp(chroma_frame, body_mask)
    
    # Render final output window
    cv2.imshow("Day 4: Procedural Hulk Muscle Engine", buff_output)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()