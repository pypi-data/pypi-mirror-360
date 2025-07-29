from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass, field
from flightdata.base import to_list   
import re


_rollstr_re = re.compile(r"((\d+)([Xx*/])(\d+)|(\d+))")
def parse_roll_string(data: str):
    res = _rollstr_re.search(data)

    if res is None:
        raise ValueError(f"Cannot parse roll string {data}")
    match res.group(3):
        case "/":
            return [float(res.group(2))/float(res.group(4))]
        case "X" | "x" | "*":
            return [1/int(res.group(4)) for _ in range(int(res.group(2)))]
        case _:
            return [float(data)]


@dataclass
class Combination(Criteria):
    desired: np.ndarray = field(default_factory=lambda : None)
    """Handles a series of criteria assessments.
    for example a number of rolls in an element.
    Warning - if not all of the desired values have collectors then the ones with collectors must
    come first.
    """
    
    def __post_init__(self):
        self.desired = np.array(self.desired)

    def __len__(self):
        return self.desired.shape[0]

    def __getitem__(self, value: int):
        return self.desired[value]

    def get_errors(self, values: npt.ArrayLike):
        """get the error between values and desired for all the options"""
        return np.array(self.desired)[:,:len(values)] - np.array(values)

    def get_option_error(self, option: int, values: npt.ArrayLike) -> npt.NDArray:
        """The difference between the values and a given option"""
        return np.array(values) - self.desired[option]

    def check_option(self, values) -> int:
        """Given a set of values, return the option id which gives the least error"""
        return int(np.sum(np.abs(self.get_errors(values)), axis=1).argmin())

    def to_dict(self, criteria_names: bool = True) -> dict:
        return dict(
            **(dict(name=self.name) if criteria_names else {}),
            kind=self.__class__.__name__,
            lookup=self.lookup.__dict__,
            desired=to_list(self.desired),
        )
    

    @staticmethod
    def rolllist(rolls, reversable=True) -> Combination:
        rolls = [r for r in rolls]
        rolls = [rolls, [-r for r in rolls]] if reversable else [rolls]
        return Combination("rolllist", desired=rolls)

    @staticmethod
    def rollcombo(rollstring, reversable=True) -> Combination:
        """Convenience constructor to allow Combinations to be built from strings such as 2X4 or 
        1/2"""
        return Combination.rolllist([2 * np.pi * r for r in parse_roll_string(rollstring)], reversable)
    
    def append_roll_sum(self, inplace=False) -> Combination:
        """Add a roll sum to the end of the desired list"""
        des = np.column_stack([self.desired, np.cumsum(self.desired, axis=1)])
        if inplace:
            self.desired = des
            return self
        return Combination("rollsum", self.lookup, des)