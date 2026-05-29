import pynq
from autofocus import autofocus
from camera import Camera
import logging
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    camera = Camera()
    if (camera.connect() and pynq.connect()):
        logging.info(pynq.idn)
        pynq.initMot()

        camera.start()
        exposure_time = 5000
        camera.set_exposure(exposure_time)

        plt.ion()
        positions = []
        sharpness = []

        fig, ax = plt.subplots()
        line,  = ax.plot(positions, sharpness, 'x')

        pynq.moveToZero()
        frame = camera.get_frame()
        positions.append(pynq.mot_absolute_steps)
        sharpness.append(camera.check_sharpness(frame))

        line.set_xdata(positions)
        line.set_ydata(sharpness)
        ax.relim()
        ax.autoscale_view()
        plt.draw()

        slope = 0.1
        step_size = 50e3
        while abs(slope*step_size) >= 1:
            pynq.moveRelativeSteps(int(slope*step_size))

            frame = camera.get_frame()
            positions.append(pynq.mot_absolute_steps)
            sharpness.append(camera.check_sharpness(frame))

            line.set_xdata(positions)
            line.set_ydata(sharpness)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            #logging.info(sharpness, positions)

            slope = (sharpness[-1]-sharpness[-2])/(positions[-1]-positions[-2])
            logging.info(slope)
        logging.info(sharpness[-1])

        
        print('Stopped')

        plt.ioff()
        plt.show()
    
    else:
        logging.error("Error connecting")