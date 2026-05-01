import pynq

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)   

    print(pynq.idn)
    pynq.initMot()
    pynq.moveRelativeSteps(-50000)
    pynq.moveToZero()

    pynq.moveRelativeSteps(-100)
    print(pynq.mot_calibrated, pynq.mot_absolute_steps)
    print('Stopped')