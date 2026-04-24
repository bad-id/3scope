import pyvisa

defaultPulsePin = "RBPI07"
defaultDirPin = "RBPI29"
defaultEndSwitch1Pin = "RBPI27"
defaultEndSwitch2Pin = "RBPI28"
defaultPWMDevice = "PWM0"

class PYNQ:
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

pynq = PYNQ()   

print(pynq.idn)