import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import time
import math

class UnrealStudioContinuous:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#0B0B0C")
        
        self.cap = cv2.VideoCapture(0)
        
        # State Control Pipeline
        self.is_calibrated = False
        self.state = 0  # 0: Normal World, 1: Quantum Collapse Active
        
        self.sequence_start_time = 0.0
        self.locked_clean_bg = None  
        
        # Particle System Configuration for the Graphic Portal Storm
        self.portal_particles = []

        # --- VIEWPORT INTERFACE LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // HIGH-VELOCITY HUMAN DISPLACEMENT CORE", 
                               fg="#00FFFF", bg="#0B0B0C", font=("Courier", 12, "bold"))
        self.header.pack(pady=10)
        
        self.canvas = tk.Canvas(window, width=640, height=480, bg="#101012", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        self.btn_frame = tk.Frame(window, bg="#0B0B0C")
        self.btn_frame.pack(pady=15)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#1C1C22', borderwidth=0)
        style.map('TButton', background=[('active', '#00FFFF')], foreground=[('active', '#0B0B0C')])
        
        self.btn_bg = ttk.Button(self.btn_frame, text="1. CACHE ROOM EMPTY", command=self.lock_clean_background)
        self.btn_bg.grid(row=0, column=0, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. TRIGGER BREACH", command=self.start_anomaly_sequence)
        self.btn_hover.grid(row=0, column=1, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET MATRIX", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=2, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // STANDBY. STEP OUT OF CAMERA VIEW AND LOCK ROOM CACHE.")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#8A8A93", bg="#101012", font=("Courier", 9), width=90, anchor="w", padx=12, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.delay = 15
        self.update_stream_loop()
        self.window.mainloop()

    def lock_clean_background(self):
        ret, frame = self.cap.read()
        if ret:
            self.locked_clean_bg = cv2.flip(frame, 1)
            self.is_calibrated = True
            self.status_var.set("CONSOLE // STABLE BACKGROUND MEMORY SECURED.")

    def start_anomaly_sequence(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: MEMORY FRAME CALIBRATION REQUIRED.")
            return
        if self.state == 0:
            self.state = 1
            self.sequence_start_time = time.time()
            self.portal_particles = [] # Fresh particle array spawn
            self.status_var.set("CONSOLE // ATTENTION: ULTRA-GRAVITY SINGULARITY ONLINE.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.state = 0
        self.locked_clean_bg = None
        self.portal_particles = []
        self.status_var.set("CONSOLE // REGISTERS REFURNISHED.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            if self.state == 1:
                elapsed = time.time() - self.sequence_start_time
                p_cx, p_cy = w // 2, h // 2
                
                # High-Precision Motion Segmentation Array (Isolates your human body)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                bg_gray = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
                frame_diff = cv2.absdiff(frame_gray, bg_gray)
                _, motion_mask = cv2.threshold(frame_diff, 24, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
                
                # Rule 6 Guarantee: Base world background is drawn completely clean from cache
                display_frame = self.locked_clean_bg.copy()
                
                # --- GENERATE PORTAL BACKDROP OBJECT OVERLAY LAYER ---
                portal_overlay = display_frame.copy()
                
                # Controls how the portal radius animates (Grows out during Phase 1, decays during Phase 2)
                if elapsed < 1.8:
                    portal_growth = min(1.0, elapsed / 1.2)
                    base_radius = int(150 * portal_growth)
                elif 1.8 <= elapsed < 3.8:
                    collapse_progress = (elapsed - 1.8) / 2.0
                    base_radius = int(150 * max(0.01, 1.0 - collapse_progress))
                else:
                    base_radius = 0

                # Generate the spinning vector storm particles behind your shoulders
                if base_radius > 5 and elapsed < 3.6:
                    # Keep feeding fresh vector energy rings into matrix
                    if len(self.portal_particles) < 120:
                        for _ in range(5):
                            self.portal_particles.append({
                                'angle': random.uniform(0, 2 * math.pi),
                                'dist_factor': random.uniform(0.85, 1.25),
                                'speed': random.uniform(0.08, 0.22),
                                'color': random.choice([(0, 255, 255), (255, 0, 140), (255, 255, 255)]),
                                'size': random.randint(2, 6)
                            })
                    
                    # Update particle paths tracking inward toward singularity center
                    for p in self.portal_particles[:]:
                        p['angle'] += p['speed']
                        p['dist_factor'] -= 0.01
                        
                        if p['dist_factor'] <= 0:
                            self.portal_particles.remove(p)
                            continue
                            
                        curr_r = int(base_radius * p['dist_factor'])
                        px = int(p_cx + curr_r * math.cos(p['angle']))
                        py = int(p_cy + curr_r * 0.75 * math.sin(p['angle'])) # Squashed anamorphic layer depth
                        
                        if 0 <= px < w and 0 <= py < h:
                            cv2.circle(portal_overlay, (px, py), p['size'], p['color'], -1, cv2.LINE_AA)
                    
                    # Layer structured neon geometric core ring bands
                    for ro in range(base_radius, 0, -12):
                        phase_shift = ro * 0.15 - time.time() * 25
                        w_ripple = 1.0 + 0.06 * math.sin(phase_shift)
                        rx = int(ro * w_ripple)
                        ry = int(ro * 0.75 * w_ripple)
                        col = (0, 240, 255) if ro % 24 == 0 else (25, 5, 40)
                        cv2.ellipse(portal_overlay, (p_cx, p_cy), (rx, ry), int(time.time()*150)%360, 0, 360, col, -1, cv2.LINE_AA)
                
                # Stamp the generated graphic portal backdrop into the room cache canvas
                cv2.addWeighted(portal_overlay, 0.85, display_frame, 0.15, 0, display_frame)

                # --- TIMELINE CONTROLLER PROCESSING LAYERS ---

                # --- PHASE 1: JAGGED RGB CHROMATIC SPLIT ON BODY ONLY (0.0s - 1.8s) ---
                if elapsed < 1.8:
                    glitched_body = frame.copy()
                    b_ch, g_ch, r_ch = cv2.split(glitched_body)
                    
                    # Apply manual memory shift channels
                    shift_amt = random.randint(25, 50)
                    r_ch = np.roll(r_ch, -shift_amt, axis=1)
                    b_ch = np.roll(b_ch, shift_amt, axis=1)
                    
                    # Horizontal slicing lines
                    num_slices = random.randint(12, 18)
                    for _ in range(num_slices):
                        sy = random.randint(0, h - 15)
                        sh = random.randint(4, 12)
                        ss = random.randint(-40, 40)
                        r_ch[sy:sy+sh, :] = np.roll(r_ch[sy:sy+sh, :], ss, axis=1)
                    
                    glitched_body = cv2.merge((b_ch, g_ch, r_ch))
                    
                    # Stencil the color-ripped body layer directly on top of the background room and portal
                    display_frame[motion_mask > 0] = glitched_body[motion_mask > 0]
                    self.status_var.set("CONSOLE // PHASE 1: CHROMATIC CHANNEL SHATTER IN PROCESS.")

                # --- PHASE 2: RAPID SPINNING RADIAL INWARD COMPRESSION SLURP (1.8s - 3.8s) ---
                elif 1.8 <= elapsed < 3.8:
                    collapse_progress = (elapsed - 1.8) / 2.0
                    
                    # Establish destination lookup mapping mesh arrays
                    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                    map_x = map_x.astype(np.float32)
                    map_y = map_y.astype(np.float32)
                    
                    dx = map_x - p_cx
                    dy = map_y - p_cy
                    r_mesh = np.sqrt(dx**2 + dy**2)
                    theta_mesh = np.arctan2(dy, dx)
                    
                    # Exponential non-linear acceleration pull factor
                    pull_rate = math.pow(collapse_progress, 3.0) 
                    
                    # Inverse lookup division math forces pixels to suck INWARD to center coordinates
                    r_warped = r_mesh / (1.0 - (pull_rate * np.exp(-r_mesh / 240.0)))
                    # Tight fluid spiral spinning (Multiplied to 6.8 for hyper rotation)
                    theta_warped = theta_mesh - (pull_rate * 6.8 * np.exp(-r_mesh / 110.0))
                    
                    slurp_x = p_cx + r_warped * np.cos(theta_warped)
                    slurp_y = p_cy + r_warped * np.sin(theta_warped)
                    
                    # Split incoming video track to maintain RGB aberration split inside the slurp transformation
                    frame_b, frame_g, frame_r = cv2.split(frame)
                    frame_r = np.roll(frame_r, -25, axis=1)
                    frame_b = np.roll(frame_b, 25, axis=1)
                    glitch_src = cv2.merge((frame_b, frame_g, frame_r))
                    
                    slurped_matrix = cv2.remap(glitch_src, slurp_x, slurp_y, cv2.INTER_LINEAR)
                    
                    # Apply the spinning slurp pixel displacement EXCLUSIVELY onto your human body mask coordinates
                    display_frame[motion_mask > 0] = slurped_matrix[motion_mask > 0]
                    
                    # Blinding flash array at instant of complete compression pop
                    if 3.65 <= elapsed < 3.8:
                        display_frame = cv2.add(display_frame, (255, 255, 255, 0))
                    self.status_var.set("CONSOLE // PHASE 2: MASS COMPRESSION CONVECTIVE DISPLACEMENT.")

                # --- PHASE 3: CALIBRATED RESET BACK TO NORMAL STABLE FEED (3.8s+) ---
                else:
                    display_frame = frame.copy()
                    self.state = 0
                    self.portal_particles = []
                    self.status_var.set("CONSOLE // SEQUENCE MET. SYSTEM SAFELY RE-ANCHORED TO STABLE DIMENSION.")

                cv2.putText(display_frame, f"WARP_FACTOR: {elapsed:.2f}s", (30, h - 30), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "SYS_STATUS // SECURE", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map the finalized pixel matrix to the interface canvas container
            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas.img_tk = img_tk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            
        self.window.after(self.delay, self.update_stream_loop)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    UnrealStudioContinuous(tk.Tk(), "UNREAL Chromatic Breach Engine v8.5")