from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndType(Enum):
    """
    <summary>
        Represents the style of an arrowhead.
    </summary>
    """
    UnDefined = -1
    none = 0
    TriangleArrowHead = 1
    StealthArrow = 2
    Diamond = 3
    Oval = 4
    NoEnd = 5

