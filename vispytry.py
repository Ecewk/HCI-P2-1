import numpy as np
from vispy import app, gloo
from vispy.gloo import Program, VertexBuffer, IndexBuffer
import pyautogui
import time
import psutil
import os
import GPUtil

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

# Measure startup time
start_time = time.time()

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
        self.fps_timer = app.Timer(1.0, connect=self.calculate_fps, start=True)
        self.frame_count = 0

        self.process = psutil.Process(os.getpid())

        self.response_times = []
        self.cpu_usages = []
        self.memory_usages = []
        self.gpu_usages = []
        self.gpu_memory_usages = []

        self.show()
        print(f"Startup Time: {time.time() - start_time} seconds")

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
        self.frame_count += 1

    def on_timer(self, event):
        start_time = time.time()
        self.track_mouse_movement()
        
        self.model = np.array([
            [np.cos(self.theta_y), 0, np.sin(self.theta_y), 0],
            [np.sin(self.theta_x) * np.sin(self.theta_y), np.cos(self.theta_x), -np.sin(self.theta_x) * np.cos(self.theta_y), 0],
            [-np.cos(self.theta_x) * np.sin(self.theta_y), np.sin(self.theta_x), np.cos(self.theta_x) * np.cos(self.theta_y), 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        self.update()
        response_time = time.time() - start_time
        self.response_times.append(response_time)

        cpu_usage = self.process.cpu_percent(interval=None)
        memory_usage = self.process.memory_info().rss / (1024 * 1024)  # in MB
        self.cpu_usages.append(cpu_usage)
        self.memory_usages.append(memory_usage)

        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            self.gpu_usages.append(gpu.load * 100)
            self.gpu_memory_usages.append(gpu.memoryUsed)

    def track_mouse_movement(self):
        mouse_x, mouse_y = pyautogui.position()
        screen_w, screen_h = pyautogui.size()

        # Update rotation angles based on mouse position
        self.theta_x = np.pi * (mouse_y / screen_h - 0.5)
        self.theta_y = np.pi * (mouse_x / screen_w - 0.5)

    def calculate_fps(self, event):
        print(f"FPS: {self.frame_count}")
        self.frame_count = 0

        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            print(f"Average Response Time: {avg_response_time} seconds")
            self.response_times = []

        if self.cpu_usages:
            avg_cpu_usage = sum(self.cpu_usages) / len(self.cpu_usages)
            print(f"Average CPU Usage: {avg_cpu_usage}%")
            self.cpu_usages = []

        if self.memory_usages:
            avg_memory_usage = sum(self.memory_usages) / len(self.memory_usages)
            print(f"Average Memory Usage: {avg_memory_usage} MB")
            self.memory_usages = []

        if self.gpu_usages:
            avg_gpu_usage = sum(self.gpu_usages) / len(self.gpu_usages)
            print(f"Average GPU Usage: {avg_gpu_usage}%")
            self.gpu_usages = []

        if self.gpu_memory_usages:
            avg_gpu_memory_usage = sum(self.gpu_memory_usages) / len(self.gpu_memory_usages)
            print(f"Average GPU Memory Usage: {avg_gpu_memory_usage} MB")
            self.gpu_memory_usages = []

if __name__ == '__main__':
    # Measure library size
    vispy_path = os.path.dirname(app.__file__)
    library_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(vispy_path) for filename in filenames)
    print(f"Library Size: {library_size / (1024 * 1024)} MB")

    canvas = Canvas()
    app.run()