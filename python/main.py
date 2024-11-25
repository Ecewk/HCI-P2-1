import socket
import cv2
import time

# Host and port for the TCP connection
host, port = "127.0.0.1", 25001

# Initialize the TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    sock.connect((host, port))

    # Start capturing video from the webcam
    cap = cv2.VideoCapture(0)

    # Load pre-trained classifier for detecting eyes
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    # Initialize variables for smoothing
    last_x, last_y = 0, 0
    alpha = 0.2  # Smoothing factor
    send_interval = 0.1  # Time interval to send data (in seconds)
    last_send_time = time.time()

    while True:
        # Read frame from the webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally to mirror it
        frame = cv2.flip(frame, 1)

        # Convert frame to grayscale (necessary for eye detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect eyes in the frame
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)

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
            smoothed_x = int(alpha * avg_x + (1 - alpha) * last_x)
            smoothed_y = int(alpha * avg_y + (1 - alpha) * last_y)

            # Update last coordinates
            last_x, last_y = smoothed_x, smoothed_y

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
            
            #print("X,Y: ", last_x, " ", last_y)
            #print("Smoothed X,Y: ", smoothed_x," ", smoothed_y)
            #average_x = sum(center[0] for center in eye_centers) // len(eye_centers)
            #average_y = sum(center[1] for center in eye_centers) // len(eye_centers)
            #print("Average X,Y: ", average_x, " ", average_y)

            # Send the smoothed coordinates to the server at a fixed interval
            if time.time() - last_send_time > send_interval:
                try:
                    data = f"{smoothed_x},{inverted_y},{z_value}"  # Include z value
                    sock.sendall(data.encode("utf-8"))
                    last_send_time = time.time()
                except socket.error:
                    print("Connection lost. Exiting...")
                    break  # Exit the loop if the connection is broken

        # Display the frame with detected eyes
        cv2.imshow('Eye Tracking - Mirrored', frame)

        # Break the loop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    sock.close()




# import cv2
# import socket
# from handTracker import handTrackerClass
# from eyeTracker import eyeTrackerClass


# if __name__ == "__main__":    
#     # Host and port for the TCP connection
#     host, port = "127.0.0.1", 25001

#     # Initialize the TCP socket
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     print("Start up hand tracking")
#     myHandtracker = handTrackerClass(sock)
#     myEyetracker = eyeTrackerClass(sock)

#     try:
#         # Connect to the server
#         sock.connect((host, port))

#         cap = cv2.VideoCapture(0)
#         while True:
#             ret, img = cap.read()
#             if not ret:
#                 break

#             myHandtracker.recog_gestures(img)
#             #myEyetracker.send_eyes_position(img)

#             img = cv2.flip(img, 1)
#             #cv2.imshow("Image", img)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
    
#     except socket.error:
#         print("Start unity project")

#     finally:
#         # Release resources
#         sock.close()