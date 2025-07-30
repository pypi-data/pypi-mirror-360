from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterEffectSubtype(Enum):
    """
    <summary>
        Represents filter effect subtypes.
    </summary>
    """
    none = 0
    Across = 1
    Down = 2
    DownLeft = 3
    DownRight = 4
    FromBottom = 5
    FromLeft = 6
    FromRight = 7
    FromTop = 8
    Horizontal = 9
    In = 10
    InHorizontal = 11
    InVertical = 12
    Left = 13
    Out = 14
    OutHorizontal = 15
    OutVertical = 16
    Right = 17
    Spokes1 = 18
    Spokes2 = 19
    Spokes3 = 20
    Spokes4 = 21
    Spokes8 = 22
    Up = 23
    UpLeft = 24
    UpRight = 25
    Vertical = 26

