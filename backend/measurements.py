import cv2
import numpy as np
from pypylon import pylon
from camera import Camera
from pynq import PYNQ

camera = Camera()
pynq = PYNQ()

# Initialize arrays
steps = np.array()
sharpness = np.array()

pynq.moveToZero()

