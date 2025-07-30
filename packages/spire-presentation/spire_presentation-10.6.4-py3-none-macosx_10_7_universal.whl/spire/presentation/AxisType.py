from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AxisType(Enum):
    """
    <summary>
        CategoryAxis Type.
    </summary>
    """
    Auto = 0
    TextAxis = 1
    DateAxis = 2

