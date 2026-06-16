'''
Displays live plot of camera and sharpness parameter, tries fitting a gauss curve
'''

from pynq import PYNQ
from autofocus import autofocus
from camera import Camera
from algorithms import Algorithms
import logging
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.optimize import curve_fit
from PIL import Image
from sklearn.metrics import r2_score
import time

class Config():
    def __init__(self,
                 FIT_live: bool,
                 iterations: int,
                 start_point: int,
                 exposure_time: int,
                 step_size: int,
                 blur: int,
                 algo: str):
        self.FIT_live: bool = FIT_live
        self.iterations: int = iterations
        self.start_point: int = start_point
        self.exposure_time: int = exposure_time
        self.step_size: int = step_size
        self.blur: int = blur
        self.algo: str = algo

exposure_time = 1e3
configs: list[Config] = [
    Config(False, 30, 0, exposure_time, 8e3, 101, 'SweepStopClimb'),
    Config(False, 30, 0, exposure_time, 8e3, 101, 'sweepAndClimb'),
    Config(False, 100, 0, exposure_time, 400, 101, 'increment'),
] 

FIT_LIVE = False
iterations = 30
start_point = 0#10e3
exposure_time = 2e3
step_size = 8e3
blur = 101 # Must be odd number
algo = 'SweepStopClimb'
#algo = 'doubleGaussAndClimb'
#algo = 'sweepAndClimb'
#algo = 'increment'
#algo = 'hillClimbing'

# Folder structure: ../data/setup[setup number per journal]/YYYY_MM_DD/[slide offset]/[nr. of measurement]
base_folder = '../data/setup4/2026_06_16/plus10mm'#'../data/trash2'#'../data/setup4/2026_06_12/plus0mm'
save_img = True

folder = ''
popt, pcov = [0, 0, 0], []
blur_matrix = (blur,blur)

anim = None

def cc(filename: str) -> str:
    '''
    Shorthand concat filename
    '''
    return os.path.join(folder, filename)

def gauss0(x, a, b, c):
    '''
    Function used to fit sharpness vs steps
    '''
    return a*np.exp(- ((x-b)**2)/(2*(c**2)))
def gauss(x, a, b, c, d, e, f):
    return gauss0(x, a, b, c)+gauss0(x, d, e, f)


def run_with_global_conf(pynq: PYNQ,
                         camera: Camera):
    os.makedirs(folder)
    os.mkdir(cc('img'))

    # Init logging
    infofile          = logging.FileHandler(cc('info.log'))
    logging.getLogger().addHandler(infofile)
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f'Files will be save in {folder}')

    # Initialize the PYNQ board and camera
    positions = []
    sharpness = []
    times = []

    algorithms = Algorithms(pynq=pynq,
                            positions=positions,
                            sharpness=sharpness)
    algorithms.increment_steps = step_size
    if True:#(camera.connect() and pynq.connect()):
        camera.set_exposure(exposure_time)

        fig, (ax1, ax2) = plt.subplots(1,2)
        fig.set_figwidth(16)
        fig.set_figheight(4)
        fig.canvas.draw()
        plt.show(block=False)

        ax1.set_xlabel("Amount of steps")
        ax1.set_ylabel("Tenengrad rating with blur")
        ax1.set_title("Amount of steps against Tenengrad with blur")
        line1, = ax1.plot([], [], 'x', color = 'g')
        fit_line, = ax1.plot([], [], color = 'r')

        ax2.set_title("Image")
        ax2.set_axis_off()

        pynq.moveToZero()
        pynq.moveAbsoluteSteps(start_point)
        frame = camera.get_frame()
        start_time = time.time()
        times.append(0)
        
        positions.append(pynq.mot_absolute_steps)

        gray = camera.gaussian_blur(frame, blur=blur_matrix)
        sharp = camera.tenengrad(gray)
        sharpness.append(sharp)

        im = ax2.imshow(frame)

        def init(): 
            line1.set_data(positions, sharpness)
            fit_line.set_data([], [])
            im.set_data(frame)
            return line1, fit_line, im
        
        def animate(i): 
            #pynq.moveRelativeSteps(step_size)
            new_pos = algorithms.moveNextStep(algo=algo)
            frame = camera.get_frame()
            if new_pos >= 0:
                times.append(time.time()-start_time)
                if save_img:
                    Image.fromarray(frame).save(cc(f'img/{str(i)}.jpg'))
                
                positions.append(pynq.mot_absolute_steps)

                gray = camera.gaussian_blur(frame, blur=blur_matrix)
                sharp = camera.tenengrad(gray)
                sharpness.append(sharp)
                line1.set_data(positions, sharpness)

                ax1.set_xlim(positions[0], positions[-1])
                ax1.set_ylim(np.min(sharpness), np.max(sharpness))

            # Fit a gauss curve
            if FIT_LIVE == True or new_pos == -1:
                if len(sharpness) > 6:
                    try:
                        popt, pcov = curve_fit(gauss,
                                            positions,
                                            sharpness,
                                            p0=(3.5, 18e3, 1e3, 1, 40e3, 2e3))
                        perr = np.sqrt(np.diag(pcov))
                        r_squared = r2_score(sharpness, gauss(positions, *popt))
                        logging.info(f'{popt} R^2: {r_squared}')

                        fit_positions = np.linspace(np.min(positions), np.max(positions), num=int(np.max(positions)-np.min(positions)))
                        fit_sharpness = gauss(fit_positions, *popt)
                        fit_line.set_data(fit_positions, fit_sharpness)
                    except RuntimeError:
                        logging.error('Optimal not found')

            if new_pos == -1:
                logging.info('Algo converged, paused')
                if FIT_LIVE:
                    anim.pause()
                else:
                    plt.close()
            # Update image            
            im.set_array(frame)
            return line1, fit_line, im

        anim = FuncAnimation(fig, animate, init_func = init,
                            frames = iterations, interval = 0, repeat=False)
        
        try:
            plt.show()
            logging.info('Closed plot')
        except KeyboardInterrupt:
            logging.error('Stopped by keyboard')

        # Save data and reset
        logging.info('Saving data')
        fig.savefig(cc('tenegrad_vs_steps.png'))

        df = pd.DataFrame({ 'Position, steps' : positions,
                            'Sharpness, -'    : sharpness,
                            'Time, s'         : times})
        df.to_csv(cc('sharpness.csv'))
        
        pynq.moveToZero()
    
    else:
        logging.error("Error connecting")
    
if __name__ == '__main__':
    # Initialize folder structure
    pynq = PYNQ(DEBUG=False)  
    camera = Camera()
    if (camera.connect() and pynq.connect()):
        pass
    logging.info(pynq.idn)
    pynq.initMot()

    camera.start()

    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    nr_of_measurement = 1
    subfolders = [ int(f.name) for f in os.scandir(base_folder) if f.is_dir() ]
    if len(subfolders) > 0:
        nr_of_measurement = max(subfolders) +1 # Increment folder name by one

    for config in configs:
        FIT_LIVE = config.FIT_live
        iterations = config.iterations
        start_point = config.start_point
        exposure_time = config.exposure_time
        step_size = config.step_size
        blur = config.blur # Must be odd number
        algo = config.algo

        folder = os.path.join(base_folder, str(nr_of_measurement), algo)
        run_with_global_conf(pynq, camera)