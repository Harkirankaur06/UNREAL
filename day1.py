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
        
        # 1. Initialize Adaptive Background Model (Shadow-aware)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=True)
        
        # Core State Machine
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.target_hover_height = -90
        
        self.object_mask = None
        self.object_texture = None
        self.saved_coords = None

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // LIVE BACKGROUND SEGMENTATION STUDIO", 
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
        self.status_var.set("CONSOLE // STEP OUT OF FRAME OR KEEP IT CLEAR TO TRAIN BACKGROUND MODULE LIVE...")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#8A8A93", bg="#101012", font=("Courier", 9), width=85, anchor="w", padx=12, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.delay = 15
        self.update_workspace()
        self.window.mainloop()

    def lock_background(self):
        """Freezes the probabilistic background model map"""
        self.is_calibrated = True
        self.status_var.set("CONSOLE // BACKGROUND SEGMENTATION STABLE. PLACE OBJECT & CLICK HOVER.")

    def trigger_hover(self):
        if self.is_calibrated and self.object_mask is not None:
            self.is_levitating = True
            self.status_var.set("CONSOLE // OVERRIDE INVERSIONS STREAMING LIVE.")

    def reset_system(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.object_mask = None
        self.object_texture = None
        self.saved_coords = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=True)
        self.status_var.set("CONSOLE // RESET COMPLETE. RE-TRAINING BACKGROUND...")

    def update_workspace(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # 1. Update background subtraction model loop
            if not self.is_calibrated:
                # The model is constantly learning the empty room layout here
                fg_mask = self.bg_subtractor.apply(frame)
            else:
                # When locked, evaluate frame changes without training the background further
                fg_mask = self.bg_subtractor.apply(frame, learningRate=0)
                
                # Filter out human skin tones/shadows from the object mask layout
                ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
                
                # Object mask = movement difference minus skin mask - filters shadows (gray code 127)
                _, clean_fg = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY) 
                only_object = cv2.bitwise_and(clean_fg, cv2.bitwise_not(skin_mask))
                
                # Cleanup edge dilation errors
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                only_object = cv2.morphologyEx(only_object, cv2.MORPH_CLOSE, kernel, iterations=2)
                
                contours, _ = cv2.findContours(only_object, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours and not self.is_levitating:
                    largest_contour = max(contours, key=cv2.contourArea)
                    if cv2.contourArea(largest_contour) > 400:
                        ox, oy, ow, oh = cv2.boundingRect(largest_contour)
                        self.saved_coords = (ox, oy, ow, oh)
                        
                        # Cache the targeted object data structure
                        self.object_mask = np.zeros_like(only_object)
                        cv2.drawContours(self.object_mask, [largest_contour], -1, 255, -1)
                        self.object_texture = frame.copy()

            # --- 2. RENDER HOVER AND RENDER BACKGROUND ---
            if self.is_levitating and self.saved_coords is not None:
                ox, oy, ow, oh = self.saved_coords
                
                # A. Render background underneath using the live running background frame model
                live_bg = self.bg_subtractor.getBackgroundImage()
                if live_bg is None: live_bg = frame.copy()
                
                # Inpaint patch the exact contour area on the live camera loop
                display_frame = cv2.inpaint(frame, self.object_mask, 7, cv2.INPAINT_TELEA)
                
                # B. Hover physics step
                if self.float_y > self.target_hover_height:
                    self.float_y -= 4
                current_y = oy + self.float_y
                
                if current_y > 10 and (current_y + oh) < h:
                    # Isolate object segment matrices
                    mask_crop = self.object_mask[oy:oy+oh, ox:ox+ow]
                    texture_crop = self.object_texture[oy:oy+oh, ox:ox+ow]
                    
                    roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                    
                    img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask_crop))
                    img_fg = cv2.bitwise_and(texture_crop, texture_crop, mask=mask_crop)
                    
                    display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                    cv2.line(display_frame, (ox, current_y + oh + 4), (ox + ow, current_y + oh + 4), (0, 229, 255), 2, cv2.LINE_AA)
            
            elif self.is_calibrated and self.saved_coords is not None and not self.is_levitating:
                # Show targeting preview line boundaries
                cx, cy, cw, ch = self.saved_coords
                cv2.rectangle(display_frame, (cx, cy), (cx+cw, cy+ch), (0, 255, 0), 1, cv2.LINE_AA)

            # Technical corner brackets HUD
            bl = 20
            cv2.line(display_frame, (30, 30), (30 + bl, 30), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (30, 30), (30, 30 + bl), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (w - 30, 30), (w - 30 - bl, 30), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (w - 30, 30), (w - 30, 30 + bl), (255, 255, 255), 1, cv2.LINE_AA)
            
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(display_frame, "UNREAL_STUDIO_LIVE", (60, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # Update Canvas frame
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
    UnrealEngineStudio(tk.Tk(), "UNREAL Studio Workspace v3.0")