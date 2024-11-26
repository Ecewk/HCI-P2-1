import cv2
import socket
from handTracker import handTrackerClass
from eyeTracker import eyeTrackerClass

if __name__ == "__main__":    
    # Host and port for the TCP connection
    host, port = "127.0.0.1", 25001

    # Initialize the TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Start up hand tracking")
    myHandtracker = handTrackerClass(sock)
    myEyetracker = eyeTrackerClass(sock)

    try:
        # Connect to the server
        sock.connect((host, port))

        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            if not ret:
                break

            myHandtracker.recog_gestures(img)
            myEyetracker.send_eyes_position(img)

            img = cv2.flip(img, 1)
            #cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except socket.error:
        print("Start unity project")

    finally:
        # Release resources
        sock.close()