from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TickLabelPositionType(Enum):
    """
    <summary>
        Represents the position type of tick-mark labels on the specified axis.
    </summary>
    """
    TickLabelPositionHigh = 0
    TickLabelPositionLow = 1
    TickLabelPositionNextToAxis = 2
    TickLabelPositionNone = 3

