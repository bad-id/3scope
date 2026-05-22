from pyflow import extensity
from camera import Camera
from pynq import PYNQ
import numpy as np
import logging
from io import StringIO
import time

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
        
        if (camera.connect() and pynq.connect()):
            logging.info(f'PYNQ connected with idn: {pynq.idn}')
            pynq.initMot()

    def getCamera(self) -> Camera:
        return camera
    def getPynq(self) -> PYNQ:
        return pynq
    def getImage(self) -> np.ndarray:
        return image
    def getLogs(self) -> str:
        return logStream.getvalue()
    def generateRandom(self) -> None:
        pynq.moveAbsoluteSteps(5000)