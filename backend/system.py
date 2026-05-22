from pyflow import extensity
from camera import Camera
from pynq import PYNQ
import numpy as np
import logging
from io import StringIO

camera: Camera     = Camera()
pynq:   PYNQ       = PYNQ()
image:  np.ndarray = []

logStream: StringIO = StringIO()
logHandler          = logging.StreamHandler(logStream)
logging.getLogger().addHandler(logHandler)
logging.getLogger().setLevel(logging.DEBUG)

@extensity
class SystemManager:
    '''
    Describes the whole microscope setup. Used to interface with frontend
    '''

    def __init__(self):
        logging.debug('Init SystemManager')
        
        if camera.connected == False:
            camera.connect()
        print(f'Logs: ')

    def getCamera(self) -> Camera:
        return camera
    def getPynq(self) -> PYNQ:
        return pynq
    def getImage(self) -> np.ndarray:
        return image
    def getLogs(self) -> str:
        return logStream.getvalue()
    