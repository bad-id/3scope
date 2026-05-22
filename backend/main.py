import pynq
from autofocus import autofocus
from camera import Camera
import logging

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    camera = Camera()
    if (camera.connect() and pynq.connect()):
        logging.info(pynq.idn)
        pynq.initMot()

        #pynq.moveToZero()
        #pynq.moveRelativeSteps(10000)
        pynq.moveAbsoluteSteps(24950)
        print('Stopped')
    
    else:
        logging.error("Error connecting")