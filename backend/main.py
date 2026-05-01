import pynq

if __name__ == '__main__':
    pynq = pynq.PYNQ(DEBUG=True)   

    print(pynq.idn)
    pynq.initMot()
    pynq.startMoving(0, 1000)
    print(pynq.endSwitchPushed())