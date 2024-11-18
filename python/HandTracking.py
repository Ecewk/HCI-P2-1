import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = "gesture_recognizer.task"
BaseOptions = python.BaseOptions
GestureRecognizer = vision.GestureRecognizer
GestureRecognizerOptions = vision.GestureRecognizerOptions
GestureRecognizerResult = vision.GestureRecognizerResult
VisionRunningMode = vision.RunningMode

#[[Category(index=-1, score=0.7852272391319275, display_name='', category_name='Open_Palm')]] <- gestures
#[[Category(index=0, score=0.9727259278297424, display_name='Right', category_name='Right')]] <- handedness
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    #print('gesture recognition result: {}'.format(result))
    if not result.gestures:
        print("No hand(s) detected")
    else:
        print(result.gestures[0][0].category_name)
        print(result.handedness[0][0].category_name)

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)
recognizer = vision.GestureRecognizer.create_from_options(options)


def recog_gestures(img):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    recognition_result = recognizer.recognize_async(mp_image, int(time.time() * 1000))
    return recognition_result

#Function to draw hand skeletons on the image if hands are located
#https://www.analyticsvidhya.com/blog/2021/07/building-a-hand-tracking-system-using-opencv/
#https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python#live-stream
#https://medium.com/@oetalmage16/a-tutorial-on-finger-counting-in-real-time-video-in-python-with-opencv-and-mediapipe-114a988df46a
def drawHands(img):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for _, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)
            
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    return img

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    while True:
        framenum = cap.get(cv2.CAP_PROP_POS_FRAMES); 
        success, img = cap.read()

        #img = drawHands(img)
        recognition_result = recog_gestures(img)

        img = cv2.flip(img, 1)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break