
from pyflow import extensity
from camera import Camera

cam: Camera = None
started: bool = False

@extensity
def getCameraInstance() -> Camera:
    if not started:
        started = True
        cam = Camera()
        cam.start()
    return cam

@extensity
def testFunctionStuff() -> str:
    return 'aa'

@extensity
class TestingClass:
    def __init__(self):
        pass
    def returnstuff(self):
        return 900