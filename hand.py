import cv2
import mediapipe as mp
import pyautogui
import time
import os
import subprocess

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()
cap = cv2.VideoCapture(0)

box_width_ratio = 0.9
box_height_ratio = 0.9
padding = 40
smoothing_factor = 0
scroll_speed = 10
volume_change_step = 2
volume_change_speed = 0.2

prev_x, prev_y = 0, 0
movement_threshold = 10
last_volume_change_time = 0

# Path of the Python file in the same directory
python_file_name = "Voice.py"  # Name of your Python file
python_file_path = os.path.join(os.getcwd(), python_file_name)

# Flag to indicate if the script is currently running
script_running = False

def set_smoothing_factor(value):
    global smoothing_factor
    smoothing_factor = value

def set_padding(value):
    global padding
    padding = value

def set_scroll_speed(value):
    global scroll_speed
    scroll_speed = value

def set_volume_change_step(value):
    global volume_change_step
    volume_change_step = value

def set_volume_change_speed(value):
    global volume_change_speed
    volume_change_speed = value

# Helper function to count extended fingers
def count_fingers(hand_landmarks):
    fingers_up = []
    landmarks = hand_landmarks.landmark

    # Thumb (special case: we look at the x-position difference with wrist for left-to-right motion)
    if landmarks[mp_hands.HandLandmark.THUMB_TIP].x > landmarks[mp_hands.HandLandmark.THUMB_IP].x:
        fingers_up.append(True)  # Thumb up
    else:
        fingers_up.append(False)  # Thumb down or retracted

    # Check each finger (index, middle, ring, pinky)
    for finger_tip, finger_dip in [(mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_DIP),
                                   (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP),
                                   (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_DIP),
                                   (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_DIP)]:
        if landmarks[finger_tip].y < landmarks[finger_dip].y:
            fingers_up.append(True)  # Finger extended
        else:
            fingers_up.append(False)  # Finger curled

    return fingers_up

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read from webcam.")
        break

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    box_top_left_x = int(frame_width * (1 - box_width_ratio) / 2)
    box_top_left_y = int(frame_height * (1 - box_height_ratio) / 2)
    box_bottom_right_x = int(frame_width * (1 + box_width_ratio) / 2)
    box_bottom_right_y = int(frame_height * (1 + box_height_ratio) / 2)
    
    padded_box_top_left_x = box_top_left_x + padding
    padded_box_top_left_y = box_top_left_y + padding
    padded_box_bottom_right_x = box_bottom_right_x - padding
    padded_box_bottom_right_y = box_bottom_right_y - padding
    
    cv2.rectangle(frame, (box_top_left_x, box_top_left_y), (box_bottom_right_x, box_bottom_right_y), (255, 0, 0), 2)
    cv2.rectangle(frame, (padded_box_top_left_x, padded_box_top_left_y), (padded_box_bottom_right_x, padded_box_bottom_right_y), (0, 255, 0), 2)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            finger_x = int(index_finger_tip.x * frame_width)
            finger_y = int(index_finger_tip.y * frame_height)

            if (padded_box_top_left_x < finger_x < padded_box_bottom_right_x and padded_box_top_left_y < finger_y < padded_box_bottom_right_y):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                relative_x = finger_x - padded_box_top_left_x
                relative_y = finger_y - padded_box_top_left_y
                box_width = padded_box_bottom_right_x - padded_box_top_left_x
                box_height = padded_box_bottom_right_y - padded_box_top_left_y
                screen_x = int((relative_x / box_width) * screen_width)
                screen_y = int((relative_y / box_height) * screen_height)
                movement_x = abs(screen_x - prev_x)
                movement_y = abs(screen_y - prev_y)

                fingers_up = count_fingers(hand_landmarks)
                extended_fingers = fingers_up.count(True)

                # Scrolling gestures
                if extended_fingers == 2 and fingers_up[1] and fingers_up[2]:
                    pyautogui.scroll(-scroll_speed)
                    cv2.putText(frame, 'Scrolling Down', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif extended_fingers == 3 and fingers_up[1] and fingers_up[2] and fingers_up[3]:
                    pyautogui.scroll(scroll_speed)
                    cv2.putText(frame, 'Scrolling Up', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Thumbs up (volume up) and thumbs down (volume down)
                current_time = time.time()
                if current_time - last_volume_change_time > volume_change_speed:
                    if fingers_up[0] and not any(fingers_up[1:]):  # Only thumb is up
                        pyautogui.press("volumedown")
                        cv2.putText(frame, 'Volume down (Thumbs down)', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        last_volume_change_time = current_time
                    elif not fingers_up[0] and all(fingers_up[1:]):  # Only thumb is down
                        pyautogui.press("volumeup")
                        cv2.putText(frame, 'Volume (Thumbs up)', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        last_volume_change_time = current_time

                # 5-finger gesture to run the Python script
                if extended_fingers == 5:
                    if not script_running:  # Check if the script is already running
                        script_running = True
                        subprocess.Popen(["python", python_file_path], shell=True)
                        cv2.putText(frame, 'Running Python Script (5 Fingers)', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    else:
                        cv2.putText(frame, 'Script Already Running', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                if movement_x > movement_threshold or movement_y > movement_threshold:
                    if smoothing_factor > 0:
                        cursor_x = prev_x + (screen_x - prev_x) // smoothing_factor
                        cursor_y = prev_y + (screen_y - prev_y) // smoothing_factor
                    else:
                        cursor_x = screen_x
                        cursor_y = screen_y
                    pyautogui.moveTo(cursor_x, cursor_y)
                    prev_x, prev_y = cursor_x, cursor_y
                else:
                    cv2.putText(frame, 'Hand is Stationary', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.circle(frame, (finger_x, finger_y), 10, (0, 255, 0), -1)
                cv2.putText(frame, 'Moving Cursor', (finger_x + 20, finger_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            else:
                cv2.putText(frame, 'Move Hand Inside the Padded Box', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Hand Controlled Mouse with Padded Box', frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
