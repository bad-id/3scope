import pynq
from autofocus import autofocus
from camera import Camera

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    pynq.connect()
    camera = Camera()
    pynq.connect() 

    print(pynq.idn)
    pynq.initMot()
    pynq.moveToZero()

    pynq.moveRelativeSteps(10000)

    print('Stopped')