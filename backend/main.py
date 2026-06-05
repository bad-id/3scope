'''
Displays live plot of camera and sharpness parameter
'''

import pynq
from autofocus import autofocus
from camera import Camera
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

iterations = 40
exposure_time = 3e3
step_size = 1e3

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)  
    camera = Camera()
    if (camera.connect() and pynq.connect()):
        logging.info(pynq.idn)
        pynq.initMot()

        camera.start()
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
        line1, = ax1.plot([], [], 'x', color = 'g')

        ax2.set_title("Image")
        ax2.set_axis_off()

        pynq.moveToZero()
        frame = camera.get_frame()
        positions.append(pynq.mot_absolute_steps)

        gray = camera.gaussian_blur(frame)
        sharp = camera.tenengrad(gray)
        sharpness.append(sharp)

        im = ax2.imshow(frame)

        def init(): 
            line1.set_data(positions, sharpness)
            im.set_data(frame)
            return line1,
        
        def animate(i): 
            pynq.moveRelativeSteps(step_size)

            frame = camera.get_frame()
            
            positions.append(pynq.mot_absolute_steps)

            gray = camera.gaussian_blur(frame)
            sharp = camera.tenengrad(gray)
            sharpness.append(sharp)
            line1.set_data(positions, sharpness)

            ax1.set_xlim(positions[0], positions[-1])
            ax1.set_ylim(np.min(sharpness), np.max(sharpness))
            
            im.set_array(frame)
            return line1, im

        anim = FuncAnimation(fig, animate, init_func = init,
                            frames = iterations, interval = 0, repeat=False)


        #plt.show()
        logging.info(sharpness[-1])
        
        try:
            plt.show()
            logging.info('Closed plot')
        except KeyboardInterrupt:
            logging.error('Stopped by keyboard')
        pynq.moveToZero()

        #plt.ioff()
    
    else:
        logging.error("Error connecting")