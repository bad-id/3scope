from pyflow import extensity
from camera import Camera
from pynq import PYNQ
import numpy as np

camera: Camera     = Camera()
pynq:   PYNQ       = None
image:  np.ndarray = None

@extensity
class SystemManager:
    '''
    Describes the whole microscope setup. Used to interface with frontend
    '''

    def __init__(self):
        if camera.connected == False:
            camera.connect()

    def getCamera(self) -> Camera:
        return camera
    def getPynq(self) -> PYNQ:
        return pynq
    def getImage(self) -> np.ndarray:
        return image