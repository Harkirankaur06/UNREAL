import cv2
import numpy as np

# Initialize Webcam
cap = cv2.VideoCapture(0)

# Buffer configuration (60 frames = approx 2 seconds of history at 30fps)
BUFFER_SIZE = 60
frame_buffer = []

print("=== CHRONO-FRICTION ENGINE ONLINE ===")
print("Stand still for 2 seconds to prime the time-buffer...")
print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1) # Mirror mode for intuitive on-camera movement
    h, w, c = frame.shape
    
    # 1. Maintain the rolling history buffer
    frame_buffer.append(frame.copy())
    if len(frame_buffer) > BUFFER_SIZE:
        frame_buffer.pop(0) # Drop the oldest frame
        
    # If buffer isn't full yet, just display the live stream
    if len(frame_buffer) < BUFFER_SIZE:
        cv2.imshow("Day 2: Chrono-Friction Mirror", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # 2. Generate the spatial distance gradient map
    # We will compute the distance of every pixel relative to the center of the screen
    center_x, center_y = w // 2, h // 2
    
    # Create coordinate matrices
    x_indices, y_indices = np.meshgrid(np.arange(w), np.arange(h))
    
    # Calculate Euclidean distance map from the anchor point
    distance_map = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
    
    # Normalize the distance map strictly between 0 and 1
    max_dist = np.max(distance_map)
    normalized_dist = distance_map / max_dist
    
    # 3. Temporal Map Allocation (Map distance directly to a specific buffer index)
    # Pixels close to center get index 59 (Live). Pixels at edges get index 0 (2 seconds ago).
    time_indices = (normalized_dist * (BUFFER_SIZE - 1)).astype(np.int32)
    # Invert it so center is live time, edges are past time
    time_indices = (BUFFER_SIZE - 1) - time_indices 
    
    # 4. Reconstruct Reality from the 3D Temporal Cube
    # Convert buffer to a highly efficient 4D NumPy array [Time, H, W, C]
    cube = np.stack(frame_buffer, axis=0)
    
    # Use advanced advanced indexing to pull the exact frame layer required for every individual pixel coordinate
    output_frame = cube[time_indices, y_indices, x_indices]

    # Draw a clean, minimal sci-fi crosshair at the center time-anchor point
    cv2.circle(output_frame, (center_x, center_y), 4, (0, 230, 255), -1)
    cv2.circle(output_frame, (center_x, center_y), 15, (0, 230, 255), 1)
    
    cv2.imshow("Day 2: Chrono-Friction Mirror", output_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()