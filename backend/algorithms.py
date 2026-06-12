'''
The different autofocusing algorithms
'''
import numpy as np
from pynq import PYNQ

class Algorithms:
    def __init__(self,
            pynq: PYNQ,
            positions: np.ndarray,
            sharpness: np.ndarray):
        self.algos = ['increment', 'hillClimbing']
        self.pynq = pynq
        self.positions = positions
        self.sharpness = sharpness

        self.increment_steps = 500
        self.hill_climb_increment = 500
        self.decrease_in_steps = -4 #divides the amount of steps taken by this number. 
        # should always be negative to turn the image around.
        self.smallest_steps = 50

    def moveNextStep(self,
                     algo: str) -> int:
        assert algo in self.algos

        next_pos = -1
        match algo:
            case 'increment':
                next_pos = self.increment()
            case 'hillClimbing':
                next_pos = self.hillClimbing()

        if next_pos != -1:
            self.pynq.moveAbsoluteSteps(next_pos)
        return next_pos

    def increment(self) -> int:
        '''
        Goes through the whole range in equal sized steps. Returns absolute steps
        '''

        return self.pynq.mot_absolute_steps + self.increment_steps
    def hillClimbing(self):
        
        if self.hill_climb_increment > self.smallest_steps:
            if len(self.positions) == 0 or len(self.positions)== 1:
                return self.pynq.mot_absolute_steps + self.hill_climb_increment
            else: 
                if self.sharpness[len(self.sharpness)] > self.sharpness[len(self.sharpness)- 1]:
                    return self.pynq.mot_absolute_steps + self.hill_climb_increment
                elif self.sharpness[len(self.sharpness)] < self.sharpness[len(self.sharpness) - 1]:
                    self.hill_climb_increment = int(self.hill_climb_increment/self.decrease_in_steps)
                    return self.pynq.mot_absolute_steps + self.hill_climb_increment
        else: return -1
        
                
        

