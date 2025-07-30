from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionDirection(Enum):
    """
    <summary>
        Represent transition direction types.
    </summary>
    """
    Horizontal = 0
    Vertical = 1
    none = 2

