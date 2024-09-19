from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3
import cv2
import mediapipe as mp
import pyautogui

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.model = self.loader.loadModel("models/environment")
        self.model.reparentTo(self.render)

        self.model.setPos(Point3(0, 50, -100))

        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.screen_w, self.screen_h = pyautogui.size()

        self.left_click_held = False
        
        self.taskMgr.add(self.track_eye_movement, "TrackEyeMovement")
    
    
    def track_eye_movement(self, task):
        
        ret, frame = self.cam.read()
        if not ret:
            return task.cont

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

                if id == 1:  
                    screen_x = int(self.screen_w * landmark.x)
                    screen_y = int(self.screen_h * landmark.y)
                    pyautogui.moveTo(screen_x, screen_y)

            left_eye = [landmarks[145], landmarks[159]]

            if (left_eye[0].y - left_eye[1].y) < 0.004:
                if not self.left_click_held:
                    pyautogui.mouseDown(button='left')


        return task.cont

app = MyApp()
app.run()
