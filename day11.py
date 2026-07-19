import cv2
import numpy as np
import mediapipe as mp
import time
import random

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

cap = cv2.VideoCapture(0)

# Landmark indexes for specific facial features to draw glowing tech overlays onto
FOREHEAD = [54, 103, 67, 109, 10, 338, 297, 332, 284]
LEFT_EYE_CIRCUIT = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # 1. CYBERPUNK COLOR GRADE (Shift toward deep blue shadow and high neon saturation)
    # Split channels to enhance color contrast manually
    b, g, r = cv2.split(frame)
    b = cv2.addWeighted(b, 1.2, np.zeros_like(b), 0, 10)  # Boost cold tones
    r = cv2.addWeighted(r, 0.9, np.zeros_like(r), 0, 0)   # Tone down standard red skin tones
    graded_frame = cv2.merge([b, g, r])
    
    # 2. CHROMATIC ABERRATION VIDEO GLITCH
    # Every few frames, simulate a tracking glitch by misaligning color channels
    if random.random() > 0.92: 
        glitch_shift = random.randint(4, 12)
        # Shift channels laterally to produce colored fringes
        chroma_b = np.roll(b, glitch_shift, axis=1)
        chroma_r = np.roll(r, -glitch_shift, axis=1)
        graded_frame = cv2.merge([chroma_b, g, chroma_r])
        
        # Draw random blocky digital artifacts across the frame
        for _ in range(3):
            y_start = random.randint(0, h-30)
            x_start = random.randint(0, w-100)
            graded_frame[y_start:y_start+20, x_start:x_start+80] = np.roll(
                graded_frame[y_start:y_start+20, x_start:x_start+80], 
                random.randint(-40, 40), axis=1
            )

    # Process face geometry mapping
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Helper logic to extract absolute pixel coordinates from structural landmarks
            def get_pt(idx):
                lm = face_landmarks.landmark[idx]
                return int(lm.x * w), int(lm.y * h)
            
            # 3. DRAW GLOWING HUD CIRCUITS
            # Draw glowing data line across forehead
            for i in range(len(FOREHEAD)-1):
                cv2.line(graded_frame, get_pt(FOREHEAD[i]), get_pt(FOREHEAD[i+1]), (255, 0, 255), 2, cv2.LINE_AA) # Neon Pink
                cv2.circle(graded_frame, get_pt(FOREHEAD[i]), 3, (0, 255, 255), -1) # Cyber Yellow nodes
                
            # Draw technical circle rings around the eye socket
            eye_pts = np.array([get_pt(idx) for idx in LEFT_EYE_CIRCUIT], np.int32)
            cv2.polylines(graded_frame, [eye_pts], True, (0, 255, 255), 1, cv2.LINE_AA)
            
            # Target crosshair tracking over the eye center
            left_eye_center = get_pt(159) 
            cv2.drawMarker(graded_frame, left_eye_center, (0, 255, 0), cv2.MARKER_CROSS, 25, 1)
            
            # Dynamic text readouts simulating software scanning target
            cv2.putText(graded_frame, f"NET_ID: 0x{id(face_landmarks)%10000:04X}", (left_eye_center[0]+20, left_eye_center[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(graded_frame, "SYSTEM: LINK_ESTABLISHED", (20, 40), 
                        cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        # Fallback system notification when face isn't detected
        cv2.putText(graded_frame, "SYSTEM: SEARCHING_FOR_HOST...", (20, 40), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.6, (0, 0, 255), 1, cv2.LINE_AA)

    cv2.imshow('Netrunner AR Interface', graded_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()