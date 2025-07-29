from __future__ import annotations
from flightdata import State
import geometry as g
import numpy as np
import pandas as pd
import numpy.typing as npt
from dataclasses import dataclass


@dataclass
class Measurement:
    value: npt.NDArray
    unit: str
    direction: g.Point
    visibility: npt.NDArray
    keys: npt.NDArray = None
    info: dict | None = None

    def __len__(self):
        return len(self.value)

    def __getitem__(self, sli):
        return Measurement(
            self.value[sli],
            self.unit,
            self.direction[sli],
            self.visibility[sli],
            self.info
        )

    def to_dict(self):
        return dict(
            value=list(self.value),
            unit=self.unit,
            direction=self.direction.to_dicts(),
            visibility=self.visibility.tolist(),
            keys=list(self.keys) if self.keys is not None else None,
            info=self.info
        )

    def __repr__(self):
        if len(self.value) == 1:
            return f"Measurement({self.value}, {self.direction}, {self.visibility})"
        else:
            return f"Measurement(len={len(self)}, unit={self.unit})"

    @staticmethod
    def from_dict(data: dict) -> Measurement:
        return Measurement(
            np.array(data["value"]),
            data["unit"],
            g.Point.from_dicts(data["direction"]),
            np.array(data["visibility"]),
            np.array(data["keys"]) if 'keys' in data and data["keys"] is not None else None,
            info=data.get("info", None)
        )

    @staticmethod
    def ratio(vs, expected):
        avs, aex = np.abs(vs), np.abs(expected)

        nom = np.maximum(avs, aex)
        denom = np.minimum(avs, aex)
        denom = np.maximum(denom, nom / 10)

        with np.errstate(divide="ignore", invalid="ignore"):
            res = ((avs > aex) * 2 - 1) * (nom / denom - 1)
        
        res[vs * expected < 0] = -10
        
        return np.nan_to_num(res, 0)



    @staticmethod
    def get_axial_direction(tp: State):
        """Proj is a vector in the axial direction for the template ref_frame (tp[0].transform)*"""
        # proj = g.g.Point(0, np.cos(el.ke), np.sin(el.ke))
        return g.PX().cross(tp[0].arc_centre()).unit()
