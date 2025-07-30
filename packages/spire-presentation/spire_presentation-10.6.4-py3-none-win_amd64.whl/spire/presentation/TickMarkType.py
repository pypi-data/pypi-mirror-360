from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TickMarkType(Enum):
    """
    <summary>
        Represents the tick mark type for the specified axis.
    </summary>
    """
    TickMarkNone = 0
    TickMarkCross = 1
    TickMarkInside = 2
    TickMarkOutside = 3

