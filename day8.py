import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import random
import math

ROWS = 3              
COLS = 3
PINCH_THRESHOLD = 35  

class Tile:
    def __init__(self, correct_id):
        self.correct_id = correct_id  
        self.current_id = correct_id  

# State tracking persistence registers across frame calls
detector = None
grid_initialized = False
tiles = []            
scrambled_mapping = [] 
selected_index = None 
game_won = False

def scramble_grid(r, c):
    indices = list(range(r * c))
    while True:
        random.shuffle(indices)
        if indices != list(range(r * c)):
            return indices

# ====================================================================
# STREAMLIT COMPATIBILITY HOOK (DO NOT TOUCH ORIGINAL LOGIC)
# ====================================================================
def process_frame(incoming_frame):
    global detector, grid_initialized, tiles, scrambled_mapping, selected_index, game_won
    
    if detector is None:
        detector = HandDetector(detectionCon=0.7, maxHands=1)
        
    frame = cv2.flip(incoming_frame, 1) 
    h_frame, w_frame, _ = frame.shape
    
    tile_w = w_frame // COLS
    tile_h = h_frame // ROWS

    if not grid_initialized:
        scrambled_mapping = scramble_grid(ROWS, COLS)
        for i in range(ROWS * COLS):
            tile = Tile(correct_id=i)
            tile.current_id = scrambled_mapping[i]
            tiles.append(tile)
        grid_initialized = True

    live_frame = frame.copy()
    hands, frame = detector.findHands(frame, draw=True)
    cursor_pos = None
    is_pinching = False

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        ix, iy = lmList[8][0], lmList[8][1]  
        tx, ty = lmList[4][0], lmList[4][1]  
        
        cursor_pos = (ix, iy)
        distance = math.hypot(tx - ix, ty - iy)
        
        if distance < PINCH_THRESHOLD:
            is_pinching = True
            cv2.circle(frame, cursor_pos, 15, (0, 255, 0), cv2.FILLED)
        else:
            cv2.circle(frame, cursor_pos, 10, (0, 0, 255), cv2.FILLED)

    hovered_index = None
    if cursor_pos:
        cx, cy = cursor_pos
        col = min(cx // tile_w, COLS - 1)
        row = min(cy // tile_h, ROWS - 1)
        hovered_index = row * COLS + col

    if not game_won and hovered_index is not None:
        if is_pinching:
            if selected_index is None:
                selected_index = hovered_index
        else:
            if selected_index is not None:
                if selected_index != hovered_index:
                    tile_a = next(t for t in tiles if t.current_id == selected_index)
                    tile_b = next(t for t in tiles if t.current_id == hovered_index)
                    tile_a.current_id, tile_b.current_id = tile_b.current_id, tile_a.current_id
                selected_index = None

    for tile in tiles:
        src_row = tile.correct_id // COLS
        src_col = tile.correct_id % COLS
        src_y = src_row * tile_h
        src_x = src_col * tile_w
        
        slice_img = live_frame[src_y : src_y + tile_h, src_x : src_x + tile_w]
        
        dest_row = tile.current_id // COLS
        dest_col = tile.current_id % COLS
        dest_y = dest_row * tile_h
        dest_x = dest_col * tile_w
        
        frame[dest_y : dest_y + tile_h, dest_x : dest_x + tile_w] = slice_img
        cv2.rectangle(frame, (dest_x, dest_y), (dest_x + tile_w, dest_y + tile_h), (100, 100, 100), 1)

    if selected_index is not None:
        sel_row = selected_index // COLS
        sel_col = selected_index % COLS
        cv2.rectangle(frame, (sel_col * tile_w, sel_row * tile_h), 
                      ((sel_col + 1) * tile_w, (sel_row + 1) * tile_h), (0, 255, 255), 4)
                      
    if hovered_index is not None and hovered_index != selected_index and not game_won:
        hov_row = hovered_index // COLS
        hov_col = hovered_index % COLS
        cv2.rectangle(frame, (hov_col * tile_w, hov_row * tile_h), 
                      ((hov_col + 1) * tile_w, (hov_row + 1) * tile_h), (255, 0, 0), 2)

    if all(t.current_id == t.correct_id for t in tiles):
        game_won = True

    if game_won:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w_frame, h_frame), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        cv2.putText(frame, "PUZZLE SOLVED!", (w_frame // 2 - 180, h_frame // 2), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 0), 3)
        cv2.putText(frame, "Press key 'r' to reset simulation setup parameters", (w_frame // 2 - 200, h_frame // 2 + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    else:
        cv2.putText(frame, "Pinch to select, Release on another tile to swap!", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return frame

# Local script fallback window execution guard
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while cap.isOpened():
        success, img_frame = cap.read()
        if not success: break
        output = process_frame(img_frame)
        cv2.imshow("Live Cam Swap Puzzle", output)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('r'):
            scrambled_mapping = scramble_grid(ROWS, COLS)
            for i, tile in enumerate(tiles):
                tile.current_id = scrambled_mapping[i]
            game_won = False
    cap.release()
    cv2.destroyAllWindows()