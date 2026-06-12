from camera import Camera
from pynq import PYNQ
import numpy as np


def autofocus(
        wanted_sharpness: float,
        number_steps: int,
        decrease_in_steps: int,
        max_iterations: int):
    """
    This function automatically finds the best position for the lens to get a good image in the lens
    :param: wanted_sharpness
    :use: sets a limit on when the focus is good enough to stop using the tenengrad sharpness scale.
    :param: number_steps
    :use: the number of steps you want the first step to be.
    :param: decrease_in_steps
    :use: How much you want the steps to decrease when the focus values start dropping.
    The new amount of steps is given by previous number of steps divided by the decrease in steps.
    :param: max_iterations
    :use: sets a limit on how many times the moter can turn around and decrease in steps.
    """
    #initialise frequentie and direction
    direction = 1
    camera = Camera()
    pynq=PYNQ()
    #get an image
    camera.start()
    image = camera.get_frame()
    #get a sharpness value
    focus_value = camera.tenengrad(image)
    focus_values_array = []
    focus_values_array.append(focus_value)
    i = 0
    while focus_value < wanted_sharpness and i < max_iterations:
        if i == 0:
            #Make the motor move
            pynq.moveRelativeSteps(direction*number_steps)
            #get an image
            image = camera.get_frame()
            #get a sharpness value
            focus_value = camera.tenengrad(image)
            focus_values_array.append(focus_value)
            i = i +1
        if i > 0:
            if focus_values_array[i] > focus_values_array[i-1]:
                #Make the motor move
                pynq.moveRelativeSteps(direction*number_steps)
                #get an image
                image = camera.get_frame()
                #get a sharpness value
                focus_value = camera.tenengrad(image)
                focus_values_array.append(focus_value)
                i = i + 1
            elif focus_values_array[i] < focus_values_array[i-1]:
                direction *=-1
                number_steps = int(number_steps/decrease_in_steps)
                #Make the motor move
                pynq.moveRelativeSteps(direction*number_steps)
                #get an image
                image = camera.get_frame()
                #get a sharpness value
                focus_value = camera.tenengrad(image)
                focus_values_array.append(focus_value)
                i = i + 1
    return camera.get_frame()

def main():
    autofocus()

if __name__ == "__main__":
    main()
        




