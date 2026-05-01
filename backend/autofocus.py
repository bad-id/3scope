from camera import Camera
from pynq import PYNQ
import numpy as np

def autofocus(wanted_sharpness : float, number_steps : int, decrease_in_steps : int):
    """
    This function automatically finds the best position for the lens to get a good image in the lens
    :param: wanted_sharpness
    :use: sets a limit on when the focus is good enough to stop.
    :param: number_steps
    :use: the number of steps you want the first step to be.
    :param: decrease_in_steps
    :use: How much you want the steps to decrease when the focus values start dropping.
    The new amount of steps is given by previous number of steps divided by the decrease in steps.
    """
    #initiate camera and PYNQ object
    pynq = PYNQ()
    camera = Camera()
    #initialise frequentie and direction
    direction = 0
    frequency = 4500
    #get an image
    image = camera.get_frame()
    #get a sharpness value
    focus_value = camera.check_sharpness(image)
    focus_values_array = []
    focus_values_array.append(focus_value)
    i = 1
    while focus_value < wanted_sharpness:
        if i == 1:
            #Make the motor move
            PYNQ.startMoving(direction, number_steps, frequency)
            #get an image
            image = camera.get_frame()
            #get a sharpness value
            focus_value = camera.check_sharpness(image)
            focus_values_array.append(focus_value)
            i = i +1
        if i > 1:
            if focus_values_array[i] > focus_values_array[i-1]:
                #Make the motor move
                PYNQ.startMoving(direction, number_steps, frequency)
                #get an image
                image = camera.get_frame()
                #get a sharpness value
                focus_value = camera.check_sharpness(image)
                focus_values_array.append(focus_value)
                i = i + 1
            if focus_values_array[i] < focus_values_array[i-1]:
                if direction == 0:
                    direction = 1
                if direction == 1:
                    direction = 0
                number_steps = number_steps/decrease_in_steps
                #Make the motor move
                PYNQ.startMoving(direction, number_steps, frequency)
                #get an image
                image = camera.get_frame()
                #get a sharpness value
                focus_value = camera.check_sharpness(image)
                focus_values_array.append(focus_value)
                i = i + 1
    return camera.get_frame()
        




