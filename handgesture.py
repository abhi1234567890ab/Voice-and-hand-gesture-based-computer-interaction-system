import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import pygetwindow as gw

# Initialize MediaPipe Hands & Face Mesh
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Capture video
cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
prev_x, prev_y = None, None
message, message_time = "", 0
cooldown_time, last_swipe_time = 0.8, time.time()
blink_threshold = 0.2

# Double Blink Detection
last_blink_time = 0
blink_count = 0

def is_browser_open():
    try:
        active_window = gw.getActiveWindow().title.lower()
        return any(word in active_window for word in ["chrome", "firefox", "edge"])
    except:
        return False

def is_music_app_open():
    try:
        active_window = gw.getActiveWindow().title.lower()
        return any(word in active_window for word in ["spotify", "music", "vlc", "itunes", "player"])
    except:
        return False

def is_photo_viewer_open():
    try:
        active_window = gw.getActiveWindow().title.lower()
        return any(word in active_window for word in ["photos", "image", "gallery", "viewer"])
    except:
        return False

def eye_aspect_ratio(eye_landmarks):
    A = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
    B = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
    C = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
    return (A + B) / (2.0 * C)

def count_fingers(hand_landmarks):
    fingers = []
    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    for tip in tips[1:]:  # Ignore thumb for now
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers.count(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    face_results = face_mesh.process(rgb_frame)
    
    in_browser = is_browser_open()
    in_photos = is_photo_viewer_open()
    
    # Eye Blink Detection for Double Click
    if face_results.multi_face_landmarks:
        for face_landmarks in face_results.multi_face_landmarks:
            left_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in [362, 385, 387, 263, 373, 380]]
            right_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in [33, 160, 158, 133, 153, 144]]
            left_ear, right_ear = eye_aspect_ratio(left_eye), eye_aspect_ratio(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            
            current_time = time.time()
            if avg_ear < blink_threshold:
                if current_time - last_blink_time > 0.2:
                    last_blink_time = current_time
                    blink_count += 1
                if blink_count == 2 and (current_time - last_blink_time) <= 1.0:
                    print("Double Blink Detected! Double Click Triggered")
                    pyautogui.doubleClick()
                    blink_count = 0
            elif current_time - last_blink_time > 1.0:
                blink_count = 0

    # Hand Gesture Control
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x_coords = [lm.x * w for lm in hand_landmarks.landmark]
            y_coords = [lm.y * h for lm in hand_landmarks.landmark]
            avg_x, avg_y = np.mean(x_coords), np.mean(y_coords)
            
            index_finger = hand_landmarks.landmark[8]
            cursor_x, cursor_y = int(index_finger.x * screen_w), int(index_finger.y * screen_h)
            pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)
            
            num_fingers = count_fingers(hand_landmarks)

            if in_photos:
                if num_fingers == 2:
                    pyautogui.hotkey('ctrl', '+')  # Zoom In
                    message, message_time = "Zooming In", time.time()
                elif num_fingers == 3:
                    pyautogui.hotkey('ctrl', '-')  # Zoom Out
                    message, message_time = "Zooming Out", time.time()
            else:
                if num_fingers == 2:
                    pyautogui.scroll(-300)  # Scroll Down
                    message, message_time = "Scrolling Down", time.time()
                elif num_fingers == 3:
                    pyautogui.scroll(300)  # Scroll Up
                    message, message_time = "Scrolling Up", time.time()
            
            # Volume Control (ONLY when thumbs-up or thumbs-down is properly shown)
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            thumb_ip = hand_landmarks.landmark[3]

            fingers_closed = (
                index_tip.y > hand_landmarks.landmark[6].y and  
                middle_tip.y > hand_landmarks.landmark[10].y and  
                ring_tip.y > hand_landmarks.landmark[14].y and  
                pinky_tip.y > hand_landmarks.landmark[18].y  
            )

            thumb_up = (thumb_tip.y < index_tip.y and 
                        thumb_tip.y < middle_tip.y and 
                        thumb_tip.y < ring_tip.y and 
                        thumb_tip.y < pinky_tip.y)

            thumb_down = (
                (thumb_tip.y > thumb_ip.y and fingers_closed) or 
                (thumb_tip.y < thumb_ip.y and fingers_closed)  
            )

            if thumb_up and fingers_closed:
                pyautogui.press("volumeup")
                message, message_time = "Volume Up", time.time()

            elif thumb_down and fingers_closed:
                pyautogui.press("volumedown")
                message, message_time = "Volume Down", time.time()

            # Swipe Left/Right Gesture
            # if prev_x is not None and prev_y is not None:
            #     current_time = time.time()
            #     if current_time - last_swipe_time > cooldown_time:
            #         if avg_x - prev_x > 80:
            #             pyautogui.hotkey('alt', 'right') if in_browser else pyautogui.press('right')
            #             message, message_time, last_swipe_time = "Forward" if in_browser else "Next Media", current_time, current_time
            #         elif avg_x - prev_x < -80:
            #             pyautogui.hotkey('alt', 'left') if in_browser else pyautogui.press('left')
            #             message, message_time, last_swipe_time = "Back" if in_browser else "Previous Media", current_time, current_time
            if prev_x is not None and prev_y is not None:
                current_time = time.time()
                if current_time - last_swipe_time > cooldown_time:
                    delta_x = avg_x - prev_x
                    music_active = is_music_app_open()

                    if delta_x > 80:
                        if in_browser:
                            pyautogui.hotkey('alt', 'right')
                            message = "Browser Forward"
                        elif in_photos:
                            pyautogui.press('right')
                            message = "Next Photo"
                        elif music_active:
                            pyautogui.press('nexttrack')
                            message = "Next Song"
                        else:
                            pyautogui.press('right')
                            message = "Next"
                        message_time = current_time
                        last_swipe_time = current_time

                    elif delta_x < -80:
                        if in_browser:
                            pyautogui.hotkey('alt', 'left')
                            message = "Browser Back"
                        elif in_photos:
                            pyautogui.press('left')
                            message = "Previous Photo"
                        elif music_active:
                            pyautogui.press('prevtrack')
                            message = "Previous Song"
                        else:
                            pyautogui.press('left')
                            message = "Previous"
                        message_time = current_time
                        last_swipe_time = current_time

            prev_x, prev_y = avg_x, avg_y
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    cv2.imshow("Hand & Eye Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()