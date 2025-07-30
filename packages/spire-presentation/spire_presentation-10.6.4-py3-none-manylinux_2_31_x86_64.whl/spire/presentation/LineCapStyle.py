from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineCapStyle(Enum):
    """
    <summary>
        Represents the line cap style.
    </summary>
    """
    none = -1
    Round = 0
    Square = 1
    Flat = 2

