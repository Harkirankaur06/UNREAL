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
        self.coloring_book_bg = None 
        
        # Particle System Configuration for the Graphic Portal Storm
        self.portal_particles = []

        # --- VIEWPORT INTERFACE LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // MULTIVERSE QUANTUM DISPLACEMENT", 
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
            
            # Procedural Coloring Book Line-Art Filter
            gray_bg = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
            blurred_bg = cv2.medianBlur(gray_bg, 5)
            edges = cv2.adaptiveThreshold(blurred_bg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                          cv2.THRESH_BINARY, 9, 9)
            self.coloring_book_bg = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            self.is_calibrated = True
            self.status_var.set("CONSOLE // ROOM CACHED. DRAWING BOOK ALIGNED.")

    def start_anomaly_sequence(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: CACHE BACKGROUND FIRST.")
            return
        if self.state == 0:
            self.state = 1
            self.sequence_start_time = time.time()
            self.portal_particles = [] 
            self.status_var.set("CONSOLE // ATTENTION: TIMELINE OVERLOAD INITIALIZED.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.state = 0
        self.locked_clean_bg = None
        self.coloring_book_bg = None
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
                
                # Motion Mask Array to track your human body shape bounds
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                bg_gray = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
                frame_diff = cv2.absdiff(frame_gray, bg_gray)
                _, motion_mask = cv2.threshold(frame_diff, 24, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
                
                # --- PHASE 1: COLORING BOOK BG + CHROMATIC BODY SPLIT (0.0s - 1.8s) ---
                if elapsed < 1.8:
                    display_frame = self.coloring_book_bg.copy() # Solid Drawing Book Room
                    
                    glitched_body = frame.copy()
                    b_ch, g_ch, r_ch = cv2.split(glitched_body)
                    
                    shift_amt = random.randint(25, 50)
                    r_ch = np.roll(r_ch, -shift_amt, axis=1)
                    b_ch = np.roll(b_ch, shift_amt, axis=1)
                    
                    num_slices = random.randint(12, 18)
                    for _ in range(num_slices):
                        sy = random.randint(0, h - 15)
                        sh = random.randint(4, 12)
                        ss = random.randint(-40, 40)
                        r_ch[sy:sy+sh, :] = np.roll(r_ch[sy:sy+sh, :], ss, axis=1)
                    
                    glitched_body = cv2.merge((b_ch, g_ch, r_ch))
                    display_frame[motion_mask > 0] = glitched_body[motion_mask > 0]
                    self.status_var.set("CONSOLE // STAGE 1: BODY FRACTURING INSIDE LINE ART.")

                # --- PHASE 2: COLORING BOOK BG + PORTAL STORM + INWARD SHRISK SLURP (1.8s - 3.8s) ---
                elif 1.8 <= elapsed < 3.8:
                    collapse_progress = (elapsed - 1.8) / 2.0
                    display_frame = self.coloring_book_bg.copy()
                    
                    portal_overlay = display_frame.copy()
                    base_radius = int(150 * max(0.01, 1.0 - collapse_progress))
                    
                    if base_radius > 5 and elapsed < 3.6:
                        if len(self.portal_particles) < 120:
                            for _ in range(5):
                                self.portal_particles.append({
                                    'angle': random.uniform(0, 2 * math.pi),
                                    'dist_factor': random.uniform(0.85, 1.25),
                                    'speed': random.uniform(0.08, 0.22),
                                    'color': random.choice([(0, 255, 255), (255, 0, 140), (255, 255, 255)]),
                                    'size': random.randint(2, 6)
                                })
                        
                        for p in self.portal_particles[:]:
                            p['angle'] += p['speed']
                            p['dist_factor'] -= 0.01
                            
                            if p['dist_factor'] <= 0:
                                self.portal_particles.remove(p)
                                continue
                                
                            curr_r = int(base_radius * p['dist_factor'])
                            px = int(p_cx + curr_r * math.cos(p['angle']))
                            py = int(p_cy + curr_r * 0.75 * math.sin(p['angle']))
                            
                            if 0 <= px < w and 0 <= py < h:
                                cv2.circle(portal_overlay, (px, py), p['size'], p['color'], -1, cv2.LINE_AA)
                        
                        for ro in range(base_radius, 0, -12):
                            phase_shift = ro * 0.15 - time.time() * 25
                            w_ripple = 1.0 + 0.06 * math.sin(phase_shift)
                            rx = int(ro * w_ripple)
                            ry = int(ro * 0.75 * w_ripple)
                            col = (0, 240, 255) if ro % 24 == 0 else (25, 5, 40)
                            cv2.ellipse(portal_overlay, (p_cx, p_cy), (rx, ry), int(time.time()*150)%360, 0, 360, col, -1, cv2.LINE_AA)
                    
                    cv2.addWeighted(portal_overlay, 0.85, display_frame, 0.15, 0, display_frame)

                    # --- INWARD COVECTIVE SLURP VECTOR ENGINE ---
                    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                    map_x = map_x.astype(np.float32)
                    map_y = map_y.astype(np.float32)
                    
                    dx = map_x - p_cx
                    dy = map_y - p_cy
                    r_mesh = np.sqrt(dx**2 + dy**2)
                    theta_mesh = np.arctan2(dy, dx)
                    
                    pull_rate = math.pow(collapse_progress, 3.0) 
                    
                    r_warped = r_mesh / (1.0 - (pull_rate * np.exp(-r_mesh / 240.0)))
                    theta_warped = theta_mesh - (pull_rate * 6.8 * np.exp(-r_mesh / 110.0))
                    
                    slurp_x = p_cx + r_warped * np.cos(theta_warped)
                    slurp_y = p_cy + r_warped * np.sin(theta_warped)
                    
                    frame_b, frame_g, frame_r = cv2.split(frame)
                    frame_r = np.roll(frame_r, -25, axis=1)
                    frame_b = np.roll(frame_b, 25, axis=1)
                    glitch_src = cv2.merge((frame_b, frame_g, frame_r))
                    
                    slurped_matrix = cv2.remap(glitch_src, slurp_x, slurp_y, cv2.INTER_LINEAR)
                    display_frame[motion_mask > 0] = slurped_matrix[motion_mask > 0]
                    
                    if 3.65 <= elapsed < 3.8:
                        display_frame = cv2.add(display_frame, (255, 255, 255, 0))
                    self.status_var.set("CONSOLE // STAGE 2: INWARD HIGH-SPEED HUMAN VACUUM SLURP.")

                # --- PHASE 3: THE 1-SECOND VOID DELAY DELIBERATE HOVER (3.8s - 4.8s) ---
                elif 3.8 <= elapsed < 4.8:
                    display_frame = self.coloring_book_bg.copy()
                    if 3.8 <= elapsed < 3.95:
                        display_frame = cv2.add(display_frame, (220, 220, 220, 0))
                    self.status_var.set("CONSOLE // STAGE 3: EVACUATION VERIFIED. SYSTEM COOLDOWN LOOP.")

                # --- PHASE 4: THE RAINBOW PORTAL REVERSE-SPIRAL LANDING (4.8s - 5.6s) ---
                elif 4.8 <= elapsed < 5.6:
                    # Target room snaps completely back to normal
                    display_frame = self.locked_clean_bg.copy()
                    
                    time_in_phase = (elapsed - 4.8) / 0.8
                    invert_progress = 1.0 - time_in_phase
                    
                    # --- REVERSE RADIAL UNWIND MESH MATH ---
                    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                    map_x = map_x.astype(np.float32)
                    map_y = map_y.astype(np.float32)
                    
                    dx = map_x - p_cx
                    dy = map_y - p_cy
                    r_mesh = np.sqrt(dx**2 + dy**2)
                    theta_mesh = np.arctan2(dy, dx)
                    
                    # Reverse pull multiplier drops sharply down to zero
                    reverse_pull = math.pow(invert_progress, 2.5)
                    
                    # Forward scaling mapping matrix forces pixels to transition OUTWARD from the center point
                    r_warped = r_mesh * (1.0 - (reverse_pull * np.exp(-r_mesh / 200.0)))
                    # Rapid untwisting angle factor
                    theta_warped = theta_mesh + (reverse_pull * 7.5 * np.exp(-r_mesh / 120.0))
                    
                    spawn_x = p_cx + r_warped * np.cos(theta_warped)
                    spawn_y = p_cy + r_warped * np.sin(theta_warped)
                    
                    # --- LIQUID PRISM RAINBOW TRANSITION CHANNELS ---
                    fb, fg, fr = cv2.split(frame)
                    rainbow_spread = int(40 * invert_progress)
                    
                    # Offset channels inside the expansion lookup matrix to draw a rainbow burst tail
                    fr = np.roll(fr, -rainbow_spread, axis=1)
                    fb = np.roll(fb, rainbow_spread, axis=1)
                    rainbow_src = cv2.merge((fb, fg, fr))
                    
                    # Remap the colorful frame through the expanding spiral vectors
                    regurgitated_body = cv2.remap(rainbow_src, spawn_x, spawn_y, cv2.INTER_LINEAR)
                    
                    # Render the active spawning portal rings directly under the player footprint
                    portal_radius = int(140 * invert_progress)
                    if portal_radius > 5:
                        for ro in range(portal_radius, 0, -10):
                            cv2.ellipse(display_frame, (p_cx, p_cy), (ro, int(ro*0.75)), 
                                        int(time.time()*-280)%360, 0, 360, (0, 240, 255) if ro % 20 == 0 else (255, 0, 130), -1, cv2.LINE_AA)
                    
                    # Stencil the expanding rainbow body strictly over the room mask canvas
                    display_frame[motion_mask > 0] = regurgitated_body[motion_mask > 0]
                    self.status_var.set("CONSOLE // PHASE 4: REVERSE SPIRAL RE-ENTRY ACTIVE.")

                # --- PHASE 5: STABLE ENVIRONMENT OVERVIEW (5.6s+) ---
                else:
                    display_frame = frame.copy() 
                    self.state = 0
                    self.portal_particles = []
                    self.status_var.set("CONSOLE // STAGE 5: TARGET MULTIVERSE REACHED.")

                cv2.putText(display_frame, f"WARP_TIME: {elapsed:.2f}s", (30, h - 30), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "SYS_STATUS // MATRIX_STABLE", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map array onto Tkinter layout canvas container
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
    UnrealStudioContinuous(tk.Tk(), "UNREAL Quantum Reset Hub v9.6")