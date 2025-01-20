import cv2
import socket
from coordinateHandTracker import handTrackerClass
from coordinateSender import coordinateSenderClass

if __name__ == "__main__":
    # Host and port for the TCP connection
    host, port = "127.0.0.1", 25001

    # Initialize the TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.sendto("jungle".encode("utf-8"), ("127.0.0.1", 25001))

    print("Start up hand tracking")
    myHandtracker = handTrackerClass(sock)
    print("Start up eye tracking")
    myEyetracker = coordinateSenderClass(sock)
    

    a = False
    b = False
    while True:
        if a:
            myHandtracker.recog_gestures()
            a = False
        elif b:
            myHandtracker.send_jungle()
            b = False
        #myHandtracker.recog_gestures()
        myEyetracker.send_position()
        
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            print("Exiting")
            exit()