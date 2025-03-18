import cv2
import mediapipe as mp
from virtual_arduino import VirtualArduino
import socketio  # Import socketio for WebSocket communication

# Initialize WebSocket client
sio = socketio.Client()
sio.connect("http://127.0.0.1:5000")  # Ensure the iot_server is running first

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Initialize Virtual Arduino
arduino = VirtualArduino()
prev_led_state = None  # Track previous LED state

# Capture video from webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the image horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Detect gestures and update the virtual Arduino
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the coordinates of the thumb and index finger
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Detect a "swipe right" gesture to turn on the LED
            if thumb_tip.x < index_tip.x:
                new_led_state = True
            # Detect a "swipe left" gesture to turn off the LED
            elif thumb_tip.x > index_tip.x:
                new_led_state = False
            else:
                continue

            # Only update if the LED state has changed
            if new_led_state != prev_led_state:
                if new_led_state:
                    arduino.turn_on_led()
                else:
                    arduino.turn_off_led()

                # Send WebSocket update to the server
                sio.emit('led_state', {'state': new_led_state})
                prev_led_state = new_led_state  # Update the previous state

    # Display the frame
    cv2.imshow('Gesture Recognition', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
sio.disconnect()  # Disconnect WebSocket
