


# Install the required libraries before running the code:
# pip install SpeechRecognition pyttsx3

import speech_recognition as sr
import pyttsx3
import os
import subprocess

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize voice commands
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        speak("I am listening.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"Recognized command: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        speak("Sorry, I could not understand the command. Please try again.")
        return ""
    except sr.RequestError:
        print("Error: Unable to request results from Google Speech Recognition service.")
        speak("Sorry, there was an error with the speech recognition service.")
        return ""

# Function to execute system commands based on voice input
def execute_command(command):
    if "open browser" in command:
        speak("Opening your default web browser.")
        os.system("start chrome")
    elif "close browser" in command:
        speak("Closing your web browser.")
        os.system("taskkill /im chrome.exe /f")
    elif "open music" in command:
        speak("Opening your music application.")
        os.system("start MediaPlayer")  # Example for Windows Media Player
    elif "shut down" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")  # Windows shutdown commands
    
    # New commands
    elif "open setting" in command:
        speak("Opening settings.")
        os.system("start ms-settings:")
    elif "close setting" in command:
        speak("Closing settings.")
        os.system("taskkill /im SystemSettings.exe /f")
    
    elif "open start menu" in command:
        speak("Opening Start menu.")
        os.system("start explorer.exe shell:appsFolder")
    elif "close start menu" in command:
        speak("Closing Start menu.")
        os.system("taskkill /im explorer.exe /f && start explorer")
    
    elif "close all applications" in command:
        speak("Closing all applications.")
        os.system("taskkill /f /fi \"STATUS eq RUNNING\"")
    
    elif "open device manager" in command:
        speak("Opening Device Manager.")
        os.system("devmgmt.msc")
    
    elif "close current tab" in command:
        speak("Closing the current tab.")
        os.system("taskkill /fi \"WINDOWTITLE eq *\" /f")
    
    elif "open Wi-Fi setting" in command:
        speak("Opening Wi-Fi settings.")
        os.system("start ms-settings:network-wifi")
    
    elif "exit" in command:
        speak("Exiting and going back to the last position.")
        # This could be left as a placeholder for closing the script or application
    
    elif "open bluetooth setting" in command:
        speak("Opening Bluetooth settings.")
        os.system("start ms-settings:bluetooth")
    
    elif "open microsoft store" in command:
        speak("Opening Microsoft Store.")
        os.system("start ms-windows-store:")
    
    elif "return to desktop" in command:
        speak("Returning to desktop.")
        os.system("start explorer.exe shell:appsFolder")
    
    elif "open file explorer" in command:
        speak("Opening File Explorer.")
        os.system("explorer")
    
    elif "open this pc" in command:
        speak("Opening This PC.")
        os.system("explorer shell:MyComputerFolder")
    
    elif "open camera" in command:
        speak("Opening Camera.")
        os.system("start microsoft.windows.camera:")
    
    elif "open downloads" in command:
        speak("Opening Downloads folder.")
        os.system("explorer shell:Downloads")
    
    elif "slide next" in command:
        speak("Next slide.")
        os.system("nircmd sendkeypress pagedown")  # Requires NirCmd for controlling PPT
    
    elif "slide back" in command:
        speak("Previous slide.")
        os.system("nircmd sendkeypress pageup")  # Requires NirCmd for controlling PPT
    
    elif "battery status" in command:
        speak("Showing battery status.")
        os.system("powercfg /batteryreport")
    
    elif "open control panel" in command:
        speak("Opening Control Panel.")
        os.system("control")
    
    else:
        speak("I did not recognize that command. Please try again.")

# Main loop to keep listening for commands
if __name__ == "__main__":
    while True:
        command = listen_for_command()
        if command:
            if "terminate" in command or "quit" in command:
                speak("Goodbye!")
                break
            execute_command(command)
