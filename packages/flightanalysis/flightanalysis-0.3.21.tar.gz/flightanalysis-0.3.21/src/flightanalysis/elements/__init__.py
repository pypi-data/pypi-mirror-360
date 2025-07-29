from .element import Element, Elements
from .line import Line
from .loop import Loop
from .stall_turn import StallTurn
from .snap import Snap
from .spin import Spin
from .tail_slide import TailSlide

type AnyElement = Line | Loop | StallTurn | Snap | Spin | TailSlide