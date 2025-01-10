import socket
import time
import cv2

global thissock

class eyeTrackerClass:
    def __init__(self, sock) -> None:
        # Load pre-trained classifier for detecting eyes
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        # Initialize variables for smoothing
        self.last_x, self.last_y = 0, 0
        self.alpha = 0.2  # Smoothing factor
        self.send_interval = 0.2  # Time interval to send data (in seconds)
        self.last_send_time = time.time()
        global thissock
        thissock = sock
    
    def send_eyes_position(self, frame):
        # Flip the frame horizontally to mirror it
        frame = cv2.flip(frame, 1)

        # Convert frame to grayscale (necessary for eye detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect eyes in the frame
        eyes = self.eye_cascade.detectMultiScale(gray, 1.3, 5)

        if len(eyes) >= 2:  # Ensure at least two eyes are detected
            eye_centers = []
            z_values = []  # List to hold eye sizes for Z calculation
            for (x, y, w, h) in eyes[:2]:  # Get only the first two eyes
                eye_center_x = x + w // 2
                eye_center_y = y + h // 2
                eye_centers.append((eye_center_x, eye_center_y))
                z_values.append(w * h)  # Use area as an estimate of distance

                # Draw a circle at the center of the detected eye
                cv2.circle(frame, (eye_center_x, eye_center_y), 10, (0, 255, 0), 2)

            # Calculate the average coordinates of the detected eyes
            avg_x = sum(center[0] for center in eye_centers) // len(eye_centers)
            avg_y = sum(center[1] for center in eye_centers) // len(eye_centers)

            # Smooth the coordinates using a simple low-pass filter
            smoothed_x = int(self.alpha * avg_x + (1 - self.alpha) * self.last_x)
            smoothed_y = int(self.alpha * avg_y + (1 - self.alpha) * self.last_y)

            # Update last coordinates
            self.last_x, self.last_y = smoothed_x, smoothed_y

            # Calculate Z based on eye sizes (smaller size means closer)
                        # Calculate Z based on eye sizes (smaller size means closer)
            #TODO: if z_values:
            #     avg_size = sum(z_values) / len(z_values)
            #             # Use a constant to scale the Z value
            #     scale_factor = -100000  # Adjust this value as needed
            #     z_value = 100 + scale_factor / avg_size  # Linear scaling
            # else:
            #     z_value = 0  # Default value if no eyes are detected

            z_value = 0

            # Invert Y coordinate
            inverted_y = 700 - smoothed_y

            # Send the smoothed coordinates to the server at a fixed interval
            if time.time() - self.last_send_time > self.send_interval:
                data = f"{smoothed_x},{inverted_y},{z_value}"  # Include z value
                thissock.sendto(data.encode("utf-8"), ("127.0.0.1", 25001))
                self.last_send_time = time.time()
                    