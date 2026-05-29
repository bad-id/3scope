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
    pynq = PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 5e3
    camera.set_exposure(exposure_time)

    steps = (pynq.MOT_LIMITS[1] - 5000) / iterations
    relative_size = 10
    zoomed_steps = 5
    steps_small = steps / relative_size
    sharpness_data = np.zeros(iterations)
    
    total_small_iterations = 2 * zoomed_steps * relative_size 
    zoomed_data = np.zeros(total_small_iterations)
    
    pynq.moveToZero()
    for i in range(0, iterations):
        frame = camera.get_frame()

        if frame is None:
            continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        #sharpness = camera.check_sharpness(frame)
        sharpness_data[i] = sharpness
        print(sharpness)

        pynq.moveRelativeSteps(steps)

    max_index = np.argmax(sharpness_data)
    best_rough_point = max_index * steps
    print(best_rough_point)
    # Finish rough stage, move to the sharpness point
    pynq.moveAbsoluteSteps(best_rough_point)

    for i in range(0, total_small_iterations):
        frame = camera.get_frame()

        if frame is None:
                continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        zoomed_data[i] = sharpness
        print(sharpness)

        pynq.moveRelativeSteps(steps_small)

    max_sharpness_index = np.argmax(zoomed_data)
    # Move to the best sharpness point
    pynq.moveAbsoluteSteps(best_rough_point + max_sharpness_index*steps_small)

if __name__ == '__main__':
     final_code(200)  


