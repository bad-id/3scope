
from pyflow import extensity

@extensity
def testFunctionStuff() -> str:
    return 'aa'

@extensity
class TestingClass:
    def __init__(self):
        pass
    def returnstuff(self):
        return 900