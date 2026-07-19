import cv2
import numpy as np
from ultralytics import YOLO
import random
import math

# Load the lightning-fast YOLOv8 Pose estimation AI model
pose_model = YOLO('yolov8n-pose.pt')

cap = cv2.VideoCapture(0)

# Running frame tracking for movement delta
prev_frame = None
chaos_particles = []
time_clock = 0.0

# AI Spell Triggers
spell_active = False
hex_blast_radius = 0.0  # Expands outward across the screen upon trigger release

print("🔮 AI Hex Trigger Online. Cross your wrists over your chest to cast! Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    time_clock += 0.5
    
    # 1. RUN AI SKELETAL POSE TRACKING
    pose_results = pose_model(frame, verbose=False)
    
    # Reset tracking flags unless sustained by AI detection
    ai_triggered = False
    blast_center = (w // 2, h // 2)
    
    if pose_results[0].keypoints is not None and len(pose_results[0].keypoints.data) > 0:
        # Keypoints: 5=L_Shoulder, 6=R_Shoulder, 9=L_Wrist, 10=R_Wrist
        kp = pose_results[0].keypoints.data[0].cpu().numpy()
        
        if len(kp) > 10:
            # Extract absolute coordinates and tracking confidence scores
            l_shldr, r_shldr = kp[5][:2], kp[6][:2]
            l_wrist, r_wrist = kp[9][:2], kp[10][:2]
            conf = [kp[5][2], kp[6][2], kp[9][2], kp[10][2]]
            
            # Ensure the AI has a high confidence lock on all 4 control points
            if all(c > 0.55 for c in conf):
                # AI Geometric Calculation: Check if wrists have crossed the midline axis
                if l_wrist[0] > r_shldr[0] and r_wrist[0] < l_shldr[0]:
                    # Check vertical proximity to confirm they are crossed near chest level
                    wrist_distance = math.hypot(l_wrist[0] - r_wrist[0], l_wrist[1] - r_wrist[1])
                    if wrist_distance < 80:
                        ai_triggered = True
                        spell_active = True
                        # Anchor the explosion origin point right between your crossed hands
                        blast_center = (int((l_wrist[0] + r_wrist[0]) / 2), int((l_wrist[1] + r_wrist[1]) / 2))

    # Handle the expanding shockwave progression upon activation
    if spell_active:
        if ai_triggered:
            # Charge state: Keep the explosion primed at the hands
            hex_blast_radius = 30.0
        else:
            # Release state: The shockwave violently explodes outward across the screen
            hex_blast_radius += 35.0
            if hex_blast_radius > max(h, w) * 1.5:
                spell_active = False
                hex_blast_radius = 0.0

    # 2. OPTIMIZED MOVEMENT DETECTION
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    if prev_frame is None:
        prev_frame = gray_frame
        continue
    frame_delta = cv2.absdiff(prev_frame, gray_frame)
    _, motion_mask = cv2.threshold(frame_delta, 22, 255, cv2.THRESH_BINARY)
    motion_mask = cv2.dilate(motion_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)), iterations=2)
    motion_mask_blur = cv2.GaussianBlur(motion_mask, (15, 15), 0)
    prev_frame = gray_frame

    # 3. ADVANCED FLUID COMPOSITING SHADER
    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = map_x.astype(np.float32)
    map_y = map_y.astype(np.float32)
    
    # Dynamic Math Vector: Calculate displacement offsets for every single pixel
    dx_mat = map_x - blast_center[0]
    dy_mat = map_y - blast_center[1]
    dist_mat = np.sqrt(dx_mat**2 + dy_mat**2) + 0.1
    
    # Default structural wave mapping (Standard live movement trailing)
    fluid_x = np.sin(map_y / 15.0 + time_clock) * np.cos(map_x / 30.0) * 16.0
    fluid_y = np.cos(map_x / 15.0 + time_clock) * np.sin(map_y / 30.0) * 16.0
    intensity = motion_mask_blur / 255.0
    
    # CRITICAL WARP OVERRIDE: Inject massive shockwave distortion if the Hex Blast is rolling out
    if spell_active:
        # Create a concentrated wave ring expanding outwards
        wave_front = np.exp(-((dist_mat - hex_blast_radius) ** 2) / 1600.0)
        # Pull or push pixels along the radial blast trajectory
        fluid_x += (dx_mat / dist_mat) * wave_front * 70.0
        fluid_y += (dy_mat / dist_mat) * wave_front * 70.0
        intensity = np.clip(intensity + wave_front, 0.0, 1.0)
        
    map_x += fluid_x * intensity
    map_y += fluid_y * intensity
    output_frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)

    # 4. CHROMATIC HEX LAYER MERGE
    b, g, r_ch = cv2.split(output_frame)
    r_boost = cv2.add(r_ch, (intensity * 110).astype(np.uint8))
    g_dim = cv2.subtract(g, (intensity * 60).astype(np.uint8))
    b_dim = cv2.subtract(b, (intensity * 30).astype(np.uint8))
    output_frame = cv2.merge([b_dim, g_dim, r_boost])

    # 5. DYNAMIC PARTICLE SPAWNER
    # Spawn continuous trails on motion or a massive ring burst on blast
    if spell_active and not ai_triggered:
        # Generate ring explosion particles along the expanding shockwave front
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            p_dist = hex_blast_radius + random.uniform(-10, 10)
            px = blast_center[0] + math.cos(angle) * p_dist
            py = blast_center[1] + math.sin(angle) * p_dist
            if 0 <= px < w and 0 <= py < h and len(chaos_particles) < 500:
                chaos_particles.append({
                    'x': float(px), 'y': float(py),
                    'vx': math.cos(angle) * random.uniform(2, 5),
                    'vy': math.sin(angle) * random.uniform(2, 5) - 1.0,
                    'life': random.randint(20, 35),
                    'radius': random.randint(4, 12)
                })

    # Standard engine particle emitter loop
    motion_pts = np.argwhere(motion_mask > 0)
    if len(motion_pts) > 0 and len(chaos_particles) < 300:
        sample_size = min(len(motion_pts), 6)
        for idx in random.sample(range(len(motion_pts)), sample_size):
            y, x = motion_pts[idx]
            chaos_particles.append({
                'x': float(x), 'y': float(y),
                'vx': random.uniform(-3.0, 3.0), 'vy': random.uniform(-5.0, -1.0),
                'life': random.randint(15, 25), 'radius': random.randint(3, 8)
            })

    # Draw and update particles
    for p in chaos_particles[:]:
        p['vx'] += math.sin(p['y'] / 12.0 + time_clock) * 0.4
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 1
        if 0 <= p['x'] < w and 0 <= p['y'] < h and p['life'] > 0:
            alpha = p['life'] / 35.0
            overlay = output_frame.copy()
            cv2.circle(overlay, (int(p['x']), int(p['y'])), p['radius'], (int(30*alpha), int(5*alpha), int(245*alpha)), -1)
            cv2.addWeighted(overlay, 0.5 * alpha, output_frame, 1.0 - (0.5 * alpha), 0, output_frame)
        else:
            chaos_particles.remove(p)

    # UI Banner Notification
    if ai_triggered:
        cv2.putText(output_frame, "AI SPELL LOCK: CHARGING HEX CORE...", (30, 50), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
    
    cv2.imshow("Wanda's Chaos Core (AI Triggered)", output_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()