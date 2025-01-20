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


def change_hand(hand, gesture):
    global righthand
    global lefthand
    if hand == 0:
        #if you are in main you can switch to jungle
        if righthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("jungle")
            print("Switch to jungle scene")
        #if you are in jungle you can switch to main
        if righthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        #righthand = gesture
    elif hand == 1:
        #if you are in main you can switch to water
        if lefthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("water")
            print("Switch to water scene")
        #if you are in water you can switch to main
        if lefthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        #lefthand = gesture

def handle_result(result, output_image: mp.Image, timestamp_ms: int):
    a = True
    global righthand
    global lefthand
            # #right hand open palm = jungle
            # righthand = "Closed_Fist"
            # change_hand(0,"Open_Palm")
            # #right hand closed fist = main
            # righthand = "Open_Palm"
            # change_hand(0,"Closed_Fist")
            # #left hand open palm = water
            # lefthand = "Closed_Fist"
            # change_hand(1,"Open_Palm")
            # #left hand closed fist = main
            # lefthand = "Open_Palm"
            # change_hand(1,"Closed_Fist")
    if i%2== 0:#switch to main
        if a:#from water to main bcs a true
            lefthand = "Open_Palm"
            change_hand(1,"Closed_Fist")
            a = False
        else:#from jungle to main bcs a false
            righthand = "Open_Palm"
            change_hand(0,"Closed_Fist")
            a = True
        i+=1
    elif not a:#a false so switch to jungle
        righthand = "Closed_Fist"
        change_hand(0,"Open_Palm")
        i+=1
    else:#a true so switch to water
        lefthand = "Closed_Fist"
        change_hand(1,"Open_Palm")
        i+=1
    #wait for 10 seconds
    time.sleep(10)


options = GestureRecognizerOptions(
base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
running_mode=RunningMode.LIVE_STREAM,
num_hands=2,
result_callback=handle_result)
recognizer = GestureRecognizer.create_from_options(options)

class handTrackerClass:
    def __init__(self, sock) -> None:
        global thissock
        thissock = sock
    
    def recog_gestures(self, img):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        recognizer.recognize_async(mp_image, int(time.time() * 1000))
    
