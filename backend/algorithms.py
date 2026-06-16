'''
The different autofocusing algorithms
'''
import numpy as np
from pynq import PYNQ
from scipy.optimize import curve_fit
from PIL import Image
from sklearn.metrics import r2_score
import logging

def gauss(x, a, b, c):
    '''
    Function used to fit sharpness vs steps
    '''
    return a*np.exp(- ((x-b)**2)/(2*(c**2)))
def doubleGauss(x, a, b, c, d, e, f):
    return gauss(x, a, b, c)+gauss(x, d, e, f)
import scipy 

class Algorithms:
    def __init__(self,
            pynq: PYNQ,
            positions: np.ndarray,
            sharpness: np.ndarray):
        self.algos = ['increment', 'hillClimbing', 'sweepAndClimb', 'doubleGaussAndClimb']
        self.pynq = pynq
        self.positions = positions
        self.sharpness = sharpness

        self.num_iterations = 0

        self.increment_steps = 8e3
        
        self.hill_climb_increment = 500
        self.decrease_in_steps = -2 #divides the amount of steps taken by this number. 
        # should always be negative to turn the image around.
        self.smallest_steps = 2

        #the prominance used for climb and stop.
        self.set_prominence = 3
    def moveNextStep(self,
                     algo: str) -> int:
        assert algo in self.algos

        next_pos = -1
        self.num_iterations += 1
        match algo:
            case 'increment':
                next_pos = self.increment()
            case 'hillClimbing':
                next_pos = self.hillClimbing()
            case 'sweepAndClimb':
                next_pos = self.sweepAndClimb()
            case 'doubleGaussAndClimb':
                next_pos = self.doubleGaussAndClimb()

        if next_pos != -1:
            self.pynq.moveAbsoluteSteps(next_pos)
        return next_pos

    def increment(self) -> int:
        '''
        Goes through the whole range in equal sized steps. Returns absolute steps
        '''

        return self.pynq.mot_absolute_steps + self.increment_steps
    def hillClimbing(self) -> int:
        
        if abs(self.hill_climb_increment) < self.smallest_steps:
            return -1 # Peak found with smallest_steps accuracy
        
        if len(self.positions) < 2:
            return self.pynq.mot_absolute_steps + self.hill_climb_increment
        
        if self.sharpness[-1] < self.sharpness[-2]: # Reverse direction, half the step size
            self.hill_climb_increment = int(self.hill_climb_increment/self.decrease_in_steps)
        return self.pynq.mot_absolute_steps + self.hill_climb_increment
    def sweepAndClimb(self) -> int:
        next_pos = -1
        if self.num_iterations < 10:
            self.increment_steps = self.pynq.MOT_LIMITS[1]/10
            next_pos = self.increment()
        elif self.num_iterations == 10:
            next_pos = self.positions[self.sharpness.index(max(self.sharpness))]
        else:
            next_pos = self.hillClimbing()

        return next_pos
    def SweepStopClimb(self) -> int:
        next_pos = -1
        peaks, properties = scipy.find_peaks(self.posistions, prominence=0)
        if properties["prominence"][-1]>=self.set_prominence:
            next_pos = self.hillClimbing()
        elif self.num_iterations < 10:
            self.increment_steps = self.pynq.MOT_LIMITS[1]/10
            next_pos = self.increment()
        elif self.num_iterations == 10:
            next_pos = self.positions[self.sharpness.index(max(self.sharpness))]
        else:
            next_pos = self.hillClimbing()
        return next_pos


    def doubleGaussAndClimb(self) -> int:
        next_pos = -1
        if self.num_iterations < 10:
            self.increment_steps = self.pynq.MOT_LIMITS[1]/10
            next_pos = self.increment()
        elif self.num_iterations == 10:       
            try:
                popt, pcov = curve_fit(doubleGauss,
                                    self.positions,
                                    self.sharpness,
                                    p0=(3.5, 18e3, 1e3, 1, 40e3, 2e3))
                perr = np.sqrt(np.diag(pcov))
                r_squared = r2_score(self.sharpness, doubleGauss(self.positions, *popt))
                logging.info(f'{popt} R^2: {r_squared}')

                fit_positions = np.linspace(np.min(self.positions), np.max(self.positions), num=int(np.max(self.positions)-np.min(self.positions)))
                fit_sharpness = doubleGauss(fit_positions, *popt)

                biggest_peak   = max(popt[0], popt[3])
                biggest_peak_i = np.where(popt == biggest_peak)
                next_pos       = popt[int(biggest_peak_i[0][0])+1]
                
            except RuntimeError:
                logging.error('Optimal not found')
                next_pos = self.positions[self.sharpness.index(max(self.sharpness))]
        else:
            next_pos = self.hillClimbing()

        return next_pos
