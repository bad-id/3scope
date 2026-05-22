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
<<<<<<< HEAD
        pynq.moveAbsoluteSteps(24950)
        print('Stopped')
=======
        pynq.moveAbsoluteSteps(10000)
        pynq.moveAbsoluteSteps(5000)
        logging.info('Stopped')
>>>>>>> 809209688b1c03d03ae64ba313d60fa6eee4ea35
    
    else:
        logging.error("Error connecting")