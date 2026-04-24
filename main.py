import pyvisa
from math import floor

class PYNQ:
    defaultPulsePin = "RBPI07"
    defaultDirPin = "RBPI29"
    defaultEndSwitch1Pin = "RBPI27"
    defaultEndSwitch2Pin = "RBPI28"
    defaultPWMDevice = "PWM0"

    def __init__(self,
                ip:str = "10.43.0.1", 
                port = "11008"):
        self.ip = ip
        self.port = port

        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(f'TCPIP::{ip}::{port}::SOCKET',
                        open_timeout=10000)


        self.inst.timeout = 2000
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'
        
        self.inst.clear()
        self.inst.flush(pyvisa.constants.BufferOperation.discard_read_buffer)
        
        self.idn = self.inst.query('*IDN?')
    
    def write(self, 
              command: str):
        self.inst.write(command)

    def writes(self,
               commands: list[str]):
        '''
        Writes multiple commands to the PYNQ board
        '''
        for command in commands:
            self.write(command)

    def setPWM(self,
               pwm: int, # PWM module selection
               frequency: float,
               duty: float,
               steps: int):
        assert (pwm>=0) and (pwm<=6)
        assert frequency >=0
        assert (duty >=0) and (duty <=1)
        assert (steps >= 0)
        
        period: int = 0
        if frequency == 0:
            period = 0
            duty = 0
        else:
            period = floor(1e8 / frequency)

        if duty == 1:
            duty = period-1
        else:
            duty = floor(period * duty)

        pwm_name: str = f'PWM{pwm}'
        self.writes([
            f':{pwm_name}:PERIOD {period}',
            f':{pwm_name}:DUTY {duty}',
            f':{pwm_name}:STEPS {steps}',
                     ])


    def stepMot(self,
                steps:int):
        pass

pynq = PYNQ()   

print(pynq.idn)
pynq.setPWM(0, 10, 0.5, 10)