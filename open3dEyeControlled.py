import cv2
import mediapipe as mp
import pyautogui
import open3d as o3d
import numpy as np

class EyeTracking3DScene:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.screen_w, self.screen_h = pyautogui.size()

        self.left_click_held = False

        self.pcd = self.generate_scene()
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        self.vis.add_geometry(self.pcd)

        self.view_control = self.vis.get_view_control()

    def generate_scene(self):
        point_cloud = self.generate_random_point_cloud(10000, 8)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(point_cloud)
        return pcd

    def generate_random_point_cloud(self, num_points=5000, num_shapes=1):
        points = []
        for _ in range(num_shapes):
            shape_type = np.random.choice(['sphere', 'cube', 'plane'])
            shape_points = num_points // num_shapes

            if shape_type == 'sphere':
                radius = np.random.uniform(0.5, 1.0)
                theta = np.random.uniform(0, 2 * np.pi, shape_points)
                phi = np.random.uniform(0, np.pi, shape_points)
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.sin(phi) * np.sin(theta)
                z = radius * np.cos(phi)
            elif shape_type == 'cube':
                x = np.random.uniform(-1, 1, shape_points)
                y = np.random.uniform(-1, 1, shape_points)
                z = np.random.uniform(-1, 1, shape_points)
            else:
                x = np.random.uniform(-1, 1, shape_points)
                y = np.random.uniform(-1, 1, shape_points)
                z = np.zeros(shape_points)

            shape_center = np.random.uniform(-5, 5, 3)
            points.extend(np.column_stack((x, y, z)) + shape_center)

        return np.array(points)

    def track_eye_movement(self):
        ret, frame = self.cam.read()
        if not ret:
            return

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
                    self.left_click_held = True


    def run(self):
        while self.vis.poll_events():
            self.track_eye_movement()
            self.vis.update_geometry(self.pcd)
            self.vis.update_renderer()
        self.cam.release()
        self.vis.destroy_window()


app = EyeTracking3DScene()
app.run()
