from camera import Camera
from pynq import PYNQ

def autofocus(wanted_sharpness):
    #initiate camera and PYNQ object
    pynq = PYNQ()
    camera = Camera()
    #initialise frequentie
    #get an image
    image = camera.get_frame()
    #get a sharpness value
    focus_value = camera.check_sharpness(image)
    while focus_value < wanted_sharpness:
        
        PYNQ.startMoving(Direction)




