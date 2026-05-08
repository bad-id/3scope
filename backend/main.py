import pynq
from autofocus import autofocus
from camera import Camera

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    camera = Camera() 

    print(pynq.idn)
    pynq.initMot()
    pynq.moveToZero()

    autofocus(
        pynq,
        camera,
        110,
        100, 50)
    print('Stopped')