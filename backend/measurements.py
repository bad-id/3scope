import cv2
import numpy as np
from pypylon import pylon
from camera import Camera
from pynq import PYNQ
import pyvisa
from math import floor
import time # temporary
import os
import matplotlib.pyplot as plt


# Initialize hardware
camera = Camera()
camera.start()
pynq = PYNQ()
pynq.initMot()
exposure_time = 5000
camera.set_exposure(exposure_time)

# Measurement settings
total_measurements = 100
steps_per_measurement = (pynq.MOT_LIMITS[1] - 5000) / total_measurements

# Initialize arrays
steps_list = np.zeros(total_measurements)
sharpness_list = np.zeros(total_measurements)

pynq.moveToZero()   

# Perform measurement
for i in range(0, total_measurements):
    steps_list[i] = i * steps_per_measurement
    frame = camera.get_frame()
    if frame is None:
        continue

    cv2.imshow("Basler Camera", frame)
    cv2.waitKey(1)
    
    sharpness = camera.check_sharpness(frame)
    sharpness_list[i] = sharpness
    pynq.moveRelativeSteps(steps_per_measurement)

camera.stop()
pynq.moveToZero()

data = np.column_stack((steps_list, sharpness_list))

BASE_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(BASE_DIR)

MEAS_DIR = os.path.join(PROJECT_DIR, "data", "measurement")
os.makedirs(MEAS_DIR, exist_ok=True)

# Save data
file_path = os.path.join(MEAS_DIR, "output.txt")
np.savetxt(file_path, data)

# Plot
plt.plot(steps_list, sharpness_list)
plt.xlabel("Amount of steps")
plt.ylabel("Sharpness rating")
plt.title("Amount of steps against Sharpness")

# Save
graph_path = os.path.join(MEAS_DIR, "graph.png")
plt.savefig(graph_path, dpi=300, bbox_inches="tight")

# Then show
plt.show()
