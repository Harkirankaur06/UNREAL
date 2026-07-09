import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
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
        self.float_y = 0
        self.target_hover_height = -90
        
        # Geometry and Live Tracking Cache
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None  
        self.tracker = None # Live structural engine

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // CONTINUOUS LIVE ISOLATION STUDIO", 
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
        
        self.btn_bg = ttk.Button(self.btn_frame, text="1. LOCK BACKGROUND", command=self.lock_clean_background)
        self.btn_bg.grid(row=0, column=0, padx=12)
        
        self.btn_select = ttk.Button(self.btn_frame, text="2. GRABCUT SELECT", command=self.run_grabcut_selection)
        self.btn_select.grid(row=0, column=1, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="3. LAUNCH HOVER", command=self.activate_hover)
        self.btn_hover.grid(row=0, column=2, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=3, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // PORTAL STABLE. STEP OUT AND LOCK BACKGROUND.")
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
            self.status_var.set("CONSOLE // BACKGROUND CACHED. CHOOSE OBJECT & GRABCUT SELECT.")

    def run_grabcut_selection(self):
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: LOCK BACKGROUND FIRST!")
            return
            
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            roi_bbox = cv2.selectROI("UNREAL // BOUNDARY CAPTURE", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("UNREAL // BOUNDARY CAPTURE")
            
            ox, oy, ow, oh = [int(v) for v in roi_bbox]
            
            if ow > 15 and oh > 15:
                self.bbox = (ox, oy, ow, oh)
                self.status_var.set("CONSOLE // GENERATING SILHOUETTE MATRIX...")
                self.window.update()
                
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                gc_mask = np.zeros(frame.shape[:2], np.uint8)
                
                cv2.grabCut(frame, gc_mask, self.bbox, bgdModel, fgdModel, 6, cv2.GC_INIT_WITH_RECT)
                
                self.precise_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 255).astype('uint8')
                self.precise_mask = cv2.morphologyEx(self.precise_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
                
                self.object_crop = frame[oy:oy+oh, ox:ox+ow].copy()
                self.mask_crop = self.precise_mask[oy:oy+oh, ox:ox+ow].copy()
                
                # Fire up the live CSRT Tracker to follow the object as it moves!
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, self.bbox)
                
                self.status_var.set("CONSOLE // SILHOUETTE PROFILE ENGAGED. LAUNCH HOVER WHEN READY.")

    def activate_hover(self):
        if self.precise_mask is not None:
            self.is_levitating = True
            self.status_var.set("CONSOLE // MOTION LEVITATION MATRIX ENGAGED. MOVE FREELY.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None
        self.tracker = None
        self.status_var.set("CONSOLE // WORKSPACE TERMINATED. SYSTEM READY.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # --- CONTINUOUS TRACKING & RENDERING PIPELINE ---
            if self.tracker is not None:
                # Continuously follow the object location live frame-by-frame
                track_success, current_box = self.tracker.update(frame)
                
                if track_success:
                    ox, oy, ow, oh = [int(v) for v in current_box]
                    
                    # Prevent outbound array execution crashes
                    if ow > 5 and oh > 5 and ox >= 0 and oy >= 0 and (ox + ow) <= w and (oy + oh) <= h:
                        
                        # Dynamically resize the static high-res mask template to match the live tracking scale
                        live_mask_crop = cv2.resize(self.mask_crop, (ow, oh))
                        live_object_crop = cv2.resize(self.object_crop, (ow, oh))
                        
                        if self.is_levitating:
                            # 1. LIVE REPLACEMENT: Reconstruct the current background where the object moves
                            dynamic_mask = np.zeros(frame.shape[:2], np.uint8)
                            dynamic_mask[oy:oy+oh, ox:ox+ow] = live_mask_crop
                            
                            inv_mask = cv2.bitwise_not(dynamic_mask)
                            live_body = cv2.bitwise_and(frame, frame, mask=inv_mask)
                            static_bg_fill = cv2.bitwise_and(self.locked_clean_bg, self.locked_clean_bg, mask=dynamic_mask)
                            
                            # Object area is continuously painted away with sharp background pixels
                            display_frame = cv2.add(live_body, static_bg_fill)
                            
                            # 2. CONTINUOUS HOVER ANIMATION
                            if self.float_y > self.target_hover_height:
                                self.float_y -= 4
                            
                            # Anchor the floating position directly to the moving 'oy' track coordinate!
                            current_y = oy + self.float_y
                            
                            if current_y > 5 and (current_y + oh) < h:
                                roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                                
                                img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(live_mask_crop))
                                img_fg = cv2.bitwise_and(live_object_crop, live_object_crop, mask=live_mask_crop)
                                
                                # Render the floating copy seamlessly over the moving scene
                                display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                        else:
                            # Standby Preview Mode: Render live tracking outline bounding box
                            cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    self.status_var.set("CONSOLE // LOCK-ON LOST. PRESS RESET.")

            # Viewport Overlay
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(display_frame, "UNREAL_LIVE_ENGINE_v4.6", (60, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

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