import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

class UnrealLevitationApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#121212") # Premium dark mode background
        
        self.cap = cv2.VideoCapture(0)
        
        # State Variables
        self.tracker = None
        self.is_tracking = False
        self.is_levitating = False
        self.bbox = None
        self.float_y = 0
        self.target_hover_height = -90 # Hover offset in pixels
        
        # --- UI LAYOUT CONFIGURATION ---
        # Top Header
        self.header = tk.Label(window, text="UNREAL // COGNITIVE ELEVATION SYSTEM", 
                               fg="#00E5FF", bg="#121212", font=("Courier", 14, "bold"))
        self.header.pack(pady=10)
        
        # Main Video Canvas Stream
        self.canvas = tk.Canvas(window, width=640, height=480, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Button Dashboard Frame
        self.btn_frame = tk.Frame(window, bg="#121212")
        self.btn_frame.pack(pady=15)
        
        # Styled Dark-Mode Buttons
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Helvetica', 10, 'bold'), foreground='#ffffff', background='#333333', borderwidth=0)
        style.map('TButton', background=[('active', '#00E5FF')], foreground=[('active', '#121212')])
        
        self.btn_select = ttk.Button(self.btn_frame, text="1. SELECT OBJECT", command=self.start_roi_selection)
        self.btn_select.grid(row=0, column=0, padx=10)
        
        self.btn_hover = ttk.Button(self.btn_frame, text="2. TRIGGER HOVER", command=self.toggle_hover)
        self.btn_hover.grid(row=0, column=1, padx=10)
        
        self.btn_reset = ttk.Button(self.btn_frame, text="RESET MATRIX", command=self.reset_system)
        self.btn_reset.grid(row=0, column=2, padx=10)
        
        # Status Bar Footer
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM STATUS: LIVE_VIEWPORT_READY")
        self.status_label = tk.Label(window, textvariable=self.status_var, fg="#ffffff", bg="#1a1a1a", font=("Helvetica", 9), width=80, anchor="w", padx=10)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Start the Background Camera Thread Processing loop
        self.delay = 15
        self.update_frame()
        self.window.mainloop()

    def start_roi_selection(self):
        """Launches a live selection framework anywhere on screen"""
        self.status_var.set("SYSTEM STATUS: DRAW BOX AROUND THE TARGET OBJECT IN THE POPUP WINDOW")
        
        # Read current live frame to select target
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            # OpenCV selectROI allows mouse drag selection anywhere on the screen layout
            roi_bbox = cv2.selectROI("TARGET CORE LOCK-ON", frame, fromCenter=False, showCrosshair=False)
            cv2.destroyWindow("TARGET CORE LOCK-ON")
            
            if roi_bbox[2] > 10 and roi_bbox[3] > 10:
                self.bbox = roi_bbox
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, self.bbox)
                self.is_tracking = True
                self.status_var.set("SYSTEM STATUS: OBJECT LOCKED & TRACKING LIVE // PRESS TRIGGER HOVER")

    def toggle_hover(self):
        """Toggles the dynamic altitude tracking engine"""
        if self.is_tracking:
            self.is_levitating = True
            self.status_var.set("SYSTEM STATUS: ALTERNATE MATERIALIZATION LAYER ACTIVE")

    def reset_system(self):
        """Clears all matrix structures back to baseline preview"""
        self.tracker = None
        self.is_tracking = False
        self.is_levitating = False
        self.bbox = None
        self.float_y = 0
        self.status_var.set("SYSTEM STATUS: RESET COMPLETED // LIVE_VIEWPORT_READY")

    def update_frame(self):
        """Main rendering engine processing pipeline"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            display_frame = frame.copy()
            
            # 1. AI RECOGNITION ENGINE TRACKING ACTIVE
            if self.is_tracking and self.tracker is not None:
                track_success, box = self.tracker.update(frame)
                
                if track_success:
                    ox, oy, ow, oh = [int(v) for v in box]
                    
                    # RENDER THE REAL OBJECT: Keep drawing the cyber frame on the real moving item
                    cv2.rectangle(display_frame, (ox, oy), (ox+ow, oy+oh), (0, 255, 255), 1, cv2.LINE_AA)
                    cv2.drawMarker(display_frame, (ox + int(ow/2), oy + int(oh/2)), (0, 255, 255), cv2.MARKER_CROSS, 8, 1, cv2.LINE_AA)
                    
                    # 2. HOVER GENERATOR ACTIVATED
                    if self.is_levitating:
                        # Smooth hover interpolation calculation
                        if self.float_y > self.target_hover_height:
                            self.float_y -= 4
                        
                        # Calculate exact dynamic floating offset relative to the object's real-time position
                        current_y = oy + self.float_y
                        
                        if current_y > 10 and (current_y + oh) < h:
                            # Safely slice and isolate the texture of the live object
                            object_texture = frame[oy:oy+oh, ox:ox+ow].copy()
                            
                            # Render the replica tracking floating perfectly a few inches above the real moving object!
                            display_frame[current_y:current_y+oh, ox:ox+ow] = object_texture
                            
                            # Minimal cyan stasis stabilization accent bar under the floating artifact
                            cv2.line(display_frame, (ox, current_y + oh + 4), (ox + ow, current_y + oh + 4), (0, 255, 255), 2, cv2.LINE_AA)
                else:
                    self.status_var.set("SYSTEM STATUS: TRACKING LOST // PLEASE RESET")

            # Convert OpenCV BGR Image frame to Tkinter Compatible Canvas Layer
            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            
            self.canvas.img_tk = img_tk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            
        self.window.after(self.delay, self.update_frame)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

# Launch the Application Sandbox
if __name__ == "__main__":
    UnrealLevitationApp(tk.Tk(), "UNREAL Engine - Day 1 Studio Workspace")