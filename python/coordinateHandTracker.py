import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import cv2
import time
import socket
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer
from mediapipe.tasks.python.vision import GestureRecognizerOptions
from mediapipe.tasks.python.vision import RunningMode

righthand = ""
lefthand = ""
i =0
global thissock

def send_scene(scene):
    global thissock
    data = scene
    thissock.sendto(data.encode("utf-8"), ("127.0.0.1", 25001))
    
    print("Sent scene: ", scene)


def change_hand(hand, gesture, rh, lh):
    righthand = rh
    lefthand = lh
    if hand == 0:
        #if you are in main you can switch to jungle
        if righthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("jungle")
            print("Switch to jungle scene")
        #if you are in jungle you can switch to main
        if righthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        righthand = gesture
    elif hand == 1:
        #if you are in main you can switch to water
        if lefthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("water")
            print("Switch to water scene")
        #if you are in water you can switch to main
        if lefthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        lefthand = gesture

class handTrackerClass:
    def __init__(self, sock) -> None:
        global thissock
        thissock = sock
    
    def recog_gestures(self):#you cant wait for input because its making everyone wait
        #count five seconds and change scene after
        send_scene("main")
        
    def send_jungle(self):
        send_scene("jungle")
        

    
