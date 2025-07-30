from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDataLabelPosition(Enum):
    """
    <summary>
        Indicates position of data labels.
    </summary>
    """
    Bottom = 0
    BestFit = 1
    Center = 2
    InsideBase = 3
    InsideEnd = 4
    Left = 5
    OutsideEnd = 6
    Right = 7
    Top = 8
    none = 9

