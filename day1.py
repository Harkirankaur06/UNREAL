import cv2
import numpy as np
import math

cap = cv2.VideoCapture(0)

# Smooth config
box_w, box_h = 160, 140
is_levitating = False
object_texture = None
float_y = 0
angle = 0  # For the rotating particle ring

print("🔮 UNREAL: Day 1 (Aesthetic Render) Active!")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    display_frame = frame.copy()
    key = cv2.waitKey(1) & 0xFF

    # Center target coordinates
    cx = int(w / 2)
    cy = int(h / 3)
    box_x = cx - int(box_w / 2)
    box_y = cy - int(box_h / 2)

    if is_levitating:
        # Smooth ease-out float animation
        float_y -= 4
        current_y = box_y + float_y
        
        if current_y > 10:
            # Render the sharp object cutout
            display_frame[current_y:current_y+box_h, box_x:box_x+box_w] = object_texture
            
            # Aesthetic Overlay: Add a subtle, sleek neon underline bar instead of a box
            cv2.line(display_frame, (box_x, current_y + box_h + 5), (box_x + box_w, current_y + box_h + 5), (255, 255, 0), 2)
            
            # Tiny floating embers rising up behind it
            for i in range(3):
                rx = box_x + int(np.random.randint(0, box_w))
                ry = current_y + box_h + int(np.random.randint(10, 30))
                if ry < h:
                    cv2.circle(display_frame, (rx, ry), 2, (255, 255, 0), -1)
        else:
            is_levitating = False
            float_y = 0
    else:
        # STANDBY: Beautiful rotating ring of elegant points instead of an ugly box
        angle += 0.05
        radius = 90
        num_particles = 8
        
        for i in range(num_particles):
            theta = angle + (i * (2 * math.pi / num_particles))
            px = int(cx + radius * math.cos(theta))
            py = int(cy + radius * math.sin(theta))
            
            # Draw sleek, anti-aliased glowing dots
            cv2.circle(display_frame, (px, py), 4, (255, 255, 0), -1, cv2.LINE_AA)
            cv2.circle(display_frame, (px, py), 2, (255, 255, 255), -1, cv2.LINE_AA)
            
        # Minimalist central targeting brackets
        cv2.drawMarker(display_frame, (cx, cy), (255, 255, 0), cv2.MARKER_CROSS, 20, 1, cv2.LINE_AA)

    # Clean UI text formatting (Fixed Font Attributes)
    cv2.putText(display_frame, "UNREAL // OVERRIDE_MATRIX", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(display_frame, "READY" if not is_levitating else "LEVITATING", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    cv2.imshow("UNREAL - Day 1", display_frame)
    if key == ord(' '):
        object_texture = frame[box_y:box_y+box_h, box_x:box_x+box_w].copy()
        is_levitating = True
        float_y = 0
    elif key == ord('r'):
        is_levitating = False
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()