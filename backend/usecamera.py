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
    camera = Camera()
    camera.connect()
    pynq = pynq.PYNQ(DEBUG=False)
    pynq.connect()
    pynq.initMot()
    exposure_time = 5000
    camera.set_exposure(exposure_time)

    camera.run()