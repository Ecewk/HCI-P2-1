import cv2
import mediapipe as mp

model_path = "Models\gesture_recognizer.task"

#Function to draw hand skeletons on the image if hands are located
#https://www.analyticsvidhya.com/blog/2021/07/building-a-hand-tracking-system-using-opencv/
#https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python#live-stream
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
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = drawHands(img)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break