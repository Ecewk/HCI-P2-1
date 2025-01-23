import time
import cv2

global thissock

class eyeTrackerClass:
    def __init__(self, sock) -> None:
        # Load pre-trained classifiers for detecting faces
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Initialize variables for smoothing and tracking
        self.last_x, self.last_y = 0, 0
        self.last_sent_x, self.last_sent_y = None, None  # Last sent coordinates
        self.alpha = 0.2  # Smoothing factor
        self.send_interval = 0.0001  # Time interval to send data (in seconds)
        self.last_send_time = time.time()
        self.change_threshold = 0.5  # Minimum change threshold for sending data
        global thissock
        thissock = sock

    def send_position(self, frame):
        # Flip the frame horizontally to mirror it
        frame = cv2.flip(frame, 1)

        # Convert frame to grayscale (necessary for detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:  # Ensure at least one face is detected
            # Use the first detected face
            (x, y, w, h) = faces[0]

            # Calculate the center of the detected face
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Smooth the coordinates using a simple low-pass filter
            smoothed_x = int(self.alpha * face_center_x + (1 - self.alpha) * self.last_x)
            smoothed_y = int(self.alpha * face_center_y + (1 - self.alpha) * self.last_y)

            # Update last coordinates
            self.last_x, self.last_y = smoothed_x, smoothed_y

            # Calculate Z based on face size (dummy value for now)
            z_value = 0

            # Invert Y coordinate
            inverted_y = 700 - smoothed_y

            # Check if the change in coordinates exceeds the threshold
            if (self.last_sent_x is None or self.last_sent_y is None or
                    abs(smoothed_x - self.last_sent_x) > self.change_threshold or
                    abs(smoothed_y - self.last_sent_y) > self.change_threshold):

                # Send the smoothed coordinates to the server at a fixed interval
                if time.time() - self.last_send_time > self.send_interval:
                    data = f"{smoothed_x},{inverted_y},{z_value}"  # Include z value
                    thissock.sendto(data.encode("utf-8"), ("127.0.0.1", 25001))
                    self.last_send_time = time.time()

                    # Update last sent coordinates
                    self.last_sent_x, self.last_sent_y = smoothed_x, smoothed_y


        cv2.waitKey(1)