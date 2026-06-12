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
    """
    This program only initializes the camera so we can use it to setup our system.
    """
    camera = Camera()
    camera.connect()
    pynq = pynq.PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 1e3
    camera.set_exposure(exposure_time)

    camera.run()