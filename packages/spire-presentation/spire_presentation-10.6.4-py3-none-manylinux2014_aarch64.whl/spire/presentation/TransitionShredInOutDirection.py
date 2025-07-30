from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionShredInOutDirection(Enum):
    """
    <summary>
        Represent shred inout transition direction types.
    </summary>
    """
    StripIn = 0
    StripOut = 1
    RectangleIn = 2
    RectangleOut = 3

