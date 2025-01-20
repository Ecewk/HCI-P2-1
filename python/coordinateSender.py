import socket
import time
import cv2

global thissock
cont = True
i = 0

class coordinateSenderClass:
    def __init__(self, sock) -> None:
        self.i = 0
        file = "coordinates.txt"
        # Load pre-trained classifiers for detecting faces
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Initialize variables for smoothing and tracking
        self.last_x, self.last_y = 0, 0
        self.last_sent_x, self.last_sent_y = None, None  # Last sent coordinates
        #self.alpha = 0.2  # Smoothing factor
        self.send_interval = 0.0001  # Time interval to send data (in seconds)
        self.last_send_time = time.time()
        self.change_threshold = 0.5  # Minimum change threshold for sending data
        global thissock
        thissock = sock

    def send_position(self,frame):
        inverted_y = 0
        smoothed_x = 0
        smoothed_y = 0
        z_value = 0
        #read the coordinates on he i'th line, get x as smoothed x, y as smoothed y
        with open("coordinates.txt", "r") as file:
            lines = file.readlines()
            if len(lines) >= self.i:
                line = lines[self.i]
                self.i += 1
                line = line.strip()
                x, y, z = line.split(",")
                smoothed_x = int(x)
                inverted_y = int(y)
                z_value = int(z)
            # else:
            #     cont = False
            smoothed_y = 700 - inverted_y
            # Update last coordinates
            self.last_x, self.last_y = smoothed_x, smoothed_y

            # Check if the change in coordinates exceeds the threshold
            if (self.last_sent_x is None or self.last_sent_y is None or
                    abs(smoothed_x - self.last_sent_x) > self.change_threshold or
                    abs(smoothed_y - self.last_sent_y) > self.change_threshold):

                # Send the smoothed coordinates to the server at a fixed interval
                if time.time() - self.last_send_time > self.send_interval:
                    #############THIS IS WHERE YOU SEND THEM AND HAVE THE CURRENT COORDINATES
                    data = f"{smoothed_x},{inverted_y},{z_value}"  # Include z value
                    thissock.sendto(data.encode("utf-8"), ("127.0.0.1", 25001))
                    self.last_send_time = time.time()

                    # Update last sent coordinates
                    self.last_sent_x, self.last_sent_y = smoothed_x, smoothed_y
        
        cv2.waitKey(1)
        
    def stop_or_no(self):
        return cont
