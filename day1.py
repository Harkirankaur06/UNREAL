import cv2
import numpy as np
import time

class Day1LevitationEngine:
    def __init__(self):
        # Operational states transferred from Tkinter memory storage
        self.locked_clean_bg = None
        self.is_calibrated = False
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.tracker = None
        self.is_levitating = False
        self.float_y = 0
        self.target_hover_height = -90

    def process_frame(self, frame):
        """
        Main interface entry point targeted by app.py.
        Accepts a standalone frame matrix, applies active filter logic, 
        and returns the modified image output back to the stream layer.
        """
        h, w, c = frame.shape
        display_frame = frame.copy()

        # If background hasn't been cached yet, auto-capture first initialization frame
        if not self.is_calibrated:
            self.locked_clean_bg = frame.copy()
            self.is_calibrated = True

        # --- CONTINUOUS TRACKING & RENDERING PIPELINE ---
        if self.tracker is not None:
            track_success, current_box = self.tracker.update(frame)
            
            if track_success:
                ox, oy, ow, oh = [int(v) for v in current_box]
                
                # Check execution bounding boxes to prevent outbound indexing crashes
                if ow > 5 and oh > 5 and ox >= 0 and oy >= 0 and (ox + ow) <= w and (oy + oh) <= h:
                    
                    live_mask_crop = cv2.resize(self.mask_crop, (ow, oh))
                    live_object_crop = cv2.resize(self.object_crop, (ow, oh))
                    
                    if self.is_levitating:
                        # 1. LIVE REPLACEMENT: Fill background matrix gap
                        dynamic_mask = np.zeros(frame.shape[:2], np.uint8)
                        dynamic_mask[oy:oy+oh, ox:ox+ow] = live_mask_crop
                        
                        inv_mask = cv2.bitwise_not(dynamic_mask)
                        live_body = cv2.bitwise_and(frame, frame, mask=inv_mask)
                        static_bg_fill = cv2.bitwise_and(self.locked_clean_bg, self.locked_clean_bg, mask=dynamic_mask)
                        
                        display_frame = cv2.add(live_body, static_bg_fill)
                        
                        # 2. CONTINUOUS HOVER ANIMATION 
                        if self.float_y > self.target_hover_height:
                            self.float_y -= 4
                        
                        current_y = oy + self.float_y
                        
                        if current_y > 5 and (current_y + oh) < h:
                            roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                            img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(live_mask_crop))
                            img_fg = cv2.bitwise_and(live_object_crop, live_object_crop, mask=live_mask_crop)
                            
                            display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                    else:
                        # Standby Mode: Render structural tracking box bounding line
                        cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 0), 1, cv2.LINE_AA)
            else:
                cv2.putText(display_frame, "ENGINE EXCEPTION: LOCK-ON LOST", (20, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # Technical Engineering UI Watermark Layer
        if int(time.time() * 2) % 2 == 0:
            cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
        cv2.putText(display_frame, "LIVE_VISION_ENGINE_v4.6", (60, 56), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        return display_frame

    # --- SIMULATED USER INTERACTION HANDLERS FOR WEB PLATFORM CONTROLS ---
    def trigger_bg_lock(self, current_frame):
        self.locked_clean_bg = current_frame.copy()
        self.is_calibrated = True

    def trigger_grabcut_init(self, current_frame, bbox_coords):
        """
        Accepts programmatic bounding boxes [x, y, w, h] to execute GrabCut tasks
        without prompting blocking cv2.selectROI desktop call loops.
        """
        ox, oy, ow, oh = bbox_coords
        if ow > 15 and oh > 15:
            self.bbox = (ox, oy, ow, oh)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            gc_mask = np.zeros(current_frame.shape[:2], np.uint8)
            
            cv2.grabCut(current_frame, gc_mask, self.bbox, bgdModel, fgdModel, 6, cv2.GC_INIT_WITH_RECT)
            
            self.precise_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 255).astype('uint8')
            self.precise_mask = cv2.morphologyEx(self.precise_mask, cv2.MORPH_CLOSE, 
                                                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
            
            self.object_crop = current_frame[oy:oy+oh, ox:ox+ow].copy()
            self.mask_crop = self.precise_mask[oy:oy+oh, ox:ox+ow].copy()
            
            self.tracker = cv2.TrackerCSRT_create()
            self.tracker.init(current_frame, self.bbox)

    def trigger_hover(self):
        if self.precise_mask is not None:
            self.is_levitating = True

    def trigger_reset(self):
        self.is_calibrated = False
        self.is_levitating = False
        self.float_y = 0
        self.bbox = None
        self.precise_mask = None
        self.object_crop = None
        self.mask_crop = None
        self.locked_clean_bg = None
        self.tracker = None


# ====================================================================
# 5. DESKTOP LOCAL COMPATIBILITY BACKWARD-GUARD
# ====================================================================
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk

    class VisionStudioContinuous:
        def __init__(self, window, window_title):
            self.window = window
            self.window.title(window_title)
            self.window.configure(bg="#0B0B0C")
            
            # Instantiate our isolated engine logic
            self.engine = Day1LevitationEngine()
            self.cap = cv2.VideoCapture(0)
            
            # UI Viewport Setup
            self.header = tk.Label(window, text="CONTINUOUS LIVE ISOLATION STUDIO", 
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
                frame = cv2.flip(frame, 1)
                self.engine.trigger_bg_lock(frame)
                self.status_var.set("CONSOLE // BACKGROUND CACHED. CHOOSE OBJECT & GRABCUT SELECT.")

        def run_grabcut_selection(self):
            if not self.engine.is_calibrated:
                self.status_var.set("CONSOLE // ERROR: LOCK BACKGROUND FIRST!")
                return
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                roi_bbox = cv2.selectROI("BOUNDARY CAPTURE", frame, fromCenter=False, showCrosshair=False)
                cv2.destroyWindow("BOUNDARY CAPTURE")
                
                ox, oy, ow, oh = [int(v) for v in roi_bbox]
                if ow > 15 and oh > 15:
                    self.status_var.set("CONSOLE // GENERATING SILHOUETTE MATRIX...")
                    self.window.update()
                    self.engine.trigger_grabcut_init(frame, (ox, oy, ow, oh))
                    self.status_var.set("CONSOLE // SILHOUETTE PROFILE ENGAGED. LAUNCH HOVER WHEN READY.")

        def activate_hover(self):
            self.engine.trigger_hover()
            self.status_var.set("CONSOLE // MOTION LEVITATION MATRIX ENGAGED. MOVE FREELY.")

        def reset_workspace(self):
            self.engine.trigger_reset()
            self.status_var.set("CONSOLE // WORKSPACE TERMINATED. SYSTEM READY.")

        def update_stream_loop(self):
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                display_frame = self.engine.process_frame(frame)
                
                img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img_tk = ImageTk.PhotoImage(image=img)
                self.canvas.img_tk = img_tk
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                
            self.window.after(self.delay, self.update_stream_loop)

        def __del__(self):
            if self.cap.isOpened():
                self.cap.release()

    VisionStudioContinuous(tk.Tk(), "Live Vision Studio Workspace v4.6")