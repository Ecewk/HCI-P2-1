import numpy as np
from vispy import app, gloo
from vispy.gloo import Program, VertexBuffer, IndexBuffer
import cv2
import mediapipe as mp
import pyautogui

"""
this is visPy
THIS ONE IS MY FAVOURITE AND IS WORKING NICELY AND SMOOTHLY AND I MADE COPILOT ALSO IMPLEMENT EYETRACKING
"""
# Vertex shader
vertex_shader = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
attribute vec3 position;
attribute vec4 color;
varying vec4 v_color;
void main()
{
    v_color = color;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

# Fragment shader
fragment_shader = """
varying vec4 v_color;
void main()
{
    gl_FragColor = v_color;
}
"""

# Cube vertices and colors
vertices = np.array([
    [-1, -1, -1], [+1, -1, -1], [+1, +1, -1], [-1, +1, -1],
    [-1, -1, +1], [+1, -1, +1], [+1, +1, +1], [-1, +1, +1]
], dtype=np.float32)

colors = np.array([
    [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 0, 1],
    [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1], [0, 0, 0, 1]
], dtype=np.float32)

# Cube indices
indices = np.array([
    [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
    [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6],
    [0, 3, 7], [0, 7, 4], [1, 2, 6], [1, 6, 5]
], dtype=np.uint32)

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        self.program = Program(vertex_shader, fragment_shader)
        self.vertices = VertexBuffer(vertices)
        self.colors = VertexBuffer(colors)
        self.indices = IndexBuffer(indices)
        self.program['position'] = self.vertices
        self.program['color'] = self.colors
        self.theta_x = 0
        self.theta_y = 0

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        gloo.set_state(clear_color='black', depth_test=True)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)

        # Initialize eye-tracking components
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.screen_w, self.screen_h = pyautogui.size()

        self.show()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)
        self.projection = np.array([
            [1.0 / (width / height), 0, 0, 0],
            [0, 1.0, 0, 0],
            [0, 0, -2.0 / (50.0 - 0.1), -(50.0 + 0.1) / (50.0 - 0.1)],
            [0, 0, 0, 1.0]
        ], dtype=np.float32)

    def on_draw(self, event):
        gloo.clear()
        self.program['model'] = self.model
        self.program['view'] = self.view
        self.program['projection'] = self.projection
        self.program.draw('triangles', self.indices)

    def on_timer(self, event):
        self.track_eye_movement()
        
        self.model = np.array([
            [np.cos(self.theta_y), 0, np.sin(self.theta_y), 0],
            [np.sin(self.theta_x) * np.sin(self.theta_y), np.cos(self.theta_x), -np.sin(self.theta_x) * np.cos(self.theta_y), 0],
            [-np.cos(self.theta_x) * np.sin(self.theta_y), np.sin(self.theta_x), np.cos(self.theta_x) * np.cos(self.theta_y), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        self.update()

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
                pyautogui.mouseDown(button='left')

            # Update rotation angles based on eye position
            self.theta_x = np.pi * (landmarks[1].y - 0.5)
            self.theta_y = np.pi * (landmarks[1].x - 0.5)

if __name__ == '__main__':
    canvas = Canvas()
    app.run()