import cv2
import numpy as np
from pypylon import pylon
from camera import Camera
import pynq
from pynq import PYNQ
import pyvisa
from math import floor
import time
import os
import matplotlib.pyplot as plt

def final_code(iterations):
    # Initialize hardware
    camera = Camera()
    camera.connect()
    camera.start()
    pynq = pynq.PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 5000
    camera.set_exposure(exposure_time)

    steps = (pynq.MOT_LIMITS[1] - 5000) / iterations
    relative_size = 10
    zoomed_steps = 5
    steps_small = steps / relative_size
    sharpness_data = np.zeros(iterations)
    zoomed_data = np.zeros(total_small_iterations)
    total_small_iterations = 2 * zoomed_steps * relative_size 
    

    for i in range(0, iterations):
        frame = camera.get_frame()

        if frame is None:
            continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        sharpness_data[i] = sharpness

        pynq.moveRelativeSteps(steps)

    max_index = np.argmax(sharpness_data)
    max_steps = max_index * steps

    pynq.moveToZero()
    pynq.moveRelativeSteps(max_steps)
    pynq.moveRelativeSteps((-1/2 * total_small_iterations) * steps_small)

    for i in range(0, total_small_iterations):
        frame = camera.get_frame()

        if frame is None:
                continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        zoomed_data[i] = sharpness

        pynq.moveRelativeSteps(steps_small)

    max_sharpness_index = np.argmax(zoomed_data)
    pynq.moveRelativeSteps(-total_small_iterations * steps_small)
    pynq.moveRelativeSteps(max_sharpness_index * steps_small)

    camera.run()

    


