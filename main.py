import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import pygame
import threading

class GestureControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("🖐️ Voice & Hand Gesture Control Panel")
        self.master.configure(bg="#121212")
        self.master.geometry("1280x720")
        self.master.resizable(True, True)

        pygame.mixer.init()
        self.mp3_file = os.path.join(os.path.dirname(__file__), 'starting.mp3')

        self.button_font = ("Segoe UI", 12, "bold")
        self.label_font = ("Segoe UI", 22, "bold")

        # Layout frames
        self.main_frame = tk.Frame(self.master, bg="#121212")
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg="#121212")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=40, pady=20)

        self.right_frame = tk.Frame(self.main_frame, bg="#121212")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=20)

        # Scrollable canvas inside left_frame
        self.canvas = tk.Canvas(self.left_frame, bg="#121212", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Load Images
        self.logo_size = (200, 200)
        self.icon_size = (35, 35)
        self.side_img_size = (750, 400)
        self.images = {
            "logo": self.load_image("assets/logo.png", self.logo_size),
            "hand": self.load_image("assets/hand.png", self.icon_size),
            "mic": self.load_image("assets/mic.png", self.icon_size),
            "game": self.load_image("assets/game.png", self.icon_size),
            "assistant": self.load_image("assets/assistant.png", self.icon_size),
            "side": self.load_image("assets/side.png", self.side_img_size),
        }

        # Right image section
        if self.images["side"]:
            self.side_img_label = tk.Label(self.right_frame, image=self.images["side"], bg="#121212")
            self.side_img_label.pack(anchor="w", padx=(10, 0), pady=(0, 10))

            self.get_started_label = tk.Label(
                self.right_frame,
                text="Let's get started!",
                bg="#121212",
                fg="#00FFB2",
                font=("Segoe UI", 30, "bold")
            )
            self.get_started_label.pack()

        # Left content section
        self.center_frame = tk.Frame(self.scrollable_frame, bg="#121212")
        self.center_frame.pack(expand=True)

        self.logo_label = tk.Label(self.center_frame, image=self.images["logo"], bg="#121212")
        self.logo_label.pack(pady=(20, 10))

        self.title_label = tk.Label(
            self.center_frame,
            text="Gesture & Voice Assistant",
            bg="#121212",
            fg="#00FFB2",
            font=self.label_font
        )
        self.title_label.pack(pady=(0, 30))

        self.button_frame = tk.Frame(self.center_frame, bg="#121212")
        self.button_frame.pack()

        # Buttons
        self.create_button("Start Hand Gesture Control", self.start_gesture_control, self.images["hand"])
        self.create_button("Stop Hand Gesture Control", self.stop_gesture_control, self.images["hand"], disabled=True)
        self.create_button("Start Voice To Text", self.start_speechtotext_control, self.images["mic"])
        self.create_button("Stop Voice To Text", self.stop_speechtotext_control, self.images["mic"], disabled=True)
        self.create_button("Start Game", self.start_game, self.images["game"])
        self.create_button("Stop Game", self.stop_game, self.images["game"], disabled=True)
        self.create_button("Start Voice Assistant", self.start_voice_assistance, self.images["assistant"])
        self.create_button("Stop Voice Assistant", self.stop_voice_assistance, self.images["assistant"], disabled=True)

        # State flags
        self.is_running = False
        self.voice_is_running = False
        self.speechto_text_is_running = False
        self.game_is_running = False

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def load_image(self, path, size=None):
        try:
            img = Image.open(path)
            if size:
                img = img.resize(size, Image.ANTIALIAS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {path}, {e}")
            return None

    def create_button(self, text, command, image, disabled=False):
        container = tk.Frame(self.button_frame, bg="#121212")
        container.pack(pady=8)

        button = tk.Button(
            container,
            text="  " + text,
            image=image,
            compound=tk.LEFT,
            command=command,
            font=self.button_font,
            bg="#1f1f1f",
            fg="#00FFB2",
            activebackground="#2c2c2c",
            activeforeground="#00FFB2",
            bd=0,
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground="#00FFB2",
            padx=14,
            pady=10,
            width=350,
            anchor="w",
            cursor="hand2"
        )
        button.pack()

        button.bind("<Enter>", lambda e: button.config(bg="#2a2a2a"))
        button.bind("<Leave>", lambda e: button.config(bg="#1f1f1f"))

        name = text.lower().replace(" ", "_")
        setattr(self, name + "_button", button)

        if disabled:
            button.config(state=tk.DISABLED)

    def play_sound(self, sound_file):
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except Exception as e:
            print(f"Error playing sound: {e}")

    def start_gesture_control(self):
        if not self.is_running:
            threading.Thread(target=self.play_sound, args=(self.mp3_file,)).start()
            self.process = subprocess.Popen(['python', 'handgesture.py'])
            self.is_running = True
            self.start_hand_gesture_control_button.config(state=tk.DISABLED)
            self.stop_hand_gesture_control_button.config(state=tk.NORMAL)

    def stop_gesture_control(self):
        if self.is_running:
            self.process.terminate()
            self.is_running = False
            self.start_hand_gesture_control_button.config(state=tk.NORMAL)
            self.stop_hand_gesture_control_button.config(state=tk.DISABLED)

    def start_speechtotext_control(self):
        if not self.speechto_text_is_running:
            threading.Thread(target=self.play_sound, args=(self.mp3_file,)).start()
            self.speechto_text = subprocess.Popen(['python', 'speechtotext.py'])
            self.speechto_text_is_running = True
            self.start_voice_to_text_button.config(state=tk.DISABLED)
            self.stop_voice_to_text_button.config(state=tk.NORMAL)

    def stop_speechtotext_control(self):
        if self.speechto_text_is_running:
            self.speechto_text.terminate()
            self.speechto_text_is_running = False
            self.start_voice_to_text_button.config(state=tk.NORMAL)
            self.stop_voice_to_text_button.config(state=tk.DISABLED)

    def start_game(self):
        if not self.game_is_running:
            threading.Thread(target=self.play_sound, args=(self.mp3_file,)).start()
            self.game = subprocess.Popen(['python', 'game.py'])
            self.game_is_running = True
            self.start_game_button.config(state=tk.DISABLED)
            self.stop_game_button.config(state=tk.NORMAL)

    def stop_game(self):
        if self.game_is_running:
            self.game.terminate()
            self.game_is_running = False
            self.start_game_button.config(state=tk.NORMAL)
            self.stop_game_button.config(state=tk.DISABLED)

    def start_voice_assistance(self):
        if not self.voice_is_running:
            threading.Thread(target=self.play_sound, args=(self.mp3_file,)).start()
            self.voice_process = subprocess.Popen(['python', 'Voice.py'])
            self.voice_is_running = True
            self.start_voice_assistant_button.config(state=tk.DISABLED)
            self.stop_voice_assistant_button.config(state=tk.NORMAL)

    def stop_voice_assistance(self):
        if self.voice_is_running:
            self.voice_process.terminate()
            self.voice_is_running = False
            self.start_voice_assistant_button.config(state=tk.NORMAL)
            self.stop_voice_assistant_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureControlApp(root)
    root.mainloop()
