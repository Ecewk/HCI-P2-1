from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3
import time
import psutil
import os

"""
    This is Panda3D
    Generally not bad but idk about the graphic quality feels like there are better options
"""

# Measure startup time
start_time = time.time()

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load a 3D model
        self.model = self.loader.loadModel("models/environment")
        self.model.reparentTo(self.render)

        # Position the model
        self.model.setPos(Point3(0, 50, -100))

        # Initialize performance metrics
        self.process = psutil.Process(os.getpid())
        self.response_times = []
        self.memory_usages = []
        self.frame_count = 0
        self.start_time = time.time()

        # Task to measure FPS and response time
        self.taskMgr.add(self.measure_performance, "measurePerformance")

        print(f"Startup Time: {time.time() - start_time} seconds")

    def measure_performance(self, task):
        frame_start_time = time.time()

        # Measure memory usage
        memory_usage = self.process.memory_info().rss / (1024 * 1024)  # in MB
        self.memory_usages.append(memory_usage)

        self.frame_count += 1

        # Print metrics every second
        if task.time >= 1.0:
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            avg_memory_usage = sum(self.memory_usages) / len(self.memory_usages) if self.memory_usages else 0
            print(f"FPS: {self.frame_count}")
            print(f"Average Response Time: {avg_response_time} seconds")
            print(f"Average Memory Usage: {avg_memory_usage} MB")

            # Reset metrics
            self.response_times = []
            self.memory_usages = []
            self.frame_count = 0
            task.time = 0

        frame_end_time = time.time()
        response_time = frame_end_time - frame_start_time
        self.response_times.append(response_time)

        return task.cont

app = MyApp()
app.run()