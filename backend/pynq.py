import pyvisa
from math import floor
import time # temporary

class MotorCommandOutOfBounds(Exception):
    pass

class PYNQ:
    defaultPulsePin = "RBPI07"
    defaultDirPin = "RBPI29"
    defaultEndSwitch1Pin = "RBPI27"
    defaultEndSwitch2Pin = "RBPI28"
    defaultPWM = 0
    defaultPWMDevice = "PWM0"

    PYNQ_MODULES = ["GPIO", "UART0_TX", "UART0_RX", "SPICLK0", "MISO0", "MOSI0",
            "SS0", "SPICLK1", "MISO1", "MOSI1", "SS1", "SDA0", "SCL0", "SDA1", "SCL1",
            "PWM0", "PWM1","PWM2", "PWM3","PWM4", "PWM5",
            "PULSECOUNTER0","PULSECOUNTER1",
            "UART1_TX", "UART1_RX","IIC0_SDA","IIC0_SCL"]

    STATES = ["LOW", "HIGH"]

    DIR_SIGN = [1, -1]
    MOT_LIMITS = [0, 57000] # 58265/58257 is the max range, for safety 57000 limit

    def __init__(self,
                ip:str = "10.43.0.1", 
                port:str = "11008",
                DEBUG: bool = False):
        self.ip = ip
        self.port = port
        self.DEBUG = DEBUG
        self.mot_calibrated = False # Is the absolute positon known
        self.mot_absolute_steps = 0 # Absolute number of steps from zero position

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
    
    def query(self,
              command: str):
        if self.DEBUG:
            print(f'{command}')
        return self.inst.query(command)

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

    def switchBoxMap(self,
                     pin: str,
                     module: str):
        self.write(f'SWITCHBOX:MAP {pin},{module}')

    def digiRead(self,
                  pin:str) -> bool:
        resp: str = self.query(f':GPIO:LEVEL? {pin}')
        if self.DEBUG:
            print(resp)

        if 'High' in resp:
            return True
        elif 'Low' in resp:
            return False
        raise Exception('Digital read failed')

    def digiWrite(self,
                  pin: str,
                  state: bool):
        '''
        Write to digital pin
        '''
        statestring = self.STATES[state]
        self.write(f':GPIO:LEVEL {pin}, {statestring}')

    def endSwitchPushed1(self): # Needs to be inverse
        return not self.digiRead(self.defaultEndSwitch1Pin)
    def endSwitchPushed2(self):
        return not self.digiRead(self.defaultEndSwitch2Pin)
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
        self.switchBoxMap(self.defaultPulsePin, self.defaultPWMDevice)
        self.switchBoxMap(self.defaultDirPin, 'GPIO')
        self.switchBoxMap(self.defaultEndSwitch1Pin, 'GPIO')
        self.switchBoxMap(self.defaultEndSwitch2Pin, 'GPIO')

        self.setDir(self.defaultDirPin, "OUT")
        self.setDir(self.defaultEndSwitch1Pin, "IN")
        self.setDir(self.defaultEndSwitch2Pin, "IN")

        self.setPWM(self.defaultPWM, 0, 0, 0)

    def startMoving(self,
                direction: bool,
                steps:int,
                frequency: float = 4500):
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
        self.mot_calibrated = False # messy fix, TODO: track pending steps
    
    def moveRelativeSteps(self, 
                          steps: int, 
                          frequency: float = 4500):
        '''
        Blocks execution while moving, to set direction, make steps negative

        :returns: True if successful, false if failed
        '''
        if self.mot_calibrated:
            new_pos = self.mot_absolute_steps + steps
            if (new_pos < self.MOT_LIMITS[0]) or (new_pos > self.MOT_LIMITS[1]):
                raise MotorCommandOutOfBounds

            self.mot_absolute_steps = new_pos
        
        abs_steps = abs(steps)

        direction = (steps < 0)
        self.startMoving(direction=direction,
                         steps=abs_steps,
                         frequency=frequency)
        time.sleep(abs_steps/frequency)
        

    def moveToZero(self,
                   steps: int = 100):
        '''
        :param steps: size of jumps the motor moves in
        '''
        assert (steps > 0)
        while (self.endSwitchPushed2() == False):
            self.moveRelativeSteps(-1*steps)
        self.stopMoving()
        self.mot_calibrated = True
        self.mot_absolute_steps = self.MOT_LIMITS[0]

        if self.DEBUG:
            print('Stopped at zero point')
        return
    
    def moveToEnd(self,
                  steps: int = 100):
        assert (steps > 0)
        while (self.endSwitchPushed1() == False):
            self.moveRelativeSteps(steps)
        self.stopMoving()

        if self.DEBUG:
            print('Stopped at end point')