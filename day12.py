import cv2
import numpy as np
import math
import random

def draw_animated_portal(img, center, rx, ry, primary_color, secondary_color, angle=0, frame_count=0):
    """
    Renders a multi-layered, animated vector portal with a swirling core and outer energy ring.
    """
    h, w, _ = img.shape
    cx, cy = center
    overlay = img.copy()

    # --- 1. Inner Void (Dark Hole inside the portal) ---
    num_points = 60
    void_pts = []
    for i in range(num_points):
        theta = (2 * math.pi / num_points) * i
        # Subtle organic wave pulse
        wave = 4 * math.sin(theta * 5 + frame_count * 0.1)
        curr_rx, curr_ry = rx + wave, ry + wave / 2
        
        x = cx + curr_rx * math.cos(theta) * math.cos(angle) - curr_ry * math.sin(theta) * math.sin(angle)
        y = cy + curr_rx * math.cos(theta) * math.sin(angle) + curr_ry * math.sin(theta) * math.cos(angle)
        void_pts.append([int(x), int(y)])
        
    pts_array = np.array(void_pts, np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(overlay, [pts_array], (12, 8, 20))  # Deep void fill

    # --- 2. Swirling Energy Trails (Sub-rings) ---
    for ring_offset in range(3, 0, -1):
        ring_pts = []
        speed_factor = 0.15 * ring_offset
        for i in range(num_points):
            theta = (2 * math.pi / num_points) * i
            wave = (6 * ring_offset) * math.sin(theta * (4 + ring_offset) + frame_count * speed_factor)
            curr_rx = rx + wave + (ring_offset * 6)
            curr_ry = ry + (wave / 2) + (ring_offset * 4)

            x = cx + curr_rx * math.cos(theta) * math.cos(angle) - curr_ry * math.sin(theta) * math.sin(angle)
            y = cy + curr_rx * math.cos(theta) * math.sin(angle) + curr_ry * math.sin(theta) * math.cos(angle)
            ring_pts.append([int(x), int(y)])

        r_pts_array = np.array(ring_pts, np.int32).reshape((-1, 1, 2))
        thickness = max(2, 6 - ring_offset)
        cv2.polylines(overlay, [r_pts_array], isClosed=True, color=secondary_color, thickness=thickness, lineType=cv2.LINE_AA)

    # --- 3. Outer Glowing Ring ---
    cv2.polylines(overlay, [pts_array], isClosed=True, color=primary_color, thickness=12, lineType=cv2.LINE_AA)
    
    # --- 4. Bright White Core Edge ---
    cv2.polylines(overlay, [pts_array], isClosed=True, color=(255, 255, 255), thickness=3, lineType=cv2.LINE_AA)

    # Blend glow layers onto main canvas
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

def create_starfield(w, h, num_stars=100):
    """Generates static random star points for the space background."""
    random.seed(42)  # Fixed seed so stars don't jitter randomly each frame
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        radius = random.choice([1, 1, 2])
        brightness = random.randint(180, 255)
        stars.append((x, y, radius, brightness))
    return stars

def run_portal_studio():
    # Canvas dimensions
    w, h = 1280, 720
    
    # Pre-generate background starfield
    stars = create_starfield(w, h, num_stars=120)

    # Interactive Portal Parameters
    # Portal 1 (Left - Orange/Gold)
    p1_pos = [int(w * 0.3), int(h * 0.5)]
    p1_rx, p1_ry = 90, 140
    p1_angle = math.radians(-15)
    p1_primary = (30, 160, 255)     # Vibrant Orange (BGR)
    p1_secondary = (100, 210, 255)  # Golden Yellow (BGR)

    # Portal 2 (Right - Cyan/Blue)
    p2_pos = [int(w * 0.7), int(h * 0.5)]
    p2_rx, p2_ry = 85, 135
    p2_angle = math.radians(15)
    p2_primary = (255, 200, 50)     # Neon Blue (BGR)
    p2_secondary = (255, 255, 120)  # Bright Cyan (BGR)

    frame_count = 0
    selected_portal = 1

    print("=" * 60)
    print("PORTAL STUDIO CONTROLS:")
    print("  [1] / [2]  : Switch active portal control (Portal 1 vs 2)")
    print("  [W][A][S][D]: Move selected portal position")
    print("  [+] / [-]  : Scale portal size")
    print("  [R]        : Rotate active portal")
    print("  [Q] / [ESC]: Exit application")
    print("=" * 60)

    while True:
        frame_count += 1

        # 1. Base Space Background
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        canvas[:] = (30, 18, 12)  # Deep cosmic purple-blue background

        # Draw stars
        for sx, sy, srad, sbright in stars:
            cv2.circle(canvas, (sx, sy), srad, (sbright, sbright, sbright), -1)

        # 2. Render Portal 1 & Portal 2
        draw_animated_portal(
            canvas, tuple(p1_pos), p1_rx, p1_ry, 
            p1_primary, p1_secondary, angle=p1_angle, frame_count=frame_count
        )
        
        draw_animated_portal(
            canvas, tuple(p2_pos), p2_rx, p2_ry, 
            p2_primary, p2_secondary, angle=p2_angle, frame_count=frame_count
        )

        # 3. On-screen UI Labels
        active_label = f"Active Control: PORTAL {selected_portal}"
        cv2.putText(canvas, active_label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, "PORTAL 1 (ENTRANCE)", (p1_pos[0] - 110, p1_pos[1] - p1_ry - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, p1_primary, 2, cv2.LINE_AA)
        cv2.putText(canvas, "PORTAL 2 (EXIT)", (p2_pos[0] - 80, p2_pos[1] - p2_ry - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, p2_primary, 2, cv2.LINE_AA)

        # Draw selection indicator around active portal center
        active_center = p1_pos if selected_portal == 1 else p2_pos
        cv2.circle(canvas, tuple(active_center), 6, (255, 255, 255), -1, cv2.LINE_AA)

        cv2.imshow("Live Portal Studio", canvas)

        # Key Inputs
        key = cv2.waitKey(16) & 0xFF  # ~60 FPS loop
        if key in (27, ord('q')):
            break
        elif key == ord('1'):
            selected_portal = 1
        elif key == ord('2'):
            selected_portal = 2
        
        # Position Adjustments (WASD)
        elif key == ord('w'):
            if selected_portal == 1: p1_pos[1] -= 8
            else: p2_pos[1] -= 8
        elif key == ord('s'):
            if selected_portal == 1: p1_pos[1] += 8
            else: p2_pos[1] += 8
        elif key == ord('a'):
            if selected_portal == 1: p1_pos[0] -= 8
            else: p2_pos[0] -= 8
        elif key == ord('d'):
            if selected_portal == 1: p1_pos[0] += 8
            else: p2_pos[0] += 8

        # Scale Adjustments (+ / -)
        elif key in (ord('+'), ord('=')):
            if selected_portal == 1: p1_rx += 4; p1_ry += 6
            else: p2_rx += 4; p2_ry += 6
        elif key in (ord('-'), ord('_')):
            if selected_portal == 1: p1_rx = max(20, p1_rx - 4); p1_ry = max(30, p1_ry - 6)
            else: p2_rx = max(20, p2_rx - 4); p2_ry = max(30, p2_ry - 6)

        # Rotation (R)
        elif key == ord('r'):
            if selected_portal == 1: p1_angle += math.radians(10)
            else: p2_angle += math.radians(10)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_portal_studio()