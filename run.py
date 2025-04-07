import cv2
import mediapipe as mp
import tkinter as tk
import subprocess
from PIL import Image, ImageTk

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

class GestureControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Hand Gesture Control")
        self.master.geometry("500x500")
        self.master.config(bg="#1e1e1e")
        
        self.label_font = ("Helvetica", 16, "bold")
        
        # Initial Caption
        self.caption_label = tk.Label(self.master, text="Click on Authenticate to Unlock the Application", bg="#1e1e1e", fg="#ffffff", font=self.label_font)
        self.caption_label.pack(pady=10)
        
        # Unlock Button
        self.unlock_button = tk.Button(self.master, text="Authenticate", command=self.start_camera, font=("Helvetica", 12, "bold"), bg="#4caf50", fg="#ffffff", width=30, height=2)
        self.unlock_button.pack(pady=20)
        
        # Label for Camera Caption (Initially Hidden)
        self.camera_caption = tk.Label(self.master, text="", bg="#1e1e1e", fg="#ffffff", font=self.label_font)
        self.camera_caption.pack()
        
        # Label for Camera Feed
        self.camera_label = tk.Label(self.master, bg="#1e1e1e")
        self.camera_label.pack()
        
        self.is_locked = True
        self.cap = None

    def start_camera(self):
        self.unlock_button.pack_forget()  # Hide button
        self.caption_label.pack_forget()  # Hide initial text
        
        # Show new caption above camera feed
        self.camera_caption.config(text="Show Thumbs Up (👍) to Unlock")
        
        self.cap = cv2.VideoCapture(0)
        self.process_camera()
    
    def process_camera(self):
        if self.cap and self.is_locked:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb_frame)
                
                if result.multi_hand_landmarks:
                    for landmarks in result.multi_hand_landmarks:
                        if self.is_thumbs_up(landmarks):
                            self.is_locked = False
                            self.cap.release()
                            self.run_main_script()
                            return
                
                # Convert frame for Tkinter display
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
            self.master.after(10, self.process_camera)

    def is_thumbs_up(self, landmarks):
        """Detects a strict thumbs-up gesture"""
        thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

        index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

        index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]  # Base of index finger

        # Condition 1: Thumb tip is above the thumb IP joint (thumb is raised)
        thumb_up = thumb_tip.y < thumb_ip.y

        # Condition 2: Other fingers should be bent (their tips should be below their MCP)
        fingers_folded = (
            index_tip.y > index_mcp.y and
            middle_tip.y > index_mcp.y and
            ring_tip.y > index_mcp.y and
            pinky_tip.y > index_mcp.y
        )

        return thumb_up and fingers_folded  # Unlock only if both conditions are met

    def run_main_script(self):
        subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.master.after(1000, self.master.destroy)  # Close Tkinter window after running script

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureControlApp(root)
    root.mainloop()
