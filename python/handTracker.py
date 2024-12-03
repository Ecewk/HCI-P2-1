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
global thissock

def send_scene(scene):
    global thissock
    data = scene
    thissock.sendto(data.encode("utf-8"), ("127.0.0.1", 25001))


def change_hand(hand, gesture):
    global righthand
    global lefthand
    if hand == 0:
        if righthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("jungle")
            print("Switch to jungle scene")
        if righthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        righthand = gesture
    elif hand == 1:
        if lefthand == "Closed_Fist" and gesture == "Open_Palm":
            send_scene("water")
            print("Switch to water scene")
        if lefthand == "Open_Palm" and gesture == "Closed_Fist":
            send_scene("main")
            print("Switch to main scene")
        lefthand = gesture

def handle_result(result, output_image: mp.Image, timestamp_ms: int):
    if not result.gestures:
        change_hand(1, "")
        change_hand(0, "")
    else:
        if result.handedness[0][0].category_name == "Left" and result.gestures[0][0].category_name != "None":
            change_hand(1, result.gestures[0][0].category_name)
        elif result.handedness[0][0].category_name == "Right" and result.gestures[0][0].category_name != "None":
            change_hand(0, result.gestures[0][0].category_name)

options = GestureRecognizerOptions(
base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
running_mode=RunningMode.LIVE_STREAM,
result_callback=handle_result)
recognizer = GestureRecognizer.create_from_options(options)

class handTrackerClass:
    def __init__(self, sock) -> None:
        global thissock
        thissock = sock
    
    def recog_gestures(self, img):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        recognizer.recognize_async(mp_image, int(time.time() * 1000))

    
