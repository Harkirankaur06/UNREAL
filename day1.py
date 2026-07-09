import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class UnrealStudioFinal:
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
        
        # Geometry Cache
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None  # Holds sharp background pixels

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // GRABCUT HIGH-RES ISOLATION STUDIO", 
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
        self.status_var.set("CONSOLE // STEP OUT OF WEB FRAME, THEN CLICK LOCK BACKGROUND...")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#8A8A93", bg="#101012", font=("Courier", 9), width=90, anchor="w", padx=12, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.delay = 15
        self.update_stream_loop()
        self.window.mainloop()

    def lock_clean_background(self):
        """Snaps a perfect high-res reference layer of the empty frame"""
        ret, frame = self.cap.read()
        if ret:
            self.locked_clean_bg = cv2.flip(frame, 1)
            self.is_calibrated = True
            self.status_var.set("CONSOLE // BACKGROUND LAYER STORAGE STABLE. CLICK GRABCUT SELECT.")

    def run_grabcut_selection(self):
        """Launches live selection and builds a solid, non-faded contour mask"""
        if not self.is_calibrated:
            self.status_var.set("CONSOLE // ERROR: PLEASE LOCK BACKGROUND FIRST!")
            return
            
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            roi_bbox = cv2.selectROI("UNREAL // BOUNDARY CAPTURE", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("UNREAL // BOUNDARY CAPTURE")
            
            ox, oy, ow, oh = [int(v) for v in roi_bbox]
            
            if ow > 15 and oh > 15:
                self.bbox = (ox, oy, ow, oh)
                self.status_var.set("CONSOLE // CALCULATING PIXEL BOUNDARIES... PLEASE WAIT.")
                self.window.update()
                
                # Setup GrabCut Allocations
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                gc_mask = np.zeros(frame.shape[:2], np.uint8)
                
                cv2.grabCut(frame, gc_mask, self.bbox, bgdModel, fgdModel, 7, cv2.GC_INIT_WITH_RECT)
                
                # Critical Fix: Convert strictly to a solid 0 or 255 binary block to remove fading completely
                self.precise_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 255).astype('uint8')
                self.precise_mask = cv2.morphologyEx(self.precise_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
                
                # Extract clean, high-contrast, un-faded object color segments
                self.object_crop = frame[oy:oy+oh, ox:ox+ow].copy()
                self.mask_crop = self.precise_mask[oy:oy+oh, ox:ox+ow].copy()
                
                self.status_var.set("CONSOLE // SILHOUETTE PROFILE LOCKED. READY FOR LAUNCH HOVER.")

    def activate_hover(self):
        if self.precise_mask is not None:
            self.is_levitating = True
            self.status_var.set("CONSOLE // HOVER RUNNING. LIVE PIXEL SWAP ENGAGED.")

    def reset_workspace(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None
        self.status_var.set("CONSOLE // BASELINE PREVIEW ACTIVE. COMMENCE CALIBRATION STEP 1.")

    def update_stream_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # --- RENDERING ENGINE ---
            if self.is_levitating and self.bbox is not None:
                ox, oy, ow, oh = self.bbox
                
                # 1. PIXEL REPLACEMENT (Zero Blur, Zero Fading)
                # Overwrite *only* the silhouette region using the sharp pre-saved room texture
                inv_mask = cv2.bitwise_not(self.precise_mask)
                live_body = cv2.bitwise_and(frame, frame, mask=inv_mask)
                static_bg_fill = cv2.bitwise_and(self.locked_clean_bg, self.locked_clean_bg, mask=self.precise_mask)
                
                # Completely replaces the object location with flat background image space
                display_frame = cv2.add(live_body, static_bg_fill)
                
                # 2. DIGITAL ELEVATION RENDER
                if self.float_y > self.target_hover_height:
                    self.float_y -= 4
                current_y = oy + self.float_y
                
                if current_y > 5 and (current_y + oh) < h:
                    roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                    
                    # Merge clean object back over scene without alpha blending to stop fading
                    img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(self.mask_crop))
                    img_fg = cv2.bitwise_and(self.object_crop, self.object_crop, mask=self.mask_crop)
                    
                    display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
            
            elif self.precise_mask is not None and not self.is_levitating:
                # Show active contour boundary preview lines before launching
                contours, _ = cv2.findContours(self.precise_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(display_frame, contours, -1, (0, 255, 0), 1, cv2.LINE_AA)

            # Viewport Accents
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(display_frame, "UNREAL_CORE_STUDIO", (60, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # Map to Tkinter Display Canvas
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
    UnrealStudioFinal(tk.Tk(), "UNREAL Engine Studio Workspace v4.5")