from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillFormatType(Enum):
    """
    <summary>
        Represents the type of fill.
    </summary>
    """
    UnDefined = -1
    none = 0
    Solid = 1
    Gradient = 2
    Pattern = 3
    Picture = 4
    Group = 5

