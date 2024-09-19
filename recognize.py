import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import keyboard 


pyautogui.FAILSAFE = False


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils


screen_width, screen_height = pyautogui.size()

last_position = (screen_width // 2, screen_height // 2)  
smoothing_factor = 0.8 
scaling_factor = 1.5  

finger_visible = False
last_finger_state = "open"
last_click_time = 0

scroll_speed = 400  # Scroll speed can be adjusted here

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          
            landmarks = []
            for id, lm in enumerate(hand_landmarks.landmark):
                x = int(lm.x * screen_width)
                y = int(lm.y * screen_height)
                landmarks.append((x, y))

            index_finger_tip = landmarks[8] 
            index_finger_dip = landmarks[7]
            middle_finger_tip = landmarks[12]
            middle_finger_dip = landmarks[11]
            ring_finger_tip = landmarks[16]
            pinky_finger_tip = landmarks[20]
            thumb_tip = landmarks[4]

           
            cv2.circle(img, (index_finger_tip[0], index_finger_tip[1]), 10, (0, 255, 0), cv2.FILLED)

            
            fingers_up = [
                index_finger_tip[1] < index_finger_dip[1],
                middle_finger_tip[1] < middle_finger_dip[1],
                ring_finger_tip[1] < landmarks[15][1],
                pinky_finger_tip[1] < landmarks[19][1],
                thumb_tip[0] < landmarks[2][0]  
            ]
            num_fingers_up = sum(fingers_up)

            
            if num_fingers_up == 2:
               
                cv2.putText(img, "Scrolling Down", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.scroll(-scroll_speed)

            elif num_fingers_up == 3:
               
                cv2.putText(img, "Scrolling Up", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.scroll(scroll_speed)

            elif num_fingers_up == 4:
                
                cv2.putText(img, "Scrolling Right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.hscroll(scroll_speed)

            elif num_fingers_up == 5:
                
                cv2.putText(img, "Scrolling Left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.hscroll(-scroll_speed)

            
            if fingers_up[0] and not any(fingers_up[1:]):  
                finger_visible = True

                smooth_x = (1 - smoothing_factor) * last_position[0] + smoothing_factor * index_finger_tip[0]
                smooth_y = (1 - smoothing_factor) * last_position[1] + smoothing_factor * index_finger_tip[1]

                fast_x = (smooth_x - screen_width / 2) * scaling_factor + screen_width / 2
                fast_y = (smooth_y - screen_height / 2) * scaling_factor + screen_height / 2

                fast_x = min(max(fast_x, 0), screen_width)
                fast_y = min(max(fast_y, 0), screen_height)

                pyautogui.moveTo(fast_x, fast_y)
                last_position = (fast_x, fast_y)
            else:
                finger_visible = False

            
            if finger_visible and last_finger_state == "closed":
                current_time = time.time()
                if current_time - last_click_time > 0.2:  
                    pyautogui.click()
                    last_click_time = current_time

            last_finger_state = "open" if finger_visible else "closed"

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', img)

    if keyboard.is_pressed('q'):  
        break

cap.release()
cv2.destroyAllWindows()
