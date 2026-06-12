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
    """
    This function is a complete implementation of an autofocus algorithm.
    It sweeps the entire range of the translation stage roughly and looks
    for the highest sharpness rating. Then it moves to that point and checks
    the local neighbourhood with smaller steps to find the absolute peak sharpness.
    """

    # Initialize hardware
    camera = Camera()
    camera.connect()
    camera.start()
    pynq = PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 5e3
    camera.set_exposure(exposure_time)

    # Sweep settings
    steps = (pynq.MOT_LIMITS[1] - 5000) / iterations # -5000 to make sure the translation stage remains within bounds
    relative_size = 10 # Relative size of the small stepsize compared to the big stepsize (1/relative_size)
    zoomed_steps = 5 # Amount of smallsteps in each direction from the rough peak
    steps_small = steps / relative_size
    sharpness_data = np.zeros(iterations)
    
    total_small_iterations = 2 * zoomed_steps * relative_size # Total small steps
    zoomed_data = np.zeros(total_small_iterations)
    
    pynq.moveToZero()
    for i in range(0, iterations):
        """
        This section performs the rough sweep of the range
        """
        frame = camera.get_frame()

        if frame is None:
            continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        # Compute sharpness rating
        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        sharpness_data[i] = sharpness
        print(sharpness)

        pynq.moveRelativeSteps(steps)

    max_index = np.argmax(sharpness_data) # Find highest value for sharpness
    best_rough_point = max_index * steps # Best translation stage position
    print(best_rough_point)
    # Finish rough stage, move to the sharpness point
    pynq.moveAbsoluteSteps(best_rough_point)

    for i in range(0, total_small_iterations):
        """
        This section sweeps the local neighbourhood of the peak sharpness
        """
        frame = camera.get_frame()

        if frame is None:
                continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)

        # Compute sharpness rating
        gray = camera.gaussian_blur(frame)
        sharpness = camera.tenengrad(gray)
        zoomed_data[i] = sharpness
        print(sharpness)

        pynq.moveRelativeSteps(steps_small)

    max_sharpness_index = np.argmax(zoomed_data) # Find final peak sharpness
    # Move to the best sharpness point
    pynq.moveAbsoluteSteps(best_rough_point + max_sharpness_index*steps_small)

if __name__ == '__main__':
     """
     This executes the autofocus algorithm.
     """
     final_code(200)  


