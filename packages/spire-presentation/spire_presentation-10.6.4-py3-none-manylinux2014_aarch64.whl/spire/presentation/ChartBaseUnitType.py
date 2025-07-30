from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartBaseUnitType(Enum):
    """
    <summary>
        Represents the base unit for the category axis
    </summary>
    """
    Days = 0
    Months = 1
    Years = 2
    Auto = -1

