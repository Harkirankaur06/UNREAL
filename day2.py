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
        
        # Core State Variables
        self.is_calibrated = False
        self.state = 0  # 0: Normal, 1: Anomaly Active
        
        # Timeline Parameters
        self.sequence_start_time = 0.0
        self.total_duration = 5.0  
        self.locked_clean_bg = None  

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // SPIDER-VERSE HUMAN PORTAL DISPLACEMENT - DAY 2", 
                               fg="#FF007F", bg="#0B0B0C", font=("Courier", 12, "bold"))
        self.header.pack(pady=10)
        
        self.canvas = tk.Canvas(window, width=640, height=480, bg="#101012", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        self.btn_frame = tk.Frame(window, bg="#0B0B0C")
        self.btn_frame.pack(pady=15)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#1C1C22', borderwidth=0)
        style.map('TButton', background=[('active', '#FF007F')], foreground=[('active', '#0B0B0C')])
        
        self.btn_bg = ttk.Button(self.btn_frame, text="1. LOCK ROOM CACHE", command=self.lock_clean_background)
        self.btn_bg.grid(row=0, column=0, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. INITIATE ANOMALY", command=self.start_anomaly_sequence)
        self.btn_hover.grid(row=0, column=1, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET WORKSPACE", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=2, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // STANDBY. STEP OUT OF FRAME AND CACHE BACKGROUND.")
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
            self.status_var.set("CONSOLE // BACKGROUND GEOMETRY CACHED. SYSTEM ARMED.")

    def start_anomaly_sequence(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: CACHE BACKGROUND BEFORE EXECUTION.")
            return
        if self.state == 0:
            self.state = 1
            self.sequence_start_time = time.time()
            self.status_var.set("CONSOLE // BREACH TRIGGERED. UNSTABLE MULTIVERSE SYNCING.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.state = 0
        self.locked_clean_bg = None
        self.status_var.set("CONSOLE // MEMORY REFRESHED. READY.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            if self.state == 1:
                elapsed = time.time() - self.sequence_start_time
                p_cx, p_cy = w // 2, h // 2
                
                # Dynamic Segment Tracking (Isolates your human body coordinates from the room)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                bg_gray = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
                frame_diff = cv2.absdiff(frame_gray, bg_gray)
                _, motion_mask = cv2.threshold(frame_diff, 20, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
                inv_motion_mask = cv2.bitwise_not(motion_mask)
                
                # --- PURE 2D CARTOON BACKGROUND GENERATOR ---
                # Flatten background textures while preserving clean boundaries
                bg_cartoon = cv2.bilateralFilter(self.locked_clean_bg, 10, 75, 75)
                bg_gray_lines = cv2.cvtColor(bg_cartoon, cv2.COLOR_BGR2GRAY)
                bg_blur = cv2.medianBlur(bg_gray_lines, 5)
                bg_edges = cv2.Laplacian(bg_blur, cv2.CV_8U, ksize=5)
                _, bg_edge_mask = cv2.threshold(bg_edges, 70, 255, cv2.THRESH_BINARY_INV)
                # Apply cartoon outlines strictly to the empty room template
                bg_cartoon = cv2.bitwise_and(bg_cartoon, bg_cartoon, mask=bg_edge_mask)

                # --- TIMELINE RENDER SEPARATION ---
                
                # STAGE 1: CARTOON ROOM + RAW ORIGINAL LIVE HUMAN BODY (0.0s - 1.8s)
                if elapsed < 1.8:
                    display_frame = frame.copy() # Clear, un-tinted original body layer
                    display_frame[inv_motion_mask > 0] = bg_cartoon[inv_motion_mask > 0] # Cartoon room only
                    self.status_var.set("CONSOLE // PHASE 1: BACKGROUND CARTOONIZED. HUMAN LAYOUT NORMAL.")

                # STAGE 2: CARTOON ROOM + LOCAL BODY GLITCH & COLOR TINT (1.8s - 3.4s)
                elif 1.8 <= elapsed < 3.4:
                    glitched_body = frame.copy()
                    
                    # Local Horizontal Shearing + High-Contrast Color Tinting ON HUMAN BODY ONLY
                    num_slices = random.randint(14, 22)
                    for _ in range(num_slices):
                        slice_y = random.randint(0, h - 20)
                        slice_h = random.randint(5, 16)
                        slice_shift = random.randint(-45, 45)
                        glitched_body[slice_y:slice_y+slice_h, :] = np.roll(
                            glitched_body[slice_y:slice_y+slice_h, :], slice_shift, axis=1
                        )
                    # Custom neon-electric stylized tint overlay over body pixels
                    glitched_body[:, :, 2] = cv2.add(glitched_body[:, :, 2], 65) # Red/Magenta Channel Boost
                    glitched_body[:, :, 0] = cv2.add(glitched_body[:, :, 0], 35) # Blue/Purple Channel Boost
                    
                    # Procedural Portal Animation Layer drawn behind the user's mask space
                    portal_base = bg_cartoon.copy()
                    portal_radius = int(140 * min(1.0, (elapsed - 1.8) / 1.0))
                    if portal_radius > 5:
                        for r_offset in range(portal_radius, 0, -10):
                            phase = r_offset * 0.12 - time.time() * 25
                            wave = 1.0 + 0.1 * math.sin(phase)
                            col = (0, 235, 255) if r_offset % 20 == 0 else (30, 5, 45)
                            cv2.ellipse(portal_base, (p_cx, p_cy), (int(r_offset*wave), int(r_offset*0.75*wave)), 
                                        int(time.time()*140)%360, 0, 360, col, -1, cv2.LINE_AA)
                        cv2.addWeighted(portal_base, 0.85, bg_cartoon, 0.15, 0, bg_cartoon)
                    
                    # Compile Layer Mask Composition (Room stays cartoon, body glitches/tints)
                    display_frame = bg_cartoon.copy()
                    display_frame[motion_mask > 0] = glitched_body[motion_mask > 0]
                    self.status_var.set("CONSOLE // PHASE 2: HUMAN CORE INSTABILITY ACTIVE.")

                # STAGE 3: THE TRUE INWARD RADIAL SLURP SYSTEM FOR HUMAN BODY (3.4s - 4.6s)
                elif 3.4 <= elapsed < 4.6:
                    collapse_factor = (elapsed - 3.4) / 1.2
                    
                    # Clean up the swirling core behind the void transition
                    portal_base = bg_cartoon.copy()
                    current_radius = int(140 * max(0.0, 1.0 - collapse_factor))
                    if current_radius > 5:
                        for r_offset in range(current_radius, 0, -8):
                            cv2.ellipse(portal_base, (p_cx, p_cy), (r_offset, int(r_offset*0.75)), 
                                        int(time.time()*-350)%360, 0, 360, (0, 240, 255), -1, cv2.LINE_AA)
                        cv2.addWeighted(portal_base, 0.9 * (1.0 - collapse_factor), bg_cartoon, 1.0 - (0.9 * (1.0 - collapse_factor)), 0, bg_cartoon)

                    # --- INWARD COVECTIVE SLURP VECTOR ENGINE ---
                    map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
                    map_x = map_x.astype(np.float32)
                    map_y = map_y.astype(np.float32)
                    
                    dx = map_x - p_cx
                    dy = map_y - p_cy
                    r_mesh = np.sqrt(dx**2 + dy**2)
                    theta_mesh = np.arctan2(dy, dx)
                    
                    # Exponential velocity multiplier pulling straight toward center
                    pull_rate = math.pow(collapse_factor, 2.2)
                    
                    # Fractional compression pulls pixels INWARD toward p_cx, p_cy
                    r_warped = r_mesh * (1.0 - (pull_rate * np.exp(-r_mesh / 160.0)))
                    theta_warped = theta_mesh + (pull_rate * 2.0 * np.exp(-r_mesh / 100.0)) # Fluid twist factor
                    
                    # Convert coordinate maps back to linear matrix slots
                    slurp_x = p_cx + r_warped * np.cos(theta_warped)
                    slurp_y = p_cy + r_warped * np.sin(theta_warped)
                    
                    # Remap your isolated body pixels straight into the coordinate sinkholes
                    slurped_matrix = cv2.remap(frame, slurp_x, slurp_y, cv2.INTER_LINEAR)
                    
                    display_frame = bg_cartoon.copy()
                    display_frame[motion_mask > 0] = slurped_matrix[motion_mask > 0]
                    
                    # Neon-white flash barrier at instant of complete compression collapse
                    if 4.45 <= elapsed < 4.6:
                        display_frame = cv2.add(display_frame, (255, 255, 255, 0))
                    self.status_var.set("CONSOLE // PHASE 3: HUMAN SLURP COMPRESSION ACTIVE.")

                # STAGE 4: RETURN TO TOTAL RAW NORMAL FEED (4.6s+)
                else:
                    # Snaps everything back to the normal webcam stream completely raw
                    display_frame = frame.copy()
                    self.state = 0
                    self.status_var.set("CONSOLE // COGNITIVE RE-STABILIZATION MET. SYSTEM SAFE.")

                if self.state != 0:
                    cv2.putText(display_frame, f"WARP_TIME: {elapsed:.2f}s", (30, h - 30), 
                                cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 235, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "SYS_STATUS // SPACE_TIME_STABLE", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map array data onto Tkinter canvas container
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
    UnrealStudioContinuous(tk.Tk(), "UNREAL Engine Reality Hop v5.5")