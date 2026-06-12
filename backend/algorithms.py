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
        pass
        

