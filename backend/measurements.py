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


if __name__ == '__main__':
    # Initialize hardware
    camera = Camera()
    camera.connect()
    camera.start()
    pynq = pynq.PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 3e3
    camera.set_exposure(exposure_time)

    # Measurement settings
    total_measurements = 50
    steps_per_measurement = (pynq.MOT_LIMITS[1] - 5000) / total_measurements

    # Initialize arrays
    steps_list = np.zeros(total_measurements)
    sharpness_list = np.zeros(total_measurements)
    tenengrad_list = np.zeros(total_measurements)
    tenengrad_and_gaussianblur_list = np.zeros(total_measurements)

    pynq.moveToZero()  

    # Perform measurement
    for i in range(0, total_measurements):
        steps_list[i] = i * steps_per_measurement
        frame = camera.get_frame()
        if frame is None:
            continue

        cv2.imshow("Basler Camera", frame)
        cv2.waitKey(1)
        
        # Apply Gaussian blur
        gray = camera.gaussian_blur(frame)
 
        # Check sharpness with three different methods
        sharpness = camera.check_sharpness(frame)
        tenengrad = camera.tenengrad(frame)
        tenengrad_and_gaussianblur = camera.tenengrad(gray)

        # Add sharpness to list
        sharpness_list[i] = sharpness
        tenengrad_list[i] = tenengrad
        tenengrad_and_gaussianblur_list[i] = tenengrad_and_gaussianblur

        pynq.moveRelativeSteps(steps_per_measurement)

    camera.stop()
    pynq.moveToZero()

    # Prepare data for saving and graphing
    data = np.column_stack((steps_list, sharpness_list))
    data_tenengrad = np.column_stack((steps_list, tenengrad_list))
    data_tenengrad_gaussianblur = np.column_stack((steps_list, tenengrad_and_gaussianblur_list))

    BASE_DIR = os.path.dirname(__file__)
    PROJECT_DIR = os.path.dirname(BASE_DIR)

    MEAS_DIR = os.path.join(PROJECT_DIR, "data", "measurement")
    os.makedirs(MEAS_DIR, exist_ok=True)

    # Save datasets
    sharpness_file = os.path.join(MEAS_DIR, "sharpness_data.txt")
    tenengrad_file = os.path.join(MEAS_DIR, "tenengrad_data.txt")
    tenengrad_and_gaussianblur_file = os.path.join(MEAS_DIR, "tenengrad_and_gaussianblur_data.txt")

    np.savetxt(sharpness_file, data)
    np.savetxt(tenengrad_file, data_tenengrad)
    np.savetxt(tenengrad_and_gaussianblur_file, data_tenengrad_gaussianblur)

    # Plot Sharpness against amount of steps
    plt.figure()

    plt.plot(steps_list, sharpness_list)
    plt.xlabel("Amount of steps")
    plt.ylabel("Sharpness rating")
    plt.title("Amount of steps against Sharpness")

    sharpness_graph = os.path.join(MEAS_DIR, "sharpness_graph.png")
    plt.savefig(sharpness_graph, dpi=300, bbox_inches="tight")

    # Plot Tenengrad against amount of steps
    plt.figure()

    plt.plot(steps_list, tenengrad_list)
    plt.xlabel("Amount of steps")
    plt.ylabel("Tenengrad rating")
    plt.title("Amount of steps against Tenengrad")

    tenengrad_graph = os.path.join(MEAS_DIR, "tenengrad_graph.png")
    plt.savefig(tenengrad_graph, dpi=300, bbox_inches="tight")

    # Plot Tenengrad with gaussian blur against amount of steps
    plt.figure()

    plt.plot(steps_list, tenengrad_and_gaussianblur_list)
    plt.xlabel("Amount of steps")
    plt.ylabel("Tenengrad rating with blur")
    plt.title("Amount of steps against Tenengrad with blur")

    tenengrad_graph = os.path.join(MEAS_DIR, "tenengrad_with_blur_graph.png")
    plt.savefig(tenengrad_graph, dpi=300, bbox_inches="tight")

    # Show all figures
    plt.show()