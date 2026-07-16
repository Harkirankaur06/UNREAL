import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import random
import math

# --- GAME CONFIGURATION ---
ROWS = 3              # 3x3 grid
COLS = 3
PINCH_THRESHOLD = 35  # Max distance between thumb & index to register a pinch

class Tile:
    def __init__(self, correct_id):
        self.correct_id = correct_id  # The slice's original index (0 to 8)
        self.current_id = correct_id  # Where it is currently positioned on the grid

# Initialize tracker and webcam
detector = HandDetector(detectionCon=0.7, maxHands=1)
cap = cv2.VideoCapture(0)

# Set camera resolution (standard 640x480 works best for performance)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Game State Setup
grid_initialized = False
tiles = []            # To track our logical tile layout
scrambled_mapping = [] # Maps grid_position -> correct_slice_id
selected_index = None # Keeps track of the first tile selected for swapping
game_won = False

def scramble_grid(r, c):
    """Generates a shuffled list of indices, ensuring it doesn't start already solved."""
    indices = list(range(r * c))
    while True:
        random.shuffle(indices)
        # Avoid generating a pre-solved puzzle
        if indices != list(range(r * c)):
            return indices

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1) # Mirror feed
    h_frame, w_frame, _ = frame.shape
    
    # Calculate dimensions for each tile dynamically based on camera resolution
    tile_w = w_frame // COLS
    tile_h = h_frame // ROWS

    # 1. INITIALIZE GRID ONCE
    if not grid_initialized:
        scrambled_mapping = scramble_grid(ROWS, COLS)
        for i in range(ROWS * COLS):
            tile = Tile(correct_id=i)
            # Assign it its starting scrambled position
            tile.current_id = scrambled_mapping[i]
            tiles.append(tile)
        grid_initialized = True

    # Capture the active (unscrambled) camera frame to slice up
    live_frame = frame.copy()

    # Detect Hand Gestures
    hands, frame = detector.findHands(frame, draw=True)
    cursor_pos = None
    is_pinching = False

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        ix, iy = lmList[8][0], lmList[8][1]  # Index finger tip
        tx, ty = lmList[4][0], lmList[4][1]  # Thumb tip
        
        cursor_pos = (ix, iy)
        distance = math.hypot(tx - ix, ty - iy)
        
        if distance < PINCH_THRESHOLD:
            is_pinching = True
            cv2.circle(frame, cursor_pos, 15, (0, 255, 0), cv2.FILLED)
        else:
            cv2.circle(frame, cursor_pos, 10, (0, 0, 255), cv2.FILLED)

    # 2. DETERMINE HOVERED TILE INDEX
    hovered_index = None
    if cursor_pos:
        cx, cy = cursor_pos
        # Math to find which grid coordinate (col, row) the cursor is in
        col = min(cx // tile_w, COLS - 1)
        row = min(cy // tile_h, ROWS - 1)
        hovered_index = row * COLS + col

    # 3. SWAP LOGIC (STATE MACHINE)
    if not game_won and hovered_index is not None:
        if is_pinching:
            # If nothing is selected yet, select the hovered tile
            if selected_index is None:
                selected_index = hovered_index
        else:
            # If we released our pinch over a DIFFERENT tile, perform the swap!
            if selected_index is not None:
                if selected_index != hovered_index:
                    # Find the two tiles in our list and swap their screen positions
                    tile_a = next(t for t in tiles if t.current_id == selected_index)
                    tile_b = next(t for t in tiles if t.current_id == hovered_index)
                    
                    # Swap current positions
                    tile_a.current_id, tile_b.current_id = tile_b.current_id, tile_a.current_id
                
                # Reset selection
                selected_index = None

    # 4. DRAW THE SCRAMBLED CAMERA FEED
    # We construct the visual frame by cutting pieces out of 'live_frame' 
    # and pasting them into 'frame' based on their scrambled positions.
    for tile in tiles:
        # Where the slice belongs on the live video feed
        src_row = tile.correct_id // COLS
        src_col = tile.correct_id % COLS
        src_y = src_row * tile_h
        src_x = src_col * tile_w
        
        # Crop the slice from the current raw camera frame
        slice_img = live_frame[src_y : src_y + tile_h, src_x : src_x + tile_w]
        
        # Where it needs to be drawn on the active scrambled screen
        dest_row = tile.current_id // COLS
        dest_col = tile.current_id % COLS
        dest_y = dest_row * tile_h
        dest_x = dest_col * tile_w
        
        # Overwrite that section of the display frame
        frame[dest_y : dest_y + tile_h, dest_x : dest_x + tile_w] = slice_img
        
        # Draw grid borders
        border_color = (100, 100, 100) # Subtle gray border
        cv2.rectangle(frame, (dest_x, dest_y), (dest_x + tile_w, dest_y + tile_h), border_color, 1)

    # 5. DRAW INTERACTION HIGHLIGHTS
    # Highlight the selected tile (Yellow border)
    if selected_index is not None:
        sel_row = selected_index // COLS
        sel_col = selected_index % COLS
        cv2.rectangle(frame, (sel_col * tile_w, sel_row * tile_h), 
                      ((sel_col + 1) * tile_w, (sel_row + 1) * tile_h), (0, 255, 255), 4)
                      
    # Highlight the currently hovered tile when dragging/preparing to swap (Blue border)
    if hovered_index is not None and hovered_index != selected_index and not game_won:
        hov_row = hovered_index // COLS
        hov_col = hovered_index % COLS
        cv2.rectangle(frame, (hov_col * tile_w, hov_row * tile_h), 
                      ((hov_col + 1) * tile_w, (hov_row + 1) * tile_h), (255, 0, 0), 2)

    # 6. WIN CONDITION CHECK
    # If every tile's current grid position is equal to its correct ID
    if all(t.current_id == t.correct_id for t in tiles):
        game_won = True

    # UI Text Overlays
    if game_won:
        # Draw a semi-transparent dark overlay for the winning screen
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w_frame, h_frame), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        cv2.putText(frame, "PUZZLE SOLVED!", (w_frame // 2 - 180, h_frame // 2), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 0), 3)
        cv2.putText(frame, "Press 'r' to restart or 'q' to quit", (w_frame // 2 - 200, h_frame // 2 + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    else:
        cv2.putText(frame, "Pinch to select, Release on another tile to swap!", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Keyboard Controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'): # Restart / Rescramble
        scrambled_mapping = scramble_grid(ROWS, COLS)
        for i, tile in enumerate(tiles):
            tile.current_id = scrambled_mapping[i]
        game_won = False

    cv2.imshow("Live Cam Swap Puzzle", frame)

cap.release()
cv2.destroyAllWindows()