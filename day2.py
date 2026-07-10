import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import time

class UnrealStudioContinuous:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#0B0B0C")
        
        self.cap = cv2.VideoCapture(0)
        
        # Core State Variables
        self.is_calibrated = False
        self.is_levitating = False
        self.state = 0  # 0: Setup, 1: Panic Float, 2: Heavy Drop
        
        # Physics Engines
        self.float_y = 0.0
        self.float_speed = 1.8   # Faster upward panic climb
        self.gravity = 2.8       # Heavy gravitational slam down
        self.drop_velocity = 0.0
        
        # Geometry and Live Tracking Cache
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None  
        self.tracker = None 

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // MULTIVERSE PANIC ENGINE - DAY 2", 
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
        
        self.btn_select = ttk.Button(self.btn_frame, text="2. PROFILE GRABCUT", command=self.run_grabcut_selection)
        self.btn_select.grid(row=0, column=1, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="3. UNLEASH PANIC", command=self.activate_panic_state)
        self.btn_hover.grid(row=0, column=2, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET SYSTEM", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=3, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // ENGINE INITIALIZED. LOCK BACKGROUND TEMPLATE TO START.")
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
            self.status_var.set("CONSOLE // ROOM CACHED. RUN GRABCUT SELECT ON TARGET OBJECT.")

    def run_grabcut_selection(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: CACHE BACKGROUND BEFORE SELECTION.")
            return
            
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            roi_bbox = cv2.selectROI("UNREAL // SELECT CHOSEN PROB", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("UNREAL // SELECT CHOSEN PROB")
            
            ox, oy, ow, oh = [int(v) for v in roi_bbox]
            
            if ow > 15 and oh > 15:
                self.bbox = (ox, oy, ow, oh)
                self.status_var.set("CONSOLE // PARSING EXTRACTED MATRIX SEGMENTS...")
                self.window.update()
                
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                gc_mask = np.zeros(frame.shape[:2], np.uint8)
                
                cv2.grabCut(frame, gc_mask, self.bbox, bgdModel, fgdModel, 6, cv2.GC_INIT_WITH_RECT)
                
                self.precise_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 255).astype('uint8')
                self.precise_mask = cv2.morphologyEx(self.precise_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
                
                self.object_crop = frame[oy:oy+oh, ox:ox+ow].copy()
                self.mask_crop = self.precise_mask[oy:oy+oh, ox:ox+ow].copy()
                
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, self.bbox)
                
                self.status_var.set("CONSOLE // SEGMENTATION PROFILE LOCKED. INITIALIZE PANIC WINDOW.")

    def activate_panic_state(self):
        if self.precise_mask is None:
            return
        
        if self.state == 0:
            self.state = 1
            self.is_levitating = True
            self.float_y = 0.0
            self.status_var.set("CONSOLE // UNREALITY DETECTED: SPATIAL ANOMALY IN PROGRESS.")
            self.btn_hover.config(text="4. SNAP GRAVITY")
        elif self.state == 1:
            self.state = 2
            self.drop_velocity = 0.0
            self.status_var.set("CONSOLE // SNAP EVENT: CRITICAL GRAVITATIONAL COLLAPSE.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.state = 0
        self.float_y = 0.0
        self.drop_velocity = 0.0
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None
        self.tracker = None
        self.btn_hover.config(text="3. LAUNCH HOVER")
        self.status_var.set("CONSOLE // MEMORY DISMISSED. STANDBY.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # --- CONTINUOUS TRACKING & RENDERING PIPELINE ---
            if self.tracker is not None:
                track_success, current_box = self.tracker.update(frame)
                
                if track_success:
                    ox, oy, ow, oh = [int(v) for v in current_box]
                    
                    if ow > 5 and oh > 5 and ox >= 0 and oy >= 0 and (ox + ow) <= w and (oy + oh) <= h:
                        live_mask_crop = cv2.resize(self.mask_crop, (ow, oh))
                        live_object_crop = cv2.resize(self.object_crop, (ow, oh))
                        
                        # Dynamic Mask Allocation
                        dynamic_mask = np.zeros(frame.shape[:2], np.uint8)
                        dynamic_mask[oy:oy+oh, ox:ox+ow] = live_mask_crop
                        inv_mask = cv2.bitwise_not(dynamic_mask)

                        if self.is_levitating:
                            # 1. APPLY EXTREME BODY PANIC GLITCH (To everything except the floating object)
                            glitched_scene = frame.copy()
                            
                            # Independent Chromatic Splits
                            b, g, r = cv2.split(glitched_scene)
                            shift = random.randint(18, 35) # Brutal pixel misalignment
                            r_shifted = np.roll(r, -shift, axis=1)
                            b_shifted = np.roll(b, shift, axis=1)
                            glitched_scene = cv2.merge((b_shifted, g, r_shifted))
                            
                            # Horizontal Interdimensional Shear Slicing
                            num_slices = random.randint(8, 14)
                            for _ in range(num_slices):
                                slice_y = random.randint(0, h - 20)
                                slice_h = random.randint(6, 22)
                                slice_shift = random.randint(-40, 40)
                                glitched_scene[slice_y:slice_y+slice_h, :] = np.roll(
                                    glitched_scene[slice_y:slice_y+slice_h, :], slice_shift, axis=1
                                )
                            
                            # Infuse Spider-Verse Tint Palette (Hot Magentas / Electric Purples)
                            glitched_scene[:, :, 2] = cv2.add(glitched_scene[:, :, 2], 55)
                            glitched_scene[:, :, 0] = cv2.add(glitched_scene[:, :, 0], 25)

                            # Patch out the object's background coordinates seamlessly
                            clean_room_base = cv2.bitwise_and(glitched_scene, glitched_scene, mask=inv_mask)
                            bg_patch = cv2.bitwise_and(self.locked_clean_bg, self.locked_clean_bg, mask=dynamic_mask)
                            display_frame = cv2.add(clean_room_base, bg_patch)
                            
                            # 2. OBJECT PHYSICS LAYER
                            if self.state == 1:
                                # Slow, eerie zero-gravity climb
                                self.float_y -= self.float_speed
                            elif self.state == 2:
                                # Acceleration via downward gravity pull
                                self.drop_velocity += self.gravity
                                self.float_y += self.drop_velocity
                                
                                # Crash Check Reset
                                if self.float_y >= 0:
                                    self.float_y = 0.0
                                    self.state = 0
                                    self.is_levitating = False
                                    self.btn_hover.config(text="3. LAUNCH HOVER")
                                    self.status_var.set("CONSOLE // RE-STABILIZED. SYSTEM RESTORED.")

                            # Compute relative floating layout positioning
                            current_y = oy + int(self.float_y)
                            
                            if current_y > 5 and (current_y + oh) < h:
                                roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                                
                                # Render ONLY the true object silhouette shape, no rectangular backgrounds!
                                img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(live_mask_crop))
                                img_fg = cv2.bitwise_and(live_object_crop, live_object_crop, mask=live_mask_crop)
                                
                                display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                        else:
                            # Tracking Standby Hud Output (GrabCut Outline Check)
                            contours, _ = cv2.findContours(dynamic_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            cv2.drawContours(display_frame, contours, -1, (255, 0, 128), 2, cv2.LINE_AA)
                else:
                    self.status_var.set("CONSOLE // MATRIX BREACH: LOCK-ON DROP.")

            # Spider-Verse Reality Anomaly Aesthetic Watermark
            if self.is_levitating and random.random() > 0.7:
                # Intermittent flicker text overlay during breach state
                cv2.putText(display_frame, "WARNING: MULTIVERSE COLLAPSE", (30, h - 30), 
                            cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "SYS_STATUS // PORTAL_STABLE", (30, h - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

            # Map to Tkinter Canvas Frame
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
    UnrealStudioContinuous(tk.Tk(), "UNREAL Engine Studio Workspace v4.6")