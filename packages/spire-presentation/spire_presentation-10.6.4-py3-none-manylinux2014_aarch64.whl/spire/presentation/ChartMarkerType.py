from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartMarkerType(Enum):
    """
    <summary>
         Chart marker types.
    </summary>
    """
    UnDefined = -1
    Circle = 0
    Dash = 1
    Diamond = 2
    Dot = 3
    none = 4
    Picture = 5
    Plus = 6
    Square = 7
    Star = 8
    Triangle = 9
    X = 10

