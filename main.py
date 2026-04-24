import pyvisa

ip = "10.43.0.1"
port = "11008"

defaultPulsePin = "RBPI07"
defaultDirPin = "RBPI29"
defaultEndSwitch1Pin = "RBPI27"
defaultEndSwitch2Pin = "RBPI28"
defaultPWMDevice = "PWM0"

rm = pyvisa.ResourceManager()
inst = rm.open_resource(f'TCPIP::{ip}::{port}::SOCKET',
                        open_timeout=10000)
inst.timeout = 2000
inst.write_termination = '\n'
inst.read_termination = '\n'

inst.clear()
inst.flush(pyvisa.constants.BufferOperation.discard_read_buffer)
idn = inst.query('*IDN?')

print(idn)