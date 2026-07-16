import cv2
import numpy as np
import random
import math
import time

class CakeGlowEngine:
    def __init__(self):
        # Operational parameters transferred to memory storage scope
        self.state = 0  # 0 = Sliding Up, 1 = Idle/Burning, 2 = Celebration Explosion
        self.cake_y = 600.0       # Start offscreen
        self.target_y = 380.0     # Pushed lower down the screen
        self.slide_speed = 0.1    # Smooth cinematic transition glide up

        # Individual candle configurations: [x_pos, is_alive, flame_flicker]
        self.candles = [[250, True, 0], [320, True, 0], [390, True, 0]]
        self.particles = []
        self.banner_y = -100.0
        self.target_banner_y = 70.0
        
        self.prev_gray = None

    def process_frame(self, frame):
        """
        Main interface entry point targeted by app.py.
        Accepts a standalone frame matrix, applies active filter logic, 
        and returns the modified image output back to the stream layer.
        """
        h, w, c = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Initialize optical flow tracking matrix on the initial frame ingress
        if self.prev_gray is None:
            self.prev_gray = gray.copy()
            
        # --- 1. AESTHETIC COLOR GRADE FILTER ---
        b, g, r = cv2.split(frame)
        r = cv2.addWeighted(r, 0.95, np.zeros_like(r), 0, 10)
        b = cv2.addWeighted(b, 0.85, np.zeros_like(b), 0, -5)
        output_frame = cv2.merge((b, g, r))
        
        # --- 2. SMOOTH SLIDE-IN ANIMATION ---
        if self.state == 0:
            self.cake_y += (self.target_y - self.cake_y) * self.slide_speed
            if abs(self.cake_y - self.target_y) < 1.0:
                self.cake_y = self.target_y
                self.state = 1

        # --- 3. REFINED DIRECTIONAL MOTION (THE BLOW) ---
        if self.state == 1:
            flow = cv2.calcOpticalFlowFarneback(self.prev_gray, gray, None, 0.5, 3, 11, 3, 5, 1.1, 0)
            self.prev_gray = gray.copy()
            
            for candle in self.candles:
                cx_pos = candle[0]
                if candle[1]:  # If candle is burning
                    # Sample local flow area directly above the wick coordinates
                    local_flow = flow[int(self.cake_y-70):int(self.cake_y-20), cx_pos-20:cx_pos+20]
                    mean_u = np.mean(local_flow[..., 0]) 
                    mean_v = np.mean(local_flow[..., 1]) 
                    magnitude = math.sqrt(mean_u**2 + mean_v**2)
                    
                    # Visual tilt response to breathing
                    candle[2] = int(mean_u * 3)
                    
                    if magnitude > 3.5: # Balanced sensitivity
                        candle[1] = False
                        # Generate neat glowing spark eruption
                        for _ in range(25):
                            self.particles.append({
                                'x': float(cx_pos),
                                'y': float(self.cake_y - 45),
                                'vx': random.uniform(-3, 3) + (mean_u * 0.3),
                                'vy': random.uniform(-10, -4),
                                'color': (random.randint(200, 255), random.randint(150, 255), 0),
                                'size': random.randint(3, 6),
                                'life': 1.0
                            })
            
            if not any(c[1] for c in self.candles):
                self.state = 2
        else:
            self.prev_gray = gray.copy()

        # --- 4. RENDER GLASSMORPHIC CAKE ---
        cy = int(self.cake_y)
        cx = w // 2
        
        overlay = output_frame.copy()
        cv2.rectangle(overlay, (cx - 130, cy), (cx + 130, cy + 70), (40, 10, 20), -1)
        cv2.rectangle(overlay, (cx - 90, cy - 45), (cx + 90, cy), (50, 15, 30), -1)
        cv2.addWeighted(overlay, 0.35, output_frame, 0.65, 0, output_frame)
        
        cv2.rectangle(output_frame, (cx - 130, cy), (cx + 130, cy + 70), (255, 0, 180), 2, cv2.LINE_AA) 
        cv2.rectangle(output_frame, (cx - 90, cy - 45), (cx + 90, cy), (255, 230, 0), 2, cv2.LINE_AA)  

        # Render Clean Geometric Candles
        for candle in self.candles:
            wx = candle[0]
            cv2.line(output_frame, (wx, cy - 45), (wx, cy - 60), (240, 240, 240), 2, cv2.LINE_AA) 
            
            if candle[1]: 
                tx = candle[2]
                cv2.circle(output_frame, (wx + tx, cy - 70), 6, (0, 165, 255), -1, cv2.LINE_AA)
                cv2.circle(output_frame, (wx + int(tx*0.5), cy - 68), 3, (0, 255, 255), -1, cv2.LINE_AA)

        # --- 5. ANIMATED CELEBRATION BANNER & CONFETTI ---
        if self.state == 2:
            if self.banner_y < self.target_banner_y:
                self.banner_y += (self.target_banner_y - self.banner_y) * 0.08

            if len(self.particles) < 60:
                self.particles.append({
                    'x': float(random.randint(cx - 120, cx + 120)),
                    'y': float(cy - 20),
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-7, -4),
                    'color': random.choice([(0, 230, 255), (255, 0, 140), (255, 255, 255), (0, 255, 120)]),
                    'size': random.randint(3, 6),
                    'life': 1.0
                })

            bx, by = cx, int(self.banner_y)
            text = "HAPPY BIRTHDAY MOM"
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            t_size = cv2.getTextSize(text, font, 0.9, 2)[0]
            tx = bx - t_size[0] // 2
            
            banner_overlay = output_frame.copy()
            cv2.rectangle(banner_overlay, (tx - 20, by - 35), (tx + t_size[0] + 20, by + 15), (20, 20, 20), -1)
            cv2.addWeighted(banner_overlay, 0.6, output_frame, 0.4, 0, output_frame)
            cv2.rectangle(output_frame, (tx - 20, by - 35), (tx + t_size[0] + 20, by + 15), (0, 230, 255), 1, cv2.LINE_AA)

            pulse = int(abs(math.sin(time.time() * 4)) * 4)
            cv2.putText(output_frame, text, (tx, by), font, 0.9, (255, 0, 140), 2 + pulse, cv2.LINE_AA)
            cv2.putText(output_frame, text, (tx, by), font, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

        # Process and draw particles safely with alpha life decay
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.22 
            p['life'] -= 0.012
            
            if p['life'] <= 0 or p['y'] > h:
                self.particles.remove(p)
                continue
                
            ix, iy = int(p['x']), int(p['y'])
            if 0 <= ix < w and 0 <= iy < h:
                decay_color = tuple([int(c_val * p['life']) for c_val in p['color']])
                cv2.circle(output_frame, (ix, iy), int(p['size'] * p['life']), decay_color, -1, cv2.LINE_AA)

        return output_frame

    def trigger_reset(self):
        self.state = 0
        self.cake_y = 600.0
        self.candles = [[250, True, 0], [320, True, 0], [390, True, 0]]
        self.particles = []
        self.banner_y = -100.0


# ====================================================================
# 6. LOCAL BACKWARD-COMPATIBILITY GUARD
# ====================================================================
if __name__ == "__main__":
    engine = CakeGlowEngine()
    cap = cv2.VideoCapture(0)
    print("=== CLEAN NEON CAKE ENGINE ONLINE ===")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        output = engine.process_frame(frame)
        cv2.imshow("Day 2 Challenge: Glassmorphic Cake Engine", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()