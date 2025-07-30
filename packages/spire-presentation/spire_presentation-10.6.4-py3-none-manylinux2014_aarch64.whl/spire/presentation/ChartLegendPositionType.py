from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartLegendPositionType(Enum):
    """
    <summary>
        Indicates a position of legend on a chart.
    </summary>
    """
    none = -1
    Bottom = 0
    Left = 1
    Right = 2
    Top = 3
    TopRight = 4

