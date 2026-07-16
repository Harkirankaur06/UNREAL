import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import random
import math

# --- CONFIG ---
GRID_SIZE = 2
PUZZLE_WIDTH = 300
PUZZLE_HEIGHT = 300
PINCH_THRESHOLD = 30  # Adjust if tracking is too loose/tight

class PuzzlePiece:
    def __init__(self, img, correct_pos, current_pos, size):
        self.img = img
        self.correct_pos = correct_pos
        self.current_pos = list(current_pos)
        self.size = size
        self.is_locked = False

    def is_hovered(self, x, y):
        px, py = self.current_pos
        w, h = self.size
        return px <= x <= px + w and py <= y <= py + h

# Use CVZone's simpler tracker instead of pure MediaPipe
detector = HandDetector(detectionCon=0.7, maxHands=1)
cap = cv2.VideoCapture(0)

puzzle_initialized = False
pieces = []
selected_piece = None
board_pos = (50, 100)
game_won = False

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h_frame, w_frame, _ = frame.shape
    
    # Init Puzzle pieces (Slicing the image)
    if not puzzle_initialized:
        crop_size = min(h_frame, w_frame) // 2
        cy, cx = h_frame // 2, w_frame // 2
        cropped_base = frame[cy - crop_size//2 : cy + crop_size//2, cx - crop_size//2 : cx + crop_size//2]
        puzzle_image = cv2.resize(cropped_base, (PUZZLE_WIDTH, PUZZLE_HEIGHT))
        
        piece_w = PUZZLE_WIDTH // GRID_SIZE
        piece_h = PUZZLE_HEIGHT // GRID_SIZE
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                src_x = c * piece_w
                src_y = r * piece_h
                slice_img = puzzle_image[src_y : src_y + piece_h, src_x : src_x + piece_w]
                correct_x = board_pos[0] + src_x
                correct_y = board_pos[1] + src_y
                random_x = random.randint(w_frame // 2 + 50, w_frame - piece_w - 50)
                random_y = random.randint(100, h_frame - piece_h - 100)
                
                pieces.append(PuzzlePiece(slice_img, (correct_x, correct_y), (random_x, random_y), (piece_w, piece_h)))
        puzzle_initialized = True

    # Detect hand
    hands, frame = detector.findHands(frame)
    
    cursor_pos = None
    is_pinching = False

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 Landmark points
        
        # Landmark 8 is Index tip, Landmark 4 is Thumb tip
        ix, iy = lmList[8][0], lmList[8][1]
        tx, ty = lmList[4][0], lmList[4][1]
        
        cursor_pos = (ix, iy)
        
        # Calculate distance between index and thumb
        distance = math.hypot(tx - ix, ty - iy)
        
        if distance < PINCH_THRESHOLD:
            is_pinching = True
            cv2.circle(frame, cursor_pos, 15, (0, 255, 0), cv2.FILLED)
        else:
            is_pinching = False
            cv2.circle(frame, cursor_pos, 10, (0, 0, 255), cv2.FILLED)

    # Gameplay Interaction
    if cursor_pos:
        cx, cy = cursor_pos
        if is_pinching:
            if selected_piece is None:
                for p in reversed(pieces):
                    if not p.is_locked and p.is_hovered(cx, cy):
                        selected_piece = p
                        break
            if selected_piece:
                selected_piece.current_pos[0] = cx - selected_piece.size[0] // 2
                selected_piece.current_pos[1] = cy - selected_piece.size[1] // 2
        else:
            if selected_piece:
                px, py = selected_piece.current_pos
                tx, ty = selected_piece.correct_pos
                snap_distance = math.hypot(px - tx, py - ty)
                
                if snap_distance < 30:
                    selected_piece.current_pos = list(selected_piece.correct_pos)
                    selected_piece.is_locked = True
                selected_piece = None

    # Render board outline
    cv2.rectangle(frame, board_pos, (board_pos[0] + PUZZLE_WIDTH, board_pos[1] + PUZZLE_HEIGHT), (255, 255, 255), 2)
    cv2.putText(frame, "TARGET BOARD", (board_pos[0], board_pos[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Draw puzzle pieces
    for p in pieces:
        px, py = int(p.current_pos[0]), int(p.current_pos[1])
        w, h = p.size
        frame[py : py + h, px : px + w] = p.img
        border_color = (0, 255, 0) if p.is_locked else (255, 255, 0)
        cv2.rectangle(frame, (px, py), (px + w, py + h), border_color, 1)

    if all(p.is_locked for p in pieces):
        game_won = True

    if game_won:
        cv2.putText(frame, "YOU SOLVED IT!", (w_frame // 2 - 150, 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 3)
    else:
        cv2.putText(frame, "Pinch to Move pieces!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Air Jigsaw Puzzle", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()