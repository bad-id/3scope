import pynq
from autofocus import autofocus
from camera import Camera
import logging
import numpy as np
import matplotlib.pyplot as plt
import time


if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    camera = Camera()
    if (camera.connect() and pynq.connect()):
        logging.info(pynq.idn)
        pynq.initMot()

        camera.start()
        exposure_time = 3e3
        camera.set_exposure(exposure_time)

        #plt.ion()
        positions = []
        sharpness = []

        fig, (ax1, ax2) = plt.subplots(1,2)
        fig.set_figwidth(16)
        fig.set_figheight(4)
        fig.canvas.draw()
        plt.show(block=False)

        ax1.set_xlabel("Amount of steps")
        ax1.set_ylabel("Tenengrad rating with blur")
        ax1.set_title("Amount of steps against Tenengrad with blur")
        li, = ax1.plot(positions, sharpness, 'x', color = 'g')

        ax2.set_title("Image")
        ax2.set_axis_off()

        pynq.moveToZero()
        frame = camera.get_frame()
        positions.append(pynq.mot_absolute_steps)

        gray = camera.gaussian_blur(frame)
        sharp = camera.tenengrad(gray)
        sharpness.append(sharp)

        step_size = 1e3
        for i in range(30):
            pynq.moveRelativeSteps(step_size)

            frame = camera.get_frame()
            ax2.imshow(frame)
            positions.append(pynq.mot_absolute_steps)

            gray = camera.gaussian_blur(frame)
            sharp = camera.tenengrad(gray)
            sharpness.append(sharp)
            
            li.set_xdata(positions)
            li.set_ydata(sharpness)

            ax1.relim() 
            ax1.autoscale_view(True,True,True) 

            fig.canvas.draw()
            
            plt.pause(0.0001)
            #logging.info(sharpness, positions)

        logging.info(sharpness[-1])
        
        pynq.moveToZero()
        print('Stopped')

        #plt.ioff()
        plt.show()
    
    else:
        logging.error("Error connecting")