import cv2
import numpy as np
from pypylon import pylon
from camera import Camera
from pynq import PYNQ
import pyvisa
from math import floor
import time # temporary
import os

# Initialize hardware
camera = Camera()
camera.start()
pynq = PYNQ()

# Measurement settings
total_measurements = 100
steps_per_measurement = pynq.MOT_LIMITS[1] / total_measurements

# Initialize arrays
steps_list = np.zeros(total_measurements)
sharpness_list = np.zeros(total_measurements)

pynq.moveToZero()   

for i in range(0, total_measurements):
    steps_list[i] = i * steps_per_measurement
    frame = camera.get_frame()
    sharpness = camera.check_sharpness(frame)
    sharpness_list[i] = sharpness
    pynq.moveRelativeSteps(steps_per_measurement)

data = np.column_stack((steps_list, sharpness_list))

BASE_DIR = os.path.dirname(__file__)          # .../backend
PROJECT_DIR = os.path.dirname(BASE_DIR)       # .../project
DATA_DIR = os.path.join(PROJECT_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

file_path = os.path.join(DATA_DIR, "output.txt")

np.savetxt(file_path, data)