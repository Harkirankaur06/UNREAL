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
        self.state = 0  # 0: Normal World, 1: Quantum Collapse Loop
        
        self.sequence_start_time = 0.0
        self.total_duration = 5.2  
        self.locked_clean_bg = None  

        # --- VIEWPORT INTERFACE ---
        self.header = tk.Label(window, text="UNREAL // RGB ANOMALY BREAKOUT", 
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
            self.status_var.set("CONSOLE // CRITICAL MATRIX INVERSION DEPLOYED.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.state = 0
        self.locked_clean_bg = None
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
                
                # High-Precision Motion Segmentation Array
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                bg_gray = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
                frame_diff = cv2.absdiff(frame_gray, bg_gray)
                _, motion_mask = cv2.threshold(frame_diff, 24, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
                
                # Rule 6 Guarantee: Room is drawn from the crystal clear cache
                display_frame = self.locked_clean_bg.copy()
                
                # --- PHASE 1: INDEPENDENT RGB CHROMATIC SPLIT MATRIX (0.0s - 2.2s) ---
                if elapsed < 2.2:
                    glitched_body = frame.copy()
                    
                    # Manual memory channel splitting
                    b_ch, g_ch, r_ch = cv2.split(glitched_body)
                    
                    # Apply intense directional channel shearing offsets
                    shift_amt = random.randint(20, 45)
                    r_ch = np.roll(r_ch, -shift_amt, axis=1)
                    b_ch = np.roll(b_ch, shift_amt, axis=1)
                    
                    # Slice lines through the channel maps
                    num_slices = random.randint(10, 16)
                    for _ in range(num_slices):
                        sy = random.randint(0, h - 15)
                        sh = random.randint(4, 12)
                        ss = random.randint(-35, 35)
                        r_ch[sy:sy+sh, :] = np.roll(r_ch[sy:sy+sh, :], ss, axis=1)
                    
                    glitched_body = cv2.merge((b_ch, g_ch, r_ch))
                    
                    # Inject heavy ink textures over your body outlines
                    body_gray = cv2.cvtColor(glitched_body, cv2.COLOR_BGR2GRAY)
                    body_edges = cv2.Canny(body_gray, 40, 130)
                    body_edges = cv2.dilate(body_edges, np.ones((2,2), np.uint8))
                    glitched_body[body_edges > 0] = [255, 0, 130] # Glowing cyan-magenta ink boundaries
                    
                    # Composite strictly onto moving coordinate addresses
                    display_frame[motion_mask > 0] = glitched_body[motion_mask > 0]
                    self.status_var.set("CONSOLE // DISPLACEMENT ACTIVE: CHROMATIC CHANNELS RIPPED.")

                # --- PHASE 2: INTERNAL GRAVITATIONAL RE-MAPPED SLURP (2.2s - 4.5s) ---
                elif 2.2 <= elapsed < 4.5:
                    collapse_progress = (elapsed - 2.2) / 2.3
                    
                    # Render vector void core rings in back-layer empty room
                    portal_overlay = display_frame.copy()
                    p_radius = int(140 * max(0.0, 1.0 - collapse_progress))
                    if p_radius > 4:
                        for ro in range(p_radius, 0, -8):
                            cv2.ellipse(portal_overlay, (p_cx, p_cy), (ro, int(ro*0.75)), 
                                        int(time.time()*-380)%360, 0, 360, (255, 0, 140), -1, cv2.LINE_AA)
                        cv2.addWeighted(portal_overlay, 0.9 * (1.0 - collapse_progress), display_frame, 1.0 - (0.9 * (1.0 - collapse_progress)), 0, display_frame)

                    # Build internal coordinate index lookups
                    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                    map_x = map_x.astype(np.float32)
                    map_y = map_y.astype(np.float32)
                    
                    dx = map_x - p_cx
                    dy = map_y - p_cy
                    r_mesh = np.sqrt(dx**2 + dy**2)
                    theta_mesh = np.arctan2(dy, dx)
                    
                    pull_rate = math.pow(collapse_progress, 2.0)
                    
                    # Fraction reduction pulls pixels INWARD to center point coordinate slots
                    r_warped = r_mesh * (1.0 - (pull_rate * np.exp(-r_mesh / 150.0)))
                    theta_warped = theta_mesh + (pull_rate * 2.5 * np.exp(-r_mesh / 90.0))
                    
                    slurp_x = p_cx + r_warped * np.cos(theta_warped)
                    slurp_y = p_cy + r_warped * np.sin(theta_warped)
                    
                    # Split channels on incoming frame array to maintain RGB glitch while pulling inward
                    frame_b, frame_g, frame_r = cv2.split(frame)
                    frame_r = np.roll(frame_r, -20, axis=1)
                    frame_b = np.roll(frame_b, 20, axis=1)
                    glitch_src = cv2.merge((frame_b, frame_g, frame_r))
                    
                    slurped_matrix = cv2.remap(glitch_src, slurp_x, slurp_y, cv2.INTER_LINEAR)
                    
                    # Blending coordinates strictly limited to body mask channel
                    display_frame[motion_mask > 0] = slurped_matrix[motion_mask > 0]
                    
                    if 4.35 <= elapsed < 4.5:
                        display_frame = cv2.add(display_frame, (255, 255, 255, 0))
                    self.status_var.set("CONSOLE // GRAV_VOID: CONVECTIVE FORCE APPLIED.")

                # --- PHASE 3: SAFE RESTORATION TO RAW STREAM (4.5s+) ---
                else:
                    display_frame = frame.copy()
                    self.state = 0
                    self.status_var.set("CONSOLE // RESTORATION MET. TARGET SEGMENTS SECURED.")

                cv2.putText(display_frame, f"WARP_FACTOR: {elapsed:.2f}s", (30, h - 30), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "SYS_STATUS // SECURE", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map array to interface canvas container
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
    UnrealStudioContinuous(tk.Tk(), "UNREAL Chromatic Breach Engine v6.0")