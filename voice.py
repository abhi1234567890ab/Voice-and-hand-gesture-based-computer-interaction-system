import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import app 
from threading import Thread

#import Gesture_Controller_Gloved as Gesture_Controller



# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files =[]
path = ''
is_awake = True  #Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)

    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am Proton, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
        r.energy_threshold = 500 
        r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data.replace('proton','')
    app.eel.addUserMsg(voice_data)

    if is_awake==False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is proton!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

     # NEW COMMANDS INTEGRATION
    elif 'open browser' in voice_data:
        reply("Opening your default web browser.")
        os.system("start chrome")

    elif 'close browser' in voice_data:
        reply("Closing your web browser.")
        os.system("taskkill /im chrome.exe /f")

    elif 'open music' in voice_data:
        reply("Opening your music application.")
        os.system("start MediaPlayer")

    elif 'shut down' in voice_data:
        reply("Shutting down the system.")
        os.system("shutdown /s /t 1")

    elif 'open setting' in voice_data:
        reply("Opening settings.")
        os.system("start ms-settings:")

    elif 'close setting' in voice_data:
        reply("Closing settings.")
        os.system("taskkill /im SystemSettings.exe /f")
    
    elif 'minimise' in voice_data:
        reply("Minimizing the current application.")
        os.system("powershell -command \"$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('%{ESC}')\"")

    
    elif 'maximize' in voice_data:
        reply("Maximizing the current application.")
        current_window = gw.getActiveWindow()
        if current_window:
            current_window.maximize()
        else:
            reply("No active window to maximize.")

    elif 'open start menu' in voice_data:
        reply("Opening Start menu.")
        os.system("start explorer.exe shell:appsFolder")

    elif 'close start menu' in voice_data:
        reply("Closing Start menu.")
        os.system("taskkill /im explorer.exe /f && start explorer")

    elif 'close all applications' in voice_data:
        reply("Closing all applications.")
        os.system("taskkill /f /fi \"STATUS eq RUNNING\"")

    elif 'open device manager' in voice_data:
        reply("Opening Device Manager.")
        os.system("devmgmt.msc")

    elif 'close current tab' in voice_data:
        reply("Closing the current tab.")
        os.system("taskkill /fi \"WINDOWTITLE eq *\" /f")

    elif 'open wi-fi setting' in voice_data:
        reply("Opening Wi-Fi settings.")
        os.system("start ms-settings:network-wifi")

    elif 'close application' in voice_data:
       reply("Exiting the application or tab.")
       pyautogui.hotkey('alt', 'f4') 


    elif 'open bluetooth setting' in voice_data:
        reply("Opening Bluetooth settings.")
        os.system("start ms-settings:bluetooth")

    elif 'open microsoft store' in voice_data:
        reply("Opening Microsoft Store.")
        os.system("start ms-windows-store:")

    elif 'return to desktop' in voice_data:
        reply("Returning to desktop.")
        os.system("start explorer.exe shell:appsFolder")

    elif 'open file explorer' in voice_data:
        reply("Opening File Explorer.")
        os.system("explorer")

    elif 'open this pc' in voice_data:
        reply("Opening This PC.")
        os.system("explorer shell:MyComputerFolder")

    elif 'open camera' in voice_data:
        reply("Opening Camera.")
        os.system("start microsoft.windows.camera:")

    elif 'open downloads' in voice_data:
        reply("Opening Downloads folder.")
        os.system("explorer shell:Downloads")

    elif 'slide next' in voice_data:
        reply("Next slide.")
        pyautogui.press('pagedown')

    elif 'slide back' in voice_data:
        reply("Previous slide.")
        pyautogui.press('pageup')

    elif 'battery status' in voice_data:
        reply("Showing battery status.")
        os.system("powercfg /batteryreport")

    elif 'open control panel' in voice_data:
        reply("Opening Control Panel.")
        os.system("control")
    
    elif 'stop' in voice_data:
        reply("Stopping the application.")
        sys.exit()  # This will exit the program

    

    elif 'search' in voice_data:
        reply('Searching for ' + voice_data.split('search')[1])
        url = 'https://google.com/search?q=' + voice_data.split('search')[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif 'location' in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False
    
    elif 'launch hand gesture' in voice_data:
        reply("Launching hand gesture recognition.")
        gesture_file_path = "hand.py"  # Replace with the actual path to the Python file
        os.system(f"python {gesture_file_path}")

    elif 'terminate hand gesture' in voice_data:
       reply("Stopping hand gesture recognition.")
       os.system("taskkill /im python.exe /f")  # This will forcefully stop any Python process



    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        #sys.exit() always raises SystemExit, Handle it in main loop
        sys.exit()
        
    
    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply('Launched Successfully')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        
    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')
          
    elif 'page' in voice_data or 'pest'  in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')
        
    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter+=1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)
        
    elif file_exp_status == True:
        counter = 0   
        if 'open' in voice_data:
            if isfile(join(path,files[int(voice_data.split(' ')[-1])-1])):
                os.startfile(path + files[int(voice_data.split(' ')[-1])-1])
                file_exp_status = False
            else:
                try:
                    path = path + files[int(voice_data.split(' ')[-1])-1] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter+=1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
                    
                except:
                    reply('You do not have permission to access this folder')
                                    
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter+=1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)
                   
    else: 
        reply('I am not functioned to do this !')

# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        #take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        #take input from Voice
        voice_data = record_audio()

    #process voice_data
    if 'proton' in voice_data:
        try:
            #Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            os._exit(0)  # This will exit the program
            break
        except:
            #some other exception got raised
            print("EXCEPTION raised while closing.") 
            break
        


