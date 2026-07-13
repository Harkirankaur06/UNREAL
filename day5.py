import cv2

# Initialize webcam (0 is usually the default built-in camera)
cap = cv2.VideoCapture(0)

print("Press 'q' to exit the thermal vision mode.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Step 1: Flip frame horizontally for a mirror effect (optional but nice)
    frame = cv2.flip(frame, 1)

    # Step 2: Convert to grayscale (thermal maps require a 1-channel input)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply the colormap. JET or INFERNO work best for heat signatures
    thermal_frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    # Display the result
    cv2.imshow('Day 5: Thermal Vision Challenge', thermal_frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()