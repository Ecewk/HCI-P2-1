import numpy as np
import open3d as o3d
import time
import psutil
import os

"""
This is Open3D
Generally its good and is a 3d scene library. 
"""

# Measure startup time
start_time = time.time()

def generate_random_point_cloud(num_points=5000, num_shapes=1):
    # Initialize an empty list to store all points
    points = []
    
    # Generate multiple shapes
    for _ in range(num_shapes):
        # Randomly choose a shape type
        shape_type = np.random.choice(['sphere', 'cube', 'plane'])
        # Calculate number of points for this shape
        shape_points = num_points // num_shapes
        
        if shape_type == 'sphere':
            # Generate points on a sphere
            radius = np.random.uniform(0.5, 1.0)
            theta = np.random.uniform(0, 2*np.pi, shape_points)
            phi = np.random.uniform(0, np.pi, shape_points)
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
        elif shape_type == 'cube':
            # Generate points in a cube
            x = np.random.uniform(-1, 1, shape_points)
            y = np.random.uniform(-1, 1, shape_points)
            z = np.random.uniform(-1, 1, shape_points)
        else:  # plane
            # Generate points on a plane (z=0)
            x = np.random.uniform(-1, 1, shape_points)
            y = np.random.uniform(-1, 1, shape_points)
            z = np.zeros(shape_points)
        
        # Generate a random center for the shape
        shape_center = np.random.uniform(-5, 5, 3)
        # Add the shape's points to the main list, offsetting by the shape's center
        points.extend(np.column_stack((x, y, z)) + shape_center)
    
    # Convert the list of points to a numpy array and return
    return np.array(points)

#%% Random Experiments
# Generate random point cloud with 10000 points and 8 shapes
point_cloud = generate_random_point_cloud(10000, 8)

# Create Open3D point cloud object
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_cloud)

# Initialize performance metrics
process = psutil.Process(os.getpid())
response_times = []
memory_usages = []
frame_count = 0
start_time = time.time()

# Function to measure performance
def measure_performance():
    global frame_count, start_time

    frame_start_time = time.time()

    # Measure memory usage
    memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
    memory_usages.append(memory_usage)

    frame_count += 1

    # Print metrics every second
    if time.time() - start_time >= 1.0:
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        avg_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0
        print(f"FPS: {frame_count}")
        print(f"Average Response Time: {avg_response_time} seconds")
        print(f"Average Memory Usage: {avg_memory_usage} MB")

        # Reset metrics
        response_times.clear()
        memory_usages.clear()
        frame_count = 0
        start_time = time.time()

    frame_end_time = time.time()
    response_time = frame_end_time - frame_start_time
    response_times.append(response_time)

# Visualize the point cloud and measure performance
vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(pcd)

print(f"Startup Time: {time.time() - start_time} seconds")

while vis.poll_events():
    vis.update_renderer()
    measure_performance()

vis.destroy_window()