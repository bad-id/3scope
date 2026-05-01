import pynq

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=False)   

    print(pynq.idn)
    pynq.initMot()
    print(pynq.mot_calibrated, pynq.mot_absolute_steps)
    pynq.moveToZero()
    print(pynq.mot_calibrated, pynq.mot_absolute_steps)

    pynq.moveRelativeSteps(0, 2000)
    print(pynq.mot_calibrated, pynq.mot_absolute_steps)
    print('Stopped')