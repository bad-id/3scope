import pyvisa
from math import floor
from pyflow import extensity

@extensity
def test():
    return 'aa'

class PYNQ:
    defaultPulsePin = "RBPI07"
    defaultDirPin = "RBPI29"
    defaultEndSwitch1Pin = "RBPI27"
    defaultEndSwitch2Pin = "RBPI28"
    defaultPWM = 0
    defaultPWMDevice = "PWM0"

    STATES = ["LOW", "HIGH"]

    def __init__(self,
                ip:str = "10.43.0.1", 
                port:str = "11008",
                DEBUG: bool = False):
        self.ip = ip
        self.port = port
        self.DEBUG = DEBUG

        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(f'TCPIP::{ip}::{port}::SOCKET',
                        open_timeout=10000)
        #print(self.rm.list_resources())

        self.inst.timeout = 2000
        self.inst.write_termination = '\n'
        self.inst.read_termination  = '\n'
        self.inst.StopBits = 1
        
        self.inst.clear()
        self.inst.flush(pyvisa.constants.BufferOperation.discard_read_buffer)
        
        self.idn = self.inst.query('*IDN?')
        #self.inst.write('*RST')
    
    def write(self, 
              command: str):
        if self.DEBUG:                
            print(f'{command}')
        self.inst.write(command)

    def writes(self,
               commands: list[str]):
        '''
        Writes multiple commands to the PYNQ board
        '''
        for command in commands:
            self.write(command)

    def setDir(self,
               pin: str,
               dir: str):
        dir = dir.upper()
        assert (dir == 'IN') or (dir == 'OUT')

        self.write(f':GPIO:DIR {pin}, {dir}')

    def digiRead(self,
                  pin:str) -> bool:
        state: str = self.inst.query(f':GPIO:LEVEL? {pin}')

        return (state == 'High')

    def digiWrite(self,
                  pin: str,
                  state: bool):
        '''
        Write to digital pin
        '''
        statestring = self.STATES[state]
        self.write(f':GPIO:LEVEL {pin}, {statestring}')

    def endSwitchPushed1(self):
        return self.digiRead(self.defaultEndSwitch1Pin)
    def endSwitchPushed2(self):
        return self.digiRead(self.defaultEndSwitch2Pin)
    def endSwitchPushed(self):
        return self.endSwitchPushed1() or self.endSwitchPushed2()
    

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


    def initMot(self):
        self.setDir(self.defaultDirPin, "OUT")
        self.setDir(self.defaultEndSwitch1Pin, "IN")
        self.setDir(self.defaultEndSwitch2Pin, "IN")

        self.setPWM(self.defaultPWM, 0, 0, 0)

    def startMoving(self,
                direction: bool,
                steps:int,
                frequency: float = 1e3):
        self.digiWrite(self.defaultDirPin, direction)
        self.setPWM(
            pwm=self.defaultPWM,
            frequency=frequency,
            duty=0.1,
            steps=steps
        )

    def stopMoving(self):
        self.setPWM(
            pwm=self.defaultPWM,
            frequency=0,
            duty=0,
            steps=0
        )