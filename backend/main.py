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
        exposure_time = 7e3
        camera.set_exposure(exposure_time)

        plt.ion()
        positions = []
        sharpness = []

        fig, ax = plt.subplots()
        ax.set_xlabel("Amount of steps")
        ax.set_ylabel("Tenengrad rating with blur")
        ax.set_title("Amount of steps against Tenengrad with blur")
        graph = ax.plot(positions, sharpness, 'x', color = 'g')[0]

        pynq.moveToZero()
        frame = camera.get_frame()
        positions.append(pynq.mot_absolute_steps)

        gray = camera.gaussian_blur(frame)
        sharp = camera.tenengrad(gray)
        sharpness.append(sharp)

        step_size = 1e3
        for i in range(20):
            pynq.moveRelativeSteps(step_size)

            frame = camera.get_frame()
            positions.append(pynq.mot_absolute_steps)

            gray = camera.gaussian_blur(frame)
            sharp = camera.tenengrad(gray)
            sharpness.append(sharp)

            graph.remove()
            graph = ax.plot(positions, sharpness, 'x', color = 'g')[0]
            plt.pause(0.0001)
            #logging.info(sharpness, positions)

        logging.info(sharpness[-1])
        
        print('Stopped')

        plt.ioff()
        plt.show()
    
    else:
        logging.error("Error connecting")