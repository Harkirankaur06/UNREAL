import cv2
import numpy as np

BUFFER_SIZE = 60
frame_buffer = []

# ====================================================================
# STREAMLIT COMPATIBILITY HOOK (DO NOT TOUCH ORIGINAL LOGIC)
# ====================================================================
def process_frame(incoming_frame):
    global frame_buffer
    
    frame = cv2.flip(incoming_frame, 1) 
    h, w, c = frame.shape
    
    frame_buffer.append(frame.copy())
    if len(frame_buffer) > BUFFER_SIZE:
        frame_buffer.pop(0) 
        
    if len(frame_buffer) < BUFFER_SIZE:
        cv2.putText(frame, "PRIMING TEMPORAL HISTORICAL BUFFER LAYERS...", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 255), 2)
        return frame

    center_x, center_y = w // 2, h // 2
    x_indices, y_indices = np.meshgrid(np.arange(w), np.arange(h))
    
    distance_map = np.sqrt((x_indices - center_x)**2 + (y_indices - center_y)**2)
    max_dist = np.max(distance_map)
    normalized_dist = distance_map / max_dist
    
    time_indices = (normalized_dist * (BUFFER_SIZE - 1)).astype(np.int32)
    time_indices = (BUFFER_SIZE - 1) - time_indices 
    
    cube = np.stack(frame_buffer, axis=0)
    output_frame = cube[time_indices, y_indices, x_indices]

    cv2.circle(output_frame, (center_x, center_y), 4, (0, 230, 255), -1)
    cv2.circle(output_frame, (center_x, center_y), 15, (0, 230, 255), 1)
    
    return output_frame

# Local script fallback window execution guard
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    print("=== CHRONO-FRICTION ENGINE ONLINE ===")
    while True:
        ret, img_frame = cap.read()
        if not ret: break
        output = process_frame(img_frame)
        cv2.imshow("Day 2: Chrono-Friction Mirror", output)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()