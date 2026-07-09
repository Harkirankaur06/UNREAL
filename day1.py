import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class UnrealStudioApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#0C0C0E") 
        
        self.cap = cv2.VideoCapture(0)
        
        # Core State Variables
        self.tracker = None
        self.is_tracking = False
        self.is_levitating = False
        self.bbox = None
        self.float_y = 0
        self.target_hover_height = -90 
        
        # Precise Mask Cutout Data Cache
        self.mask_crop = None
        self.object_crop = None
        self.full_frame_mask = None

        # --- UI VIEWPORT LAYOUT ---
        self.header = tk.Label(window, text="UNREAL // SILHOUETTE INVERSION ENGINE", 
                               fg="#00E5FF", bg="#0C0C0E", font=("Courier", 14, "bold"))
        self.header.pack(pady=10)
        
        self.canvas = tk.Canvas(window, width=640, height=480, bg="#111115", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        self.btn_frame = tk.Frame(window, bg="#0C0C0E")
        self.btn_frame.pack(pady=15)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#1E1E24', borderwidth=0)
        style.map('TButton', background=[('active', '#00E5FF')], foreground=[('active', '#0C0C0E')])
        
        self.btn_select = ttk.Button(self.btn_frame, text="1. SELECT OBJECT", command=self.process_silhouette)
        self.btn_select.grid(row=0, column=0, padx=12)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. LAUNCH HOVER", command=self.activate_hover)
        self.btn_hover.grid(row=0, column=1, padx=12)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET SYSTEM", command=self.reset_workspace)
        self.btn_reset.grid(row=0, column=2, padx=12)
        
        self.status_var = tk.StringVar()
        self.status_var.set("CONSOLE // PORTAL STREAM STABLE. CHOOSE AN ACTION.")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#A0A0AA", bg="#111115", font=("Courier", 9), width=85, anchor="w", padx=12, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.delay = 15
        self.update_stream()
        self.window.mainloop()

    def process_silhouette(self):
        """Captures frame live, lets user select, and runs GrabCut boundary isolation"""
        self.status_var.set("CONSOLE // DRAW BOX BOUNDARY AROUND TARGET ON THE LIVE FRAME POPUP")
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            roi_bbox = cv2.selectROI("UNREAL // TARGET CAPTURE", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("UNREAL // TARGET CAPTURE")
            
            ox, oy, ow, oh = [int(v) for v in roi_bbox]
            
            if ow > 15 and oh > 15:
                self.bbox = (ox, oy, ow, oh)
                
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                gc_mask = np.zeros(frame.shape[:2], np.uint8)
                
                cv2.grabCut(frame, gc_mask, self.bbox, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                
                self.full_frame_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 1).astype('uint8') * 255
                self.full_frame_mask = cv2.morphologyEx(self.full_frame_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
                
                isolated_texture = cv2.bitwise_and(frame, frame, mask=self.full_frame_mask)
                self.object_crop = isolated_texture[oy:oy+oh, ox:ox+ow]
                self.mask_crop = self.full_frame_mask[oy:oy+oh, ox:ox+ow]
                
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, self.bbox)
                self.is_tracking = True
                self.status_var.set("CONSOLE // OBJECT BOUNDARIES MAP GENERATED SUCCESSFULLY. READY FOR HOVER.")

    def activate_hover(self):
        if self.is_tracking:
            self.is_levitating = True
            self.status_var.set("CONSOLE // MATRIX SPLIT COMPLETE. DYNAMIC INPAINT MODIFIER ENGAGED.")

    def reset_workspace(self):
        self.tracker = None
        self.is_tracking = False
        self.is_levitating = False
        self.bbox = None
        self.float_y = 0
        self.mask_crop = None
        self.object_crop = None
        self.full_frame_mask = None
        self.status_var.set("CONSOLE // WORKSPACE TERMINATED. SYSTEM RELOAD COMPLETED.")

    def update_stream(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # --- HUD VIEWPORT OVERLAYS ---
            bl = 20
            cv2.line(display_frame, (30, 30), (30 + bl, 30), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (30, 30), (30, 30 + bl), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (w - 30, 30), (w - 30 - bl, 30), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(display_frame, (w - 30, 30), (w - 30, 30 + bl), (255, 255, 255), 1, cv2.LINE_AA)
            
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(display_frame, (45, 52), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.putText(display_frame, "LIVE_VIEWFEED", (60, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

            # --- ENGINE PROCESSING CORE ---
            if self.is_tracking and self.tracker is not None:
                track_success, box = self.tracker.update(frame)
                
                if track_success:
                    ox, oy, ow, oh = [int(v) for v in box]
                    
                    # Prevent zero-size layout tracking crashes
                    if ow > 5 and oh > 5 and ox >= 0 and oy >= 0 and (ox + ow) <= w and (oy + oh) <= h:
                        
                        # CRITICAL FIX: Dynamically match template arrays to the exact live window tracking bounds
                        live_mask_crop = cv2.resize(self.mask_crop, (ow, oh))
                        live_object_crop = cv2.resize(self.object_crop, (ow, oh))
                        
                        if self.is_levitating:
                            # 1. Real-time background pixel-repair mask
                            active_mask = np.zeros(frame.shape[:2], np.uint8)
                            active_mask[oy:oy+oh, ox:ox+ow] = live_mask_crop
                            
                            display_frame = cv2.inpaint(frame, active_mask, 5, cv2.INPAINT_TELEA)
                            
                            # 2. Translate Floating Layer Coordinates
                            if self.float_y > self.target_hover_height:
                                self.float_y -= 4
                                
                            current_y = oy + self.float_y
                            
                            # Ensure the float layer fits safely inside screen limits
                            if current_y > 5 and (current_y + oh) < h:
                                roi = display_frame[current_y:current_y+oh, ox:ox+ow]
                                
                                # Perform operations on matching dimensions safely
                                img_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(live_mask_crop))
                                img_fg = cv2.bitwise_and(live_object_crop, live_object_crop, mask=live_mask_crop)
                                
                                display_frame[current_y:current_y+oh, ox:ox+ow] = cv2.add(img_bg, img_fg)
                                cv2.line(display_frame, (ox, current_y + oh + 4), (ox + ow, current_y + oh + 4), (0, 229, 255), 2, cv2.LINE_AA)
                        else:
                            # Pre-hover mode: Render clean green tracking contours onto the screen layout
                            cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    self.status_var.set("CONSOLE // TRACKING GEOMETRY DETACHED. PRESS RESET WORKSPACE.")

            # Map array details directly over the Tkinter canvas setup
            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            
            self.canvas.img_tk = img_tk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            
        self.window.after(self.delay, self.update_stream)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    UnrealStudioApp(tk.Tk(), "UNREAL Engine Studio Workspace v2.0")