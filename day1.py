import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class UnrealEngineStudio:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#0B0B0C")
        
        self.cap = cv2.VideoCapture(0)
        
        # Initialize Adaptive Background Model
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=False)
        
        # Core State Machine
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.target_hover_height = -90
        
        self.object_mask = None
        self.object_texture = None
        self.saved_coords = None
        self.locked_clean_bg = None # Caches the sharp background pixels

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // LIVE SEGMENTATION STUDIO v4.0", 
                               fg="#00E5FF", bg="#0B0B0C", font=("Courier", 12, "bold"))
        self.header.pack(pady=10)
        
        self.canvas = tk.Canvas(window, width=640, height=480, bg="#101012", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        self.btn_frame = tk.Frame(window, bg="#0B0B0C")
        self.btn_frame.pack(pady=15)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#1C1C22', borderwidth=0)
        style.map('TButton', background=[('active', '#00E5FF')], foreground=[('active', '#0B0B0C')])
        
        self.btn_lock = ttk.Button(self.btn_frame, text="1. LOCK BACKGROUND", command=self.lock_background)
        self.btn_lock.grid(row=0, column=0, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. INVERT & HOVER", command=self.trigger_hover)
        self.btn_hover.grid(row=0, column=1, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET SYSTEM", command=self.reset_system)
        self.btn_reset.grid(row=0, column=2, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // STEP OUT OF FRAME TO TRAIN BACKGROUND MODULE LIVE...")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#8A8A93", bg="#101012", font=("Courier", 9), width=85, anchor="w", padx=12, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.delay = 15
        self.update_workspace()
        self.window.mainloop()

    def lock_background(self):
        """Captures a sharp template of the clean background room"""
        self.locked_clean_bg = self.bg_subtractor.getBackgroundImage()
        if self.locked_clean_bg is None:
            # Fallback if model isn't completely saturated yet
            _, frame = self.cap.read()
            self.locked_clean_bg = cv2.flip(frame, 1)
            
        self.is_calibrated = True
        self.status_var.set("CONSOLE // SHARP BACKGROUND REPLICATED. PLACE OBJECT & CLICK HOVER.")

    def trigger_hover(self):
        if self.is_calibrated and self.object_mask is not None:
            self.is_levitating = True
            self.status_var.set("CONSOLE // LEVITATION SEQUENCE ACTIVE. ZERO BLUR MATRIX APPLIED.")

    def reset_system(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.object_mask = None
        self.object_texture = None
        self.saved_coords = None
        self.locked_clean_bg = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=False)
        self.status_var.set("CONSOLE // RESET COMPLETE. RE-TRAINING BACKGROUND...")

    def update_workspace(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            if not self.is_calibrated:
                fg_mask = self.bg_subtractor.apply(frame)
            else:
                fg_mask = self.bg_subtractor.apply(frame, learningRate=0)
                
                # Dynamic Skin Isolation
                ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
                
                _, clean_fg = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY) 
                only_object = cv2.bitwise_and(clean_fg, cv2.bitwise_not(skin_mask))
                
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                only_object = cv2.morphologyEx(only_object, cv2.MORPH_CLOSE, kernel, iterations=2)
                
                contours, _ = cv2.findContours(only_object, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours and not self.is_levitating:
                    largest_contour = max(contours, key=cv2.contourArea)
                    if cv2.contourArea(largest_contour) > 400:
                        ox, oy, ow, oh = cv2.boundingRect(largest_contour)
                        self.saved_coords = (ox, oy, ow, oh)
                        
                        self.object_mask = np.zeros_like(only_object)
                        cv2.drawContours(self.object_mask, [largest_contour], -1, 255, -1)
                        self.object_texture = frame.copy()

            # --- RENDER HOVER ENGINE ---
            if self.is_levitating and self.saved_coords is not None:
                ox, oy, ow, oh = self.saved_coords
                
                # FIX 1: RECONSTRUCT BACKGROUND IN PLACE OF THE OBJECT WITH CRISP PIXELS
                # Instead of blurring, we paste the pristine clean room texture directly over the shape
                inv_object_mask = cv2.bitwise_not(self.object_mask)
                live_bg_restored = cv2.bitwise_and(frame, frame, mask=inv_object_mask)
                static_clean_patch = cv2.bitwise_and(self.locked_clean_bg, self.locked_clean_bg, mask=self.object_mask)
                
                # Combine them—the object is now perfectly replaced by the true background with 0% blur
                display_frame = cv2.add(live_bg_restored, static_clean_patch)
                
                # Hover Calculation
                if self.float_y > self.target_hover_height:
                    self.float_y -= 4
                current_y = oy + self.float_y
                
                if current_y > 10 and (current_y + oh) < h:
                    mask_crop = self.object_mask[oy:oy+oh, ox:ox+ow]
                    texture_crop = self.object_texture[oy:oy+oh, ox:ox+ow]
                    
                    roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                    
                    img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask_crop))
                    img_fg = cv2.bitwise_and(texture_crop, texture_crop, mask=mask_crop)
                    
                    # Merge the clean floating object over the scene
                    display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                    
                    # FIX 2: Yellow line is completely removed from here! No line artifacts.
            
            elif self.is_calibrated and self.saved_coords is not None and not self.is_levitating:
                cx, cy, cw, ch = self.saved_coords
                cv2.rectangle(display_frame, (cx, cy), (cx+cw, cy+ch), (0, 255, 0), 1, cv2.LINE_AA)

            # Minimalist Recording HUD
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(display_frame, "UNREAL_STUDIO_LIVE", (60, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # Update Canvas Frame
            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas.img_tk = img_tk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            
        self.window.after(self.delay, self.update_workspace)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    UnrealEngineStudio(tk.Tk(), "UNREAL Studio Workspace v4.0")