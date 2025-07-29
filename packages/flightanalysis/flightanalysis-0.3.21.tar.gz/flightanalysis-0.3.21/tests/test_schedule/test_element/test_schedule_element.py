import numpy as np
from flightdata import State
from flightanalysis.elements import Element


class SubEl(Element):
    def __init__(self, speed, arg1, arg2, uid: str = None):
        super().__init__(uid, speed)
        self.arg1 = arg1
        self.arg2 = arg2



def test_set_parms():
    se = SubEl(30, 2, 3)
    se2 = se.set_parms(arg1=4)
    assert se2.arg1 == 4
    assert se2.arg2 == 3
    assert isinstance(se2, SubEl)


def test_create_time_basic():
    t = Element.create_time(10, None)
    assert len(t) == np.ceil(10 * State._construct_freq)
