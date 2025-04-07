# voice_typing_app.py
import speech_recognition as sr
import pyautogui
import threading
import tkinter as tk
import sounddevice as sd
import queue
import vosk
import json
import time

class VoiceTypingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("⚡ Fast Voice Typing - Notepad")
        self.master.geometry("500x350")
        self.master.config(bg="#1e1e1e")

        self.label = tk.Label(self.master, text="🎤 Speak Now", font=("Helvetica", 16, "bold"), fg="white", bg="#1e1e1e")
        self.label.pack(pady=10)

        self.text_area = tk.Text(self.master, height=5, width=50, font=("Helvetica", 12))
        self.text_area.pack(pady=10)

        self.start_button_eng = tk.Button(self.master, text="Start English Typing", command=self.start_voice_typing_eng,
                                          font=("Helvetica", 12), bg="green", fg="white", width=20)
        self.start_button_eng.pack(pady=5)

        self.start_button_hin = tk.Button(self.master, text="Start Hindi Typing", command=self.start_voice_typing_hin,
                                          font=("Helvetica", 12), bg="blue", fg="white", width=20)
        self.start_button_hin.pack(pady=5)

        self.recognizer = sr.Recognizer()

        self.is_running = False
        self.q = queue.Queue()

        self.model_eng = vosk.Model(lang="en-in")
        self.model_hin = vosk.Model(lang="hi")

        self.rec_eng = vosk.KaldiRecognizer(self.model_eng, 16000)
        self.rec_hin = vosk.KaldiRecognizer(self.model_hin, 16000)

        self.stop_event = threading.Event()

    def vosk_audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        if self.is_running:
            self.q.put(bytes(indata))

    def start_vosk_recognition(self, lang):
        rec = self.rec_eng if lang == "en" else self.rec_hin
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=self.vosk_audio_callback):
            while not self.stop_event.is_set():
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())["text"]
                    if result:
                        self.master.after(0, self.update_text_area, result)

    def update_text_area(self, text):
        print(f"📝 {text}")
        self.text_area.insert(tk.END, text + " ")
        self.text_area.see(tk.END)
        self.text_area.update_idletasks()
        pyautogui.typewrite(text + " ")

    def start_voice_typing(self, lang):
        if self.is_running:
            return
        self.is_running = True
        self.stop_event.clear()
        self.start_button_eng.config(state=tk.DISABLED)
        self.start_button_hin.config(state=tk.DISABLED)

        self.vosk_thread = threading.Thread(target=self.start_vosk_recognition, args=("en" if lang == "en-IN" else "hi",), daemon=True)
        self.vosk_thread.start()

    def start_voice_typing_eng(self):
        self.start_voice_typing("en-IN")

    def start_voice_typing_hin(self):
        self.start_voice_typing("hi-IN")


def run_voice_typing_app():
    root = tk.Tk()
    app = VoiceTypingApp(root)

    time.sleep(1)
    pyautogui.hotkey("win", "r")
    pyautogui.typewrite("notepad")
    pyautogui.press("enter")

    root.mainloop()


if __name__ == "__main__":
    run_voice_typing_app()
