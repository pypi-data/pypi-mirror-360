from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineStyle(Enum):
    """
    <summary>
        Represents the style of a line.
    </summary>
    """
    none = -1
    Single = 0
    ThinThin = 1
    ThinThick = 2
    ThickThin = 3
    ThickBetweenThin = 4

