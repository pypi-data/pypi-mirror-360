from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartDisplayUnitType(Enum):
    """
    <summary>
        Indicates multiplicity of the displayed data.
    </summary>
    """
    none = 0
    Hundreds = 1
    Thousands = 2
    TenThousands = 3
    HundredThousands = 4
    Millions = 5
    TenMillions = 6
    HundredMillions = 7
    Billions = 8
    Trillions = 9
    Percentage = 10

