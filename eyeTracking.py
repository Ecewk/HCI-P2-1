import cv2
import mediapipe as mp

class EyeTracking:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    def track_eye_movement(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame = cv2.flip(frame, 1)  
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            output = self.face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w, _ = frame.shape

            if landmark_points:
                landmarks = landmark_points[0].landmark

                for id, landmark in enumerate(landmarks[474:478]):  
                    x = int(landmark.x * frame_w)
                    y = int(landmark.y * frame_h)

                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)  

                    if id == 1:
                        cv2.putText(frame, f"Eye Coords: ({x}, {y})", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow('Eye Tracking', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = EyeTracking()
    tracker.track_eye_movement()
