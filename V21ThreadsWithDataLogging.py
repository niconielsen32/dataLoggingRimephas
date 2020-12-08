import pygame
import pygame.freetype
import cv2
import threading
import multiprocessing as mp

from moviepy.editor import VideoFileClip
import math
import socket
import snowboydecoder
import speech_recognition as sr
#from gtts import gTTS
import re
from pydub import AudioSegment as AS
import numpy as np
import random
import subprocess

pygame.init()

import dispenser           #dispenser.py
import stattracker         #stattracker.py
from scrollingtext import *#scrollingtext.py
import LEDs                #LEDs.py
import trackeduser         #trackeduser.py
import showimages          #showimages.py
import facetracking as ft  #facetracking.py
from wizardOfOz import *
import globdef
import RPi.GPIO as GPIO
import os
import time

#--------------------------------Data Logging----------------------------------------------------------
import csv
import pandas as pd
from threading import Timer,Thread,Event

filename = "dataRimephas.csv"

numberOfPeople = 0

seconds = 0
minutes = 0
hours = 0


class TimerClass():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
      
      
def clearFile(filename):
    open(filename, 'w').close()

def incrementSeconds():
    global seconds, minutes, hours

    seconds += 1

    if(seconds == 60):
        minutes += 1
        seconds = 0

    if(minutes == 60):
        hours += 1
        minutes = 0

    
def readDataFromFile(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
        file.close()


def readDataToPDframe(filename):
    df = pd.read_csv(filename)
    print(df)


def writeDataToFile(filename, disp, typeOfActivation):
    with open(filename, 'a') as file:
        print("Writing to File")
        writer = csv.writer(file)
        writer.writerow([typeOfActivation, hours, minutes, seconds, disp.numberOfActivations, numberOfPeople])
        file.close()

# Call this function to clear file
#clearFile()
#---------------------------------------------------------------------------------------------------


#import picamera
"""
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

from irSensorClass import irSensor
"""

##########  Settings  ##########
wizardOfOz = False
showScrollingImages = False
showFaceMask = True
largeScreen = True
size = (800,480)
largeSize = (800,1280)
if largeScreen:
    screenSize = largeSize
    moveScreen = (largeSize[0]-size[0])/2
else:
    screenSize = size
    moveScreen = 0
WHITE = (255,255,255)
BACKGROUND = WHITE
LANGUAGE = "da-DK" # en-US or da-DK
isOnline = True
eyeDesign = "normal" # normal or monster
"""
# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

numSensors = 2
sensorThreshold = 1.5

ADC = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
irSensors = irSensor(ADC, numSensors, sensorThreshold)
thresholdValue = irSensors.initSensors()
"""

########## Load images ##########
normalL = pygame.image.load("images/png/normalL.png")
normalR = pygame.transform.flip(normalL, True, False)
normalwhiteL = pygame.image.load("images/png/normalLwhite.png")
normalwhiteR = pygame.transform.flip(normalwhiteL, True, False)

closedL = pygame.image.load("images/png/closedL.png")
closedR = pygame.transform.flip(closedL, True, False)

happyL = pygame.image.load("images/png/happyL.png")
happyR = pygame.transform.flip(happyL, True, False)

confusedL = pygame.image.load("images/png/confusedL.png")
confusedR = pygame.image.load("images/png/confusedR.png")
confusedLwhite = pygame.image.load("images/png/normalAltLwhite.png")
confusedRwhite = pygame.image.load("images/png/confusedRwhite.png")

onlineicon = pygame.image.load("images/png/online.png")
offlineicon = pygame.image.load("images/png/offline.png")

danishbutton = pygame.image.load("images/bg/danishicon.png")
englishbutton = pygame.image.load("images/bg/englishicon.png")
danishbutton = pygame.transform.scale(danishbutton, (120,90))
englishbutton = pygame.transform.scale(englishbutton, (120,90))

nobutton = pygame.image.load("images/png/nobutton.png")
yesbutton = pygame.image.load("images/png/yesbutton.png")

pupil = pygame.image.load("images/png/pupil.png")

colorselector = pygame.image.load("images/bg/ColorPicker.bmp")
colorselector = pygame.transform.flip(colorselector, False, True)
coloricon = pygame.transform.scale(colorselector, (120, 90))
colorselector = pygame.transform.scale(colorselector, (700, 350))

menuicon = pygame.image.load("images/png/menuicon.png")
graphicon = pygame.image.load("images/png/graphicon.png")
graphicon = pygame.transform.scale(graphicon, (90,90))

monster = pygame.image.load("images/png/monstereyes.png")
monsterpupil = pygame.image.load("images/png/monsterpupil.png")
monsterpupilsmall = pygame.image.load("images/png/monsterpupilsmall.png")
monsterblinkL = pygame.image.load("images/png/monsterclosedL.png")
monsterblinkM = pygame.image.load("images/png/monsterclosedM.png")
monsterblinkR = pygame.image.load("images/png/monsterclosedR.png")

benderL = pygame.image.load("images/bg/benderL.png")
benderR = pygame.transform.flip(benderL, True, False)
benderpupil = pygame.image.load("images/bg/benderpupil.png")

handDetectL = pygame.image.load("images/png/left_hand_detect2.png")
scalex = int(handDetectL.get_width()/1.5)
scaley = int(handDetectL.get_height()/1.5)
handDetectL = pygame.transform.scale(handDetectL, (scalex,scaley))
handDetectR = pygame.transform.flip(handDetectL, True, False)
#print("hm: ", handDetectL.get_size())

#facemask = pygame.image.load("images/png/mundbind800alt.png")
facemask = pygame.image.load("images/png/mundbind1100.png")
#facemask = pygame.transform.scale(facemask, (800,700))

########## Load sounds ##########
Hi_sanitizer = "sounds/Hi_sanitizer.mp3"
Sorry_sanitizer = "sounds/Sorry_sanitizer.mp3"
Great_dispenser = "sounds/Great_dispenser.mp3"
Nice_day = "sounds/Nice_day.mp3"
Sorry_bye = "sounds/Sorry_bye.mp3"
Sorry_video = "sounds/Sorry_video.mp3"
Video = "sounds/Video.mp3"

Hej_sprit = "sounds/Hej_sprit.mp3"
Undskyld_sprit = "sounds/Undskyld_sprit.mp3"
Under_automaten = "sounds/Under_automaten.mp3"
God_dag = "sounds/God_dag.mp3"
Undskyld_farvel = "sounds/Undskyld_farvel.mp3"
Undskyld_video = "sounds/Undskyld_video.mp3"
Video_da = "sounds/Video_da.mp3"
Okay_video = "sounds/Okay_video.mp3"
countdown_da = "sounds/countdown_da.mp3"

thirtysec = "sounds/30sec.mp3"
joke1_1 = "sounds/joke1_1.mp3"
joke1_2 = "sounds/joke1_2.mp3"
joke2_1 = "sounds/joke2_1.mp3"
joke2_2 = "sounds/joke2_2.mp3"
joke3_1 = "sounds/joke3_1.mp3"
joke3_2 = "sounds/joke3_2.mp3"
nudge1 = "sounds/nudge1.mp3"
nudge2 = "sounds/nudge2.mp3"
nudge1da = "sounds/nudge1da.mp3"
Okay_video_da = "sounds/Okay_video_da.mp3"
thirtysecda = "sounds/30sec_da.mp3"
caring = "sounds/thanks_for_caring.mp3"
often = "sounds/sanitize_often.mp3"


# List of English voice lines
sounds_EN = [Hi_sanitizer, Video, Great_dispenser, Okay_video, Sorry_sanitizer, Sorry_video,  Nice_day, Sorry_bye,
          often, nudge1, thirtysec, caring, joke1_1, joke1_2, joke2_1, joke2_2, joke3_1, joke3_2]
# List of Danish voice lines
sounds_DA = [Hej_sprit, Video_da, Under_automaten, Okay_video_da, Undskyld_sprit, Undskyld_video, God_dag, Undskyld_farvel,
          nudge1da, nudge1da, thirtysecda, countdown_da, caring]

########## Functions ##########
# Check if connected to internet
def checkInternet(host="8.8.8.8", port=53, itimeout=3):
    try:
        socket.setdefaulttimeout(itimeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def showButtons():
    screen.blit(yesbutton, (720,0))
    screen.blit(nobutton, (0,0))

def wait(ms):
    pygame.time.wait(ms)

def blitImages(left, right):
    screen.blit(left, (0,0))
    screen.blit(right, (400,0))
    
########## Functions for Snowboy keyword detection - used when not connected to internet ##########
def signal():
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted, timeout
    timeout += 0.03
    if threadevent.is_set():
        return True
    if timeout > 5:
        print("Timeout happened")
        return True
    return interrupted

# Callback function for detected "yes"
def detected_callback1():
    print("callback 1")
    signal()
    global yes_detected
    yes_detected = True
    
# Callback function for detected "no"
def detected_callback2():
    print("callback 2")
    signal()
    global no_detected
    no_detected = True

def listen_for_two_cmds(cmd1, cmd2):
    global interrupted, timeout
    interrupted = False
    timeout = 0.
    detector = snowboydecoder.HotwordDetector(
        [f"resources/models/{cmd1}.pmdl",f"resources/models/{cmd2}.pmdl"], sensitivity=[0.5,0.5])
    detector.start(detected_callback=[detected_callback1, detected_callback2],
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    detector.terminate()
    print("Terminated")

########## Function for Google Speech Recognition - used when connected to internet ###########
def google_in():
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Say something!")
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=2)
        except sr.WaitTimeoutError:
            return "Timeout"
        else:
            try:
                out = r.recognize_google(audio, language=LANGUAGE)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                return out
        return "Error"
    
# Search for keywords in string from Google SR
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

########## Speech recognition main function ##########
def speech_in(cmd1, cmd2):
    global yes_detected, no_detected
    yes_detected = False
    no_detected = False
    if cmd1 == "yes" and LANGUAGE == "da-DK":
        cmdList1 = ["ja", "gerne", "jo", "ok"]
        cmdList2 = ["nej", "ellers tak"]
    elif cmd1 == "yes" and LANGUAGE == "en-US":
        cmdList1 = [cmd1, "please", "ok", "alright", "why not", "yeah", "i guess"]
        cmdList2 = [cmd2, "don't"]
    else:
        cmdList1 = [cmd1]
        cmdList2 = [cmd2]
    if not isOnline:
        listen_for_two_cmds(cmd1, cmd2)
    else:    
        gin = google_in()
        for cmd in cmdList1:
            if findWholeWord(cmd)(gin):
                yes_detected = True
                return
        for cmd in cmdList2:
            if findWholeWord(cmd)(gin):
                no_detected = True
                return

########## Text-to-Speech function ##########
def speech_out(index):
    if LANGUAGE == "da-DK":
        sounds = sounds_DA
    else:
        sounds = sounds_EN
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    """
    sound = AS.from_mp3(sounds[index])
    raw_data = sound.raw_data
    sample_rate = sound.frame_rate * 2.3
    amp_data = np.frombuffer(raw_data, dtype=np.int16)
    amp_data = np.absolute(amp_data)
    """
    pygame.mixer.music.play()
    if largeScreen:
        global textList
        textList = createTextSurface(finalSurface, index, top_screen_height, top_screen_width, wizardOfOz, LANGUAGE)
    while pygame.mixer.music.get_busy():
        pass
        #if threadevent.is_set():
        #pygame.mixer.quit()
        #break
    """
        leds.change_brightness_when_speaking(sample_rate, amp_data)
    leds.dots.fill(leds.NOCOLOR)
    leds.indexLED = 5
    """
########## Main interaction function going through interaction items to be executed ##########
def interaction(*items):
    global textList, show_buttons, state, interactionWait
    if wizardOfOz:
        for item in items:
            speech_out
    else:    
        skip = False
        for item in items:
            if item == "nudge":
                speech_out(8+items[1])
            elif item == "30s":
                #rand = random.randint(0,2)
                #speech_out(10+rand)
                rand = 1
                if rand: speech_out(10)
                else: speech_out(11)
            elif item == "joke":
                speech_out(11+items[1])
                wait(2000)
                speech_out(12+items[1])
            elif item == "sanitizer":
                if len(items)<=1:
                    skip = interactionQuestion(3)
                else: skip = interactionQuestion(0)
            elif item == "video" and not skip:
                interactionQuestion(1)
            elif item == "monster":
                global eyeDesign, state
                speech_in(items[0], items[1])
                if yes_detected:
                    eyeDesign = items[0]
                    state = NORMALSTATE
                elif no_detected:
                    eyeDesign = items[1]
                    state = NORMALSTATE
            elif item == "novideo":
                skip = interactionQuestion(3)    
            textList = []
            if threadevent.is_set(): break
    threadevent.clear()
    if interactionWait: state = WAITSTATE #BLINKSTATE2
    print("Flow ended")
    #show_buttons = False

########## Interaction function for two-way communication ##########
def interactionQuestion(question):
    if question == 3:
        novideo = True
        question = 0
    else: novideo = False
    global show_buttons, show_hand_detect
    skip = False
    lastNumberOfActivations = disp.numberOfActivations
    speech_out(question)
    i = 0
    
    while not threadevent.is_set():
        listenthread = threading.Thread(target=speech_in, args=("yes","no"))
        listenthread.start()
        while listenthread.is_alive():
            if yes_detected or no_detected: break
        #speech_in("yes", "no")
        if yes_detected:
            pygame.event.post(happyevent)
            speech_out(question+2)
            if question == 0:
                if novideo:
                    iwait = 200
                    while iwait:
                        if disp.numberOfActivations != lastNumberOfActivations:
                            speech_out(10)
                            break
                        iwait -= 1
                        if iwait < 1:
                            break
                else:
                    print("video")
                    wait(2000)
                break
            else:
                global state
                state = VIDEOSTATE
                wait(35000)
                break
        elif no_detected:
            speech_out(6)
            skip = True
            break
        elif question == 0 and disp.numberOfActivations != lastNumberOfActivations:
            #pygame.event.post(happyevent)
            if novideo:
                speech_out(11)
            else: wait(2000)
            break
        #elif i < 1:
        #    pygame.event.post(questionevent)      # dont repeat if sound level low?
        #    speech_out(question+4)
        #    show_buttons = True
        #    i += 1
        elif i < 1:
            show_hand_detect = True
            i += 1
        elif question == 1:
            speech_out(6)
            break
        else:
            #wait(2000)
            #speech_out(7)
            skip = True
            break
    show_hand_detect = False
    print("Interaction ended")
    return skip

def playVideo():
    """
    print(pygame.display.get_wm_info())
    movie = "videos/normalvideo.mp4"
    vlcInstance = vlc.Instance()
    media = vlcInstance.media_new(movie)
    player = vlcInstance.media_player_new()
    #player.set_hwnd(pygame.display.get_wm_info()['window'])
    winID = pygame.display.get_wm_info()['window']
    player.set_xwindow(winID)
    player.set_position(0.7)
    player.set_media(media)
    pygame.mixer.quit()
    player.play()
    return player
    
    while player.get_state() != vlc.State.Ended:
        pass
    player.stop()
    
    """
    clip = VideoFileClip(f'videos/{eyeDesign}video.mp4')#, target_resolution=(480,800))
    clip = clip.volumex(0.05)
    clip.preview(fullscreen = True)
    
res0 = (320,320)
res1 = (320,240)
res2 = (640,480)
res3 = (1280,960)
res = res2

# Calculating the gaze angles to detected face
def calculateAngles(x, y, w, h):
    WIDTH = res[0]/2
    HEIGHT = res[1]/2
    EYE_DEPTH = 2
    hFOV = 62/2
    vFOV = 49/2
    ppcm = WIDTH*2/15.5# * 1.5

    center = (int(x+w*0.5), int(y+h*0.5))
    hAngle = (1 - center[0]/WIDTH) * hFOV
    vAngle = (1 - center[1]/HEIGHT) * vFOV            
    c = -0.26*w+103
    if c < 30: c = 30
    
    global pupilL, pupilR, pupilV
    # horizontal
    b = 4
    angleA = (90 - hAngle)*math.pi/180
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
    angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
    pupilL = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
    
    b_hat = 2*b
    c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
    angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
    pupilR = int((math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm)
    
    # vertical
    b = 6
    angleA = (90 - vAngle)*math.pi/180
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
    angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
    pupilV = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
    
# Draw the pupils on the eyes
def drawPupils():
    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
    
def drawMonsterPupils():
    centerLmonster = (158-43, 218-50)
    centerMmonster = (390-25, 250-27)
    centerRmonster = (640-43, 222-50)
    pupilposL = (centerLmonster[0]+pupilL, centerLmonster[1]-pupilV)
    pupilposR = (centerRmonster[0]+pupilR, centerRmonster[1]-pupilV)
    pupilposM = (centerMmonster[0]+int((pupilL+pupilR)/2), centerMmonster[1]-pupilV) 
    screen.blit(monsterpupil, pupilposL)
    screen.blit(monsterpupil, pupilposR)
    screen.blit(monsterpupilsmall, pupilposM)

########## Set up face detection globals ##########
pupilL = 0
pupilR = 0
pupilV = 0

########## Set up speech recognition globals ##########
interrupted = False
yes_detected = False
no_detected = False
timeout = 0.
show_hand_detect = False

show_buttons = False
interactionWait = False #Indicate if waiting between interactions

offset = 800-170-100
eyeL = pygame.Rect(100, 210, 170, 170)
eyeR = pygame.Rect(offset, 210, 170, 170)
centerL = (185-30+10, 295-30) 
centerR =(offset+85-30-10,295-30)
buttonL = pygame.Rect(0,0,100,70)
buttonR = pygame.Rect(800-100,0,100,70)

########## Events ##########
BLINKEVENT = pygame.USEREVENT + 1
NORMALEVENT = pygame.USEREVENT + 2
HAPPYEVENT = pygame.USEREVENT + 3
HAPPYSTARTEVENT = pygame.USEREVENT + 4
QUESTIONEVENT = pygame.USEREVENT + 5
INTERACTIONEVENT = pygame.USEREVENT + 6
GAZEEVENT = pygame.USEREVENT + 7
MONSTERBLINKEVENT = pygame.USEREVENT + 8
PHOTOEVENT = pygame.USEREVENT + 9
happyevent = pygame.event.Event(HAPPYSTARTEVENT)
questionevent = pygame.event.Event(QUESTIONEVENT)

########## States ##########
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
CONFUSEDSTATE = 4
VIDEOSTATE = 5
BLINKSTATE2 = 6
HAPPYSTATE2 = 7
MENUSTATE = 8
COLORSTATE = 9
MONSTERSTATE = 10
MONSTERBLINKSTATE = 11
MONSTERBLINKSTATE2 = 12
MONSTERBLINKSTATE3 = 13
GRAPHSTATE = 14
WAITSTATE = 15
TESTSTATE = 16
state = NORMALSTATE

textList = []
if __name__ == '__main__':
    
    # Initialize interprocess communication
    if not wizardOfOz:
        receiver, sender = mp.Pipe(True)
        mp.set_start_method('spawn',force=True)
        tracking_proc = mp.Process(target=ft.faceTracking, args=(sender,))
        tracking_proc.start()
    else:
        logfile = open("testing/testlog.txt","a+")
        timestamp = dt.datetime.now()
        logfile.write(f"{timestamp}: Device started\n")
        sh = ft.Snapshot()
        
    logfile = open("testing/abenalog.txt","a+")
    timestamp = dt.datetime.now()
    logfile.write(f"{timestamp}: Device started\n")
    
    if not largeScreen:
        subprocess.run(["xinput", "map-to-output", "8", "DSI-1"])
    #else:
    #    subprocess.run(["xinput", "map-to-output", "8", "HDMI-1"])
    if isOnline and not checkInternet():
        isOnline = False
    
    
    # Call this function to clear file and reset data for new test
    #clearFile(filename)
    
    # Seconds timer for data logging
    timer = TimerClass(1, incrementSeconds)
    timer.start()
    
    oldActivations = 0
    oldPeople = 0
    activatedPIR = False
    #-------------------------------------Data logging -------------------------------
    with open(filename, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(["Type", "Hours", "Minutes", "Seconds", "Total Activations", "Total People"])
        file.close()

    
    # Initialize dispenser
    disp = dispenser.Dispenser()
    disp.init_GPIO()
    # Initialize LEDs
    leds = LEDs.LEDinit()
    disp.gelUpdate()
    pygame.time.set_timer(BLINKEVENT, 10000, True)
    monsterblinks = [monsterblinkL, monsterblinkM, monsterblinkR]
    
    # Initialize interaction variables
    flow = threading.Thread(target=interaction)
    threadevent = threading.Event() #Used to terminate interaction thread
    trackID = 0 #ID of closest person
    altTrackID = 0 #ID of other random person
    gazeAtClosest = True
    pygame.time.set_timer(GAZEEVENT, 8000, True) #Start gaze event
    videoKeys = [] #IDs of people present at last video showing
    prevKeys = [] #IDs of people present last iteration
    prevInteraction = 0 #What interaction scenario was last run
    #interactionWait = False #Indicate if waiting between interactions
    interactionIndex = 0 #What interaction was last run if repeat interaction scenario
    lastNumberOfActivations = 0 #Activation counter last iteration
    peopleAmount = 1 #len(trackedList)
    frequency = 1    #from trailing_five
    interactionItems = [] #Interaction stages
    runInteraction = False #Turn on/off interactions (r button)
    
    # Initialize stats variables
    st = stattracker.StatTracker()

    oldNumberOfPeople = 0 #People counter last iteration
    numberOfPeople = 0 #People counter this iteration
    
    if largeScreen:
        ## Timer bubbles settings ##
        #Show photo of person who used dispenser
        showPhoto = False
        photoTimer = 0
        BubbleUpdate = 5 #Hz of trackeduser bubble update
        bubbles = []   
        ## Set up infographic images ##
        showimages.imagesInit("images/info/")
        hScale = 1.2
    else:
        hScale = 1.0
    # Set up screen and misc
    pygame.mouse.set_visible(False) #Hide mouse from GUI
    clock = pygame.time.Clock()
    screen = pygame.Surface(size) #Initialize screen
    finalSurface = pygame.display.set_mode(screenSize)#, pygame.NOFRAME) #Final screen because large screen
    pygame.display.toggle_fullscreen()
    
    #top_screen_height = int(largeSize[0]*.7)
    #hScale = 1.2
    top_screen_height = int(size[1]*hScale)
    top_screen_width = largeSize[0]
    
    # Set up text
    myfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 20)
    bubblefont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)
    bigfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 60)
    #handsfont = pygame.freetype.SysFont(
    #header_font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 50)
    #scroll_text = "This is an example of scrolling text moving over the screen"
    #scroll_object = ScrollText(finalSurface, scroll_text, top_screen_height+400, (0,0,255))
    #text_surface, _ = header_font.render("Welcome to Abena", (0,0,0))
    
    yes_rect = pygame.Rect(100-50, top_screen_height+590, 170, 70)
    no_rect = pygame.Rect(offset+50, top_screen_height+590, 170, 70)
    ja_text, _ = bigfont.render("Ja", (0,0,0))
    nej_text, _ = bigfont.render("Nej", (0,0,0))
    
    done = False
    start = time.time()
    while not done:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC")
                    done = True
                elif event.key == pygame.K_r:
                    pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                    runInteraction = not runInteraction
                    print("Run: ", runInteraction)
                elif event.key == pygame.K_o:
                    turnOffDispenser = not turnOffDispenser
                    print(turnOffDispenser)
                elif event.key == pygame.K_a:
                    disp.numberOfActivations += 1
                    print("Activation!")
                elif event.key == pygame.K_f:
                    if frequency == 1: frequency = 10
                    else: frequency = 1
                    print("Frequency: ", frequency)
                elif event.key == pygame.K_p:
                    if peopleAmount == 1: peopleAmount = 10
                    else: peopleAmount = 1
                    print("Number of people: ", peopleAmount)
                elif event.key == pygame.K_v:
                    state = VIDEOSTATE
                elif wizardOfOz:
                    if event.key == pygame.K_w:
                        textList = []
                    else:
                        ozSpeech, textIndex = OzKeydownEvents(event, interactionItems, threadevent, flow, logfile)
                        if ozSpeech is not None and not flow.is_alive():
                            textList = createTextSurface(finalSurface, textIndex, top_screen_height, top_screen_width, wizardOfOz, LANGUAGE)
                            pygame.mixer.init()
                            pygame.mixer.music.load(ozSpeech)
                            pygame.mixer.music.play()
            
            elif event.type == pygame.KEYUP:
                if wizardOfOz:
                    OzKeyupEvents(event)
            # Touchscreen events
            elif event.type == pygame.FINGERDOWN:
                if show_buttons:
                    if event.x*screenSize[0] < nobutton.get_width() and event.y*screenSize[1] < nobutton.get_height()*hScale:
                        print("Left button pressed")
                        interrupted = True
                        no_detected = True
                    if event.x*screenSize[0] > size[0]-yesbutton.get_width() and event.y*screenSize[1] < yesbutton.get_height()*hScale:
                        print("Right button pressed")
                        interrupted = True
                        yes_detected = True
                if event.x*screenSize[0] < 5+menuicon.get_width() and int((size[1]-menuicon.get_height()-20)*hScale) < event.y*screenSize[1] < size[1]*hScale: 
                    if state == MENUSTATE:
                        state = NORMALSTATE
                        pygame.time.set_timer(BLINKEVENT, 15000, True)
                    else: state = MENUSTATE
                elif state == MENUSTATE:
                    if 160 < event.x*screenSize[0] < 160+danishbutton.get_width() and int(100*hScale) < event.y*screenSize[1] < int((100+danishbutton.get_height())*hScale):
                        state = NORMALSTATE
                        if LANGUAGE == "en-US":
                            threadevent.set()
                            LANGUAGE = "da-DK"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            interactionIndex = 0
                    elif 160 < event.x*screenSize[0] < 160+englishbutton.get_width() and int(250*hScale) < event.y*screenSize[1] < int((250+englishbutton.get_height())*hScale):
                        state = NORMALSTATE
                        if LANGUAGE == "da-DK":
                            threadevent.set()
                            LANGUAGE = "en-US"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            interactionIndex = 0
                    elif size[0]-160-coloricon.get_width() < event.x*screenSize[0] < size[0]-160 and int(250*hScale) < event.y*screenSize[1] < int((250+coloricon.get_height())*hScale):
                        state = COLORSTATE
                    elif size[0]-160-onlineicon.get_width() < event.x*screenSize[0] < size[0]-160 and int(100*hScale) < event.y*screenSize[1] < int((100+onlineicon.get_height())*hScale):
                        if isOnline: isOnline = False
                        elif not isOnline and checkInternet(): isOnline = True
                    elif (size[0]-graphicon.get_width())/2 < event.x*screenSize[0] < (size[0]+graphicon.get_width())/2 and int(370*hScale) < event.y*screenSize[1] < int((370+graphicon.get_height())*hScale):
                        plot_data, plot_size = st.get_plot()
                        plot = pygame.image.fromstring(plot_data, plot_size, "RGB")
                        state = GRAPHSTATE
                elif state == COLORSTATE:
                    BACKGROUND = screen.get_at((int(event.x*size[0]), int(size[1]*event.y)))
            """elif event.type == pygame.FINGERMOTION and not multiGestureLock:
                if eyeDesign == "monster": eyeDesign = "normal"
                elif eyeDesign == "normal": eyeDesign = "monster"
                multiGestureLock = True
                pygame.time.set_timer(MULTIEVENT, 1000, True)"""
            ########## User Events ##########
            if state != MENUSTATE:
                if event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 300, True)
                    state = BLINKSTATE2
                elif event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "monster":
                    pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                    state = MONSTERBLINKSTATE
                    random.shuffle(monsterblinks)
                elif event.type == MONSTERBLINKEVENT:
                    if state == MONSTERBLINKSTATE:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE2
                    elif state == MONSTERBLINKSTATE2:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE3
                    elif state == MONSTERBLINKSTATE3:
                        blinktime = random.randrange(5000, 20000, 1000)
                        pygame.time.set_timer(BLINKEVENT, blinktime, True)
                        state = NORMALSTATE
                elif event.type == NORMALEVENT:
                    blinktime = random.randrange(5000, 20000, 1000)
                    pygame.time.set_timer(BLINKEVENT, blinktime, True)
                    state = NORMALSTATE
                elif event.type == HAPPYSTARTEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(HAPPYEVENT, 70, True)
                    state = HAPPYSTATE
                elif event.type == HAPPYEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 1500, True)
                    state = HAPPYSTATE2
                elif event.type == QUESTIONEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 3000, True)
                    state = CONFUSEDSTATE
            if event.type == INTERACTIONEVENT:
                interactionWait = False
                if state == WAITSTATE: state = NORMALSTATE
                print("Interaction timer reset")
            elif event.type == GAZEEVENT:
                gazeAtClosest = not gazeAtClosest
                altTrackID = 0
                if gazeAtClosest:
                    gazeTime = 8000 + random.randrange(-3, 3)*1000
                else:
                    gazeTime = 5000 + random.randrange(-2, 2)*1000
                pygame.time.set_timer(GAZEEVENT, gazeTime, True)
            elif event.type == PHOTOEVENT:
                if bubbles:
                    trackeduser.updateAll(bubbles)
                
        ########## Interaction ##########
        
        #st.trailing_five_min_activations(disp.numberOfActivations)
        frequency = st.trailingFiveMinSum
        #could use pygame.timers to create variable length trailing activations - call function every event
        manyPeople = 3 # Number indicating many people being tracked
        frequentUse = 20 # Number indicating frequent use of dispenser
        waitTimer = 0
        
        if disp.numberOfActivations != lastNumberOfActivations:
            timestamp = dt.datetime.now()
            logfile.write(f"{timestamp}: Activation! Number of activations: {disp.numberOfActivations}\n")
            #lastNumberOfActivations = disp.numberOfActivations
        
        # If in Wizard of Oz test mode
        if wizardOfOz:
            pupilL, pupilR, pupilV = OzMovePupils(pupilL, pupilR, pupilV)
            if disp.numberOfActivations != lastNumberOfActivations:
                timestamp = dt.datetime.now()
                logfile.write(f"{timestamp}: Activation! Number of activations: {disp.numberOfActivations}\n")
                lastNumberOfActivations = disp.numberOfActivations
                pygame.event.post(happyevent)
                
                frame, x, y, h, w = sh.take()
                frame = frame[y:(y+h), x-30:(x+w+30)]
                bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate, frame)) # Adds face to bubbles list
                pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))
                
        elif receiver.poll():
            trackedList, peopleCount, frame = receiver.recv()
            trackedList = {k:v for (k,v) in trackedList.items() if v[4]>5}
            
            if runInteraction:
                keys = trackedList.keys() # IDs of currently tracked people
                recurrents = set(keys) & set(prevKeys) # IDs of people present during last interaction and now
                if not interactionWait and not flow.is_alive() and trackedList:        
                    recurrentsVideo = set(keys) & set(videoKeys)
                    #interactionItems = []
                    
                    # Scenarios
                    if frequency >= frequentUse:           # Scenario 1
                        waitTimer = 30000

                    else:                                  # Scenario 3
                        if not recurrents:
                            interactionIndex = 0
                        else:
                            interactionIndex += 1
                        numberOfNewPeople = len(keys - recurrents)
                        if numberOfNewPeople >= 1:
                            #if prevInteraction == 3: interactionIndex += 1
                            #else: interactionIndex = 0
                            if interactionIndex >= 2: interactionIndex = 0
                            #if interactionIndex == 1:        # 0
                            #    interactionItems.append("nudge")
                            #    interactionItems.append(0)
                            if interactionIndex == 0:      # 1
                                interactionItems.append("novideo")
                                if not recurrentsVideo or len(keys - recurrentsVideo) >= 2:
                                    #interactionItems.append("video")
                                    videoKeys = keys
                                else:
                                    interactionItems.append("countdown")
                            prevKeys = keys
                            waitTimer = 15000
                            #receiver.send((False, False))
                        #else:
                        #    interactionItems.append("educational")
                        numberOfActivationsInteraction = disp.numberOfActivations
                        prevInteraction = 3
                        #waitTimer = 30000
                #if flow.is_alive() and not recurrents: #trackedList:
                    #threadevent.set()
                #    pass
                # track and decay rates important above
                if not interactionItems and not flow.is_alive() and lastNumberOfActivations != disp.numberOfActivations:
                    #pygame.event.post(happyevent)
                    interactionItems.append("30s")
                    prevKeys = keys
                    waitTimer = 8000

                if interactionItems:
                        print("Arguments: ", interactionItems)       
                        flow = threading.Thread(target=interaction, args=interactionItems)
                        flow.start()
                        interactionItems = []
                        #receiver.send((False, False))
                #elif not flow.is_alive():
                #    receiver.send((False, True))
            if waitTimer > 0:
                interactionWait = True
                pygame.time.set_timer(INTERACTIONEVENT, waitTimer, True)
            
            # Gaze calculation and control
            if trackedList:
                if largeScreen and lastNumberOfActivations != disp.numberOfActivations:
                    pygame.event.post(happyevent)
                    userID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                    (x, y, w, h, n, u, c) = trackedList.get(userID)
                    frame = frame[y:(y+h), x-30:(x+w+30)]
                    bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate, frame)) # Adds face to bubbles list
                    pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))
                    #lastNumberOfActivations = disp.numberOfActivations
                    #BOTTOMBACKGROUND = (255,0,0)
                if gazeAtClosest:
                    if altTrackID == 0: # Determine ID of closest person
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                        altTrackID = trackID
                    elif trackID not in trackedList: # If we lose track of ID; look at the new closest
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                else:
                    if altTrackID == 0: # Determine ID of random person
                        peopleList = list(trackedList.keys())
                        if len(peopleList) > 1: # Remove the ID of closest person, then randomly choose ID
                            maxID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                            peopleList.remove(maxID)
                        altTrackID = random.choice(peopleList)
                    if altTrackID in trackedList:
                        trackID = altTrackID
                    else: # If we lose track of ID; look at closest
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]

                (x, y, w, h, n, u, c) = trackedList.get(trackID)
                calculateAngles(x, y, w, h)
                
                if peopleCount > oldNumberOfPeople:
                    newPeople = peopleCount - oldNumberOfPeople
                    numberOfPeople += newPeople
                    oldNumberOfPeople = peopleCount
            
            else:
                if largeScreen and lastNumberOfActivations != disp.numberOfActivations:
                    pygame.event.post(happyevent)
                    bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate)) # Adds face to bubbles list
                    pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))
                    
        lastNumberOfActivations = disp.numberOfActivations
        st.update_plot(disp.numberOfActivations, numberOfPeople)
        """
        irSensors.detectHands(ADC)
        hands = irSensors.getHandList()
        #print(hands)
        if hands[0]:
            yes_detected = True
        elif hands[1]:
            no_detected = True
        #disp.update()
        """
        ########## State Machine ##########
        screen.fill(BACKGROUND)
        
        if state == NORMALSTATE:
            if eyeDesign == "normal":
                blitImages(normalwhiteL, normalwhiteR)
                drawPupils()
                blitImages(normalL, normalR)
            elif eyeDesign == "monster":
                screen.blit(monster, (0,0))
                drawMonsterPupils()
        elif state == BLINKSTATE:
            blitImages(closingwhiteL, closingwhiteR)
            drawPupils()
            blitImages(closingL, closingR)
        elif state == BLINKSTATE2:
            blitImages(closedL, closedR)
        elif state == HAPPYSTATE:
            blitImages(happyL, happyR)
        elif state == HAPPYSTATE2:
            blitImages(happyL, happyR)
        elif state == CONFUSEDSTATE:
            blitImages(confusedLwhite, confusedRwhite)
            drawPupils()
            blitImages(confusedL, confusedR)
        elif state == VIDEOSTATE:
            playVideo()
            state = NORMALSTATE
        elif state == MENUSTATE:
            screen.blit(danishbutton, (160, 100))
            screen.blit(englishbutton, (160, 250))
            screen.blit(coloricon, (size[0]-160-coloricon.get_width(), 250))
            if isOnline: screen.blit(onlineicon, (size[0]-160-onlineicon.get_width(), 100))
            else: screen.blit(offlineicon, (size[0]-160-offlineicon.get_width(), 100))
            screen.blit(graphicon, (400-graphicon.get_width()/2, 370))
            if not flow.is_alive():
                flow = threading.Thread(target=interaction, args=("monster", "normal"))
                flow.start()
            text_surface, _ = myfont.render(f"Activations: {disp.numberOfActivations}", (0,0,0))
            screen.blit(text_surface, (5,5))
        elif state == COLORSTATE:
            screen.blit(colorselector, (50, 50))
        elif state == MONSTERBLINKSTATE:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[0], (0,0))
        elif state == MONSTERBLINKSTATE2:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[1], (0,0))
        elif state == MONSTERBLINKSTATE3:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[2], (0,0))
        elif state == GRAPHSTATE:
            screen.blit(plot, (0,0))
        elif state == WAITSTATE:
            print("Wait state")
            pupilL = 0
            pupilR = 0
            pupilV = -50
            blitImages(normalwhiteL, normalwhiteR)
            drawPupils()
            blitImages(normalL, normalR)
        if show_buttons:
            showButtons()
        
        ''' # Send notification to phone if dispenser almost empty
        if disp.numberOfActivations >= almostEmpty:
            disp.numberOfActivations = 0
            st.pushbullet_notification(typeOfNotification, msg)
            print("Notification sent!")
        '''
        #screen.blit(menuicon, (5, size[1]-50))

        if largeScreen: 
            scalescreen = pygame.transform.smoothscale(screen, (top_screen_width,top_screen_height))
            finalSurface.fill(BACKGROUND)
            finalSurface.blit(scalescreen, (0,0))
            if show_hand_detect:
                finalSurface.blit(handDetectL, (0,largeSize[1]-600+150))
                finalSurface.blit(handDetectR, (500,largeSize[1]-600+150))
                pygame.draw.rect(finalSurface, (255,0,0), yes_rect)
                pygame.draw.rect(finalSurface, (0,255,0), no_rect)
                #finalSurface.blit(nej_text, (100-50+50, top_screen_height+150+10))
                #finalSurface.blit(ja_text, (offset+50+40, top_screen_height+150+10))
                finalSurface.blit(nej_text, (100-50+50, top_screen_height+590+10))
                finalSurface.blit(ja_text, (offset+50+40, top_screen_height+590+10))
            elif textList:
                if showFaceMask:
                    text_offset = 100
                    for txt in textList:
                        finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                        text_offset += 75
                else:
                    text_offset = 0
                    for txt in textList:
                        finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                        text_offset += 75
            elif showScrollingImages:
                showimages.showImage(finalSurface, 0, largeSize[1]-600, 100) #Infographic images
            if showFaceMask:
                finalSurface.blit(facemask, (-150, top_screen_height-50))
                #finalSurface.blit(facemask, (0, top_screen_height-250))#50))
            
            if not showFaceMask and bubbles:
                text_surface, _ = bubblefont.render("Gnid hænderne indtil tiden er udløbet", (0,0,255)) #moi
                finalSurface.blit(text_surface, (200, top_screen_height+50)) #moi
                trackeduser.showAll(bubbles)       #Rub timer bubbles

        else: finalSurface.blit(screen, (0,0))
        pygame.display.flip()
        
        
        #--------------------------Data Logging------------------------------------
        
        if(oldPeople != disp.numberOfPeople):
            writeDataToFile(filename, disp, "Person")
        
        if(oldActivations != disp.numberOfActivations):
            writeDataToFile(filename, disp, "Activation")
        
        oldPeople = disp.numberOfPeople
        oldActivations = disp.numberOfActivations
        
        
    # Cancel the timer for data logging
    timer.cancel()
    
    #Output data from logging in terminal - also stored in csv file in directory
    #readDataToPDframe(filename)
    
    
    
    logfile.close()
    interrupted = True
    threadevent.set()
    if not wizardOfOz:
        receiver.send(True)
        while receiver.poll():  
            (trackedList, peopleCount, frame) = receiver.recv()
        tracking_proc.terminate()
        tracking_proc.join()
    #else:
        #logfile.close()
    pygame.display.quit()
    pygame.quit()
    GPIO.cleanup()
    print("Cleaned up")
    
     #Output data from logging in terminal - also stored in csv file in directory
    readDataToPDframe(filename)
    
    exit(0)



