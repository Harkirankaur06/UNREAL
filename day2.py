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
        self.state = 0  # 0: Normal Feed, 1: Portal Anomaly Core
        
        # Timeline Mechanics
        self.panic_start_time = 0.0
        self.panic_duration = 4.0  # Slightly longer for the epic portal build
        
        # Static Background Frame Cache
        self.locked_clean_bg = None  
        
        # Advanced Portal Particle System
        self.portal_particles = []

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // MULTIVERSE PORTAL ENGINE - DAY 2", 
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
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. ESCAPE REALITY", command=self.activate_portal_sequence)
        self.btn_hover.grid(row=0, column=1, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET WINDOW", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=2, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // STANDBY. STEP OUT OF FRAME AND LOCK ROOM CACHE.")
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
            self.status_var.set("CONSOLE // ROOM GEOMETRY CACHED. READY FOR PORTAL SEQUENCE.")

    def activate_portal_sequence(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: LOCK ROOM CACHE FIRST!")
            return
        
        if self.state == 0:
            self.state = 1
            self.panic_start_time = time.time()
            self.portal_particles = [] # Clear old particles
            self.status_var.set("CONSOLE // RIFT DETECTED. HIGH-ENERGY CONDENSATION STARTING.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.state = 0
        self.locked_clean_bg = None
        self.portal_particles = []
        self.status_var.set("CONSOLE // WORKSPACE CLEAR. RE-CALIBRATE ROOM.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            if self.state == 1:
                elapsed = time.time() - self.panic_start_time
                
                if elapsed >= self.panic_duration:
                    self.state = 0
                    self.status_var.set("CONSOLE // ESCAPE SUCCESSFUL. BREAKOUT CONCLUDED.")
                
                # --- MOTION ISOLATION MATRIX ---
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                bg_gray = cv2.cvtColor(self.locked_clean_bg, cv2.COLOR_BGR2GRAY)
                frame_diff = cv2.absdiff(frame_gray, bg_gray)
                _, motion_mask = cv2.threshold(frame_diff, 22, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_DILATE, np.ones((5,5), np.uint8))
                
                # Default scene structure starts as the normal frozen room layout
                display_frame = self.locked_clean_bg.copy()
                p_cx, p_cy = w // 2, h // 2
                
                # --- PHASE 1 & 2: PANIC OVERLOAD + HIGH-END SPIDER-VERSE RIFT ---
                if elapsed < 3.2:
                    glitched_body = frame.copy()
                    b, g, r = cv2.split(glitched_body)
                    
                    shift = random.randint(25, 55)
                    r_shifted = np.roll(r, -shift, axis=1)
                    b_shifted = np.roll(b, shift, axis=1)
                    glitched_body = cv2.merge((b_shifted, g, r_shifted))
                    
                    # Horizontal slicing vectors
                    num_slices = random.randint(14, 22)
                    for _ in range(num_slices):
                        slice_y = random.randint(0, h - 20)
                        slice_h = random.randint(5, 18)
                        slice_shift = random.randint(-60, 60)
                        glitched_body[slice_y:slice_y+slice_h, :] = np.roll(
                            glitched_body[slice_y:slice_y+slice_h, :], slice_shift, axis=1
                        )
                    
                    glitched_body[:, :, 2] = cv2.add(glitched_body[:, :, 2], 75) # Aggressive Pink
                    glitched_body[:, :, 0] = cv2.add(glitched_body[:, :, 0], 45) # Intense Indigo
                    
                    # --- PROCEDURAL HIGH-ENERGY PORTAL GENERATION ---
                    portal_overlay = display_frame.copy()
                    
                    # Scale portal up gracefully over the first 1.5 seconds
                    growth_factor = min(1.0, elapsed / 1.5)
                    base_radius = int(140 * growth_factor)
                    
                    if base_radius > 10:
                        # 1. Spawn spinning outer ring energy streaks
                        for _ in range(15):
                            angle = random.uniform(0, 2 * math.pi)
                            # Add an undulating ripple based on a quick wave calculation
                            distortion = 1.0 + 0.15 * math.sin(time.time() * 25 + angle * 4)
                            r_curr = int(base_radius * distortion)
                            
                            px = int(p_cx + r_curr * math.cos(angle))
                            py = int(p_cy + r_curr * 0.8 * math.sin(angle)) # Sightly squashed anamorphic ring
                            
                            p_color = random.choice([(255, 0, 140), (0, 240, 255), (255, 255, 255)])
                            cv2.circle(portal_overlay, (px, py), random.randint(2, 6), p_color, -1, cv2.LINE_AA)
                        
                        # 2. Draw intense internal multi-layered neon energy bands
                        for r_offset in range(base_radius, 0, -10):
                            phase_shift = r_offset * 0.1 - time.time() * 15
                            wave_val = 1.0 + 0.1 * math.sin(phase_shift)
                            rx = int(r_offset * wave_val)
                            ry = int(r_offset * 0.8 * wave_val)
                            
                            # Alternate colors through the rift core layers
                            if r_offset % 30 == 0:
                                col = (255, 0, 140) # Hot Magenta
                            elif r_offset % 20 == 0:
                                col = (0, 230, 255) # Electric Cyan
                            else:
                                col = (40, 10, 50)  # Dark Void Core
                                
                            cv2.ellipse(portal_overlay, (p_cx, p_cy), (rx, ry), int(time.time() * 60) % 360, 0, 360, col, -1, cv2.LINE_AA)

                        # Mix portal graphics onto clean background template
                        cv2.addWeighted(portal_overlay, 0.85, display_frame, 0.15, 0, display_frame)

                    # Seamlessly layer your live glitched body ON TOP of the background room and portal
                    display_frame[motion_mask > 0] = glitched_body[motion_mask > 0]
                    
                # --- PHASE 3: THE DETONATION ZAP & COLLAPSE ---
                elif 3.2 <= elapsed < self.panic_duration:
                    # You have broken reality and faded out. Only the portal remains, aggressively shrinking.
                    portal_overlay = display_frame.copy()
                    collapse_factor = max(0.0, 1.0 - ((elapsed - 3.2) / (self.panic_duration - 3.2)))
                    base_radius = int(140 * collapse_factor)
                    
                    if base_radius > 2:
                        for r_offset in range(base_radius, 0, -8):
                            rx = int(r_offset * (1.0 + 0.1 * math.sin(time.time() * 40)))
                            ry = int(r_offset * 0.8)
                            cv2.ellipse(portal_overlay, (p_cx, p_cy), (rx, ry), int(time.time() * -180) % 360, 0, 360, (0, 240, 255), -1, cv2.LINE_AA)
                        cv2.addWeighted(portal_overlay, 0.9 * collapse_factor, display_frame, 1.0 - (0.9 * collapse_factor), 0, display_frame)
                    
                    # Absolute blinding white-hot flash on frame transition
                    if 3.2 <= elapsed < 3.32:
                        display_frame = cv2.add(display_frame, (245, 245, 245, 0))

                # HUD Diagnostics
                cv2.putText(display_frame, "EVAC_SEQUENCE_ACTIVE", (30, h - 30), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.55, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                # Standby state
                cv2.putText(display_frame, "PORTAL STABLE // SYSTEM READY", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map to Tkinter Canvas Output
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
    UnrealStudioContinuous(tk.Tk(), "UNREAL Engine Studio Workspace v5.0")