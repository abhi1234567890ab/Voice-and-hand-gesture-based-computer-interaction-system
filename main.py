import tkinter as tk
import subprocess
import os
import pygame  # Import pygame for audio playback
import threading  # For playing sound in a separate thread

class GestureControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Hand Gesture Control")
        
        # Initialize Pygame mixer
        pygame.mixer.init()

        # Set the window size (width x height)
        self.master.geometry("400x400")  # Example: 400 width, 400 height

        # Set background color and font styles
        self.master.config(bg="#1e1e1e")  # Dark background
        button_font = ("Helvetica", 12, "bold")
        button_color = "#4caf50"  # Green color for buttons
        button_fg = "#ffffff"  # White text color for buttons
        self.label_font = ("Helvetica", 16, "bold")
        
        # Title label
        self.title_label = tk.Label(self.master, text="Gesture Control Panel", bg="#1e1e1e", fg="#ffffff", font=self.label_font)
        self.title_label.pack(pady=20)

        # Start Gesture Control Button
        self.start_button = tk.Button(self.master, text="Start Hand Gesture Control", 
                                      command=self.start_gesture_control, 
                                      font=button_font, bg=button_color, fg=button_fg, width=30, height=2)
        self.start_button.pack(pady=10)

        # Stop Gesture Control Button
        self.stop_button = tk.Button(self.master, text="Stop Hand Gesture Control", 
                                     command=self.stop_gesture_control, 
                                     font=button_font, bg=button_color, fg=button_fg, width=30, height=2)
        self.stop_button.pack(pady=10)

        # Start Voice Assistance Button
        self.voice_start_button = tk.Button(self.master, text="Start Voice Assistance", 
                                            command=self.start_voice_assistance, 
                                            font=button_font, bg=button_color, fg=button_fg, width=30, height=2)
        self.voice_start_button.pack(pady=10)

        # Stop Voice Assistance Button
        self.voice_stop_button = tk.Button(self.master, text="Stop Voice Assistance", 
                                           command=self.stop_voice_assistance, 
                                           font=button_font, bg=button_color, fg=button_fg, width=30, height=2)
        self.voice_stop_button.pack(pady=10)

        self.is_running = False
        self.voice_is_running = False

        # Automatically get the current directory and locate the mp3 file
        self.mp3_file = os.path.join(os.path.dirname(__file__), 'starting.mp3')

    def play_sound(self, sound_file):
        try:
            # Load the sound
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Wait for music to finish playing
                continue
        except Exception as e:
            print(f"Error playing sound: {e}")

    def start_gesture_control(self):
        if not self.is_running:
            sound_thread = threading.Thread(target=self.play_sound, args=(self.mp3_file,))
            sound_thread.start()
            self.process = subprocess.Popen(['python', 'hand.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)  # Disable start button
            self.stop_button.config(state=tk.NORMAL)  # Enable stop button

    def stop_gesture_control(self):
        if self.is_running:
            self.process.terminate()  # Terminate the process
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)  # Enable start button
            self.stop_button.config(state=tk.DISABLED)  # Disable stop button

    def start_voice_assistance(self):
        if not self.voice_is_running:
            sound_thread = threading.Thread(target=self.play_sound, args=(self.mp3_file,))
            sound_thread.start()
            self.voice_process = subprocess.Popen(['python', 'Voice.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.voice_is_running = True
            self.voice_start_button.config(state=tk.DISABLED)  # Disable start button
            self.voice_stop_button.config(state=tk.NORMAL)  # Enable stop button

    def stop_voice_assistance(self):
        if self.voice_is_running:
            self.voice_process.terminate()  # Terminate the process
            self.voice_is_running = False
            self.voice_start_button.config(state=tk.NORMAL)  # Enable start button
            self.voice_stop_button.config(state=tk.DISABLED)  # Disable stop button

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureControlApp(root)
    root.mainloop()
