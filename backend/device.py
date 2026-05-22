from abc import ABCMeta, abstractmethod

'''
Abstract base class for any device like camera or pynq
'''

class Device(metaclass=ABCMeta):
    device_name = None
    connected = False

    @abstractmethod
    def connect(self) -> bool: # returns true if successful connection
        ...