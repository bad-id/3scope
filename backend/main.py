import pynq

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)   

    print(pynq.idn)
    pynq.initMot()
    pynq.moveToZero()

    pynq.moveRelativeSteps(2000)
    pynq.moveRelativeSteps(-1000)
    print(pynq.mot_calibrated, pynq.mot_absolute_steps)
    print('Stopped')