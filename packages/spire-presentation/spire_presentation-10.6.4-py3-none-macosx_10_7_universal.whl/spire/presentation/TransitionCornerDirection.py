from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionCornerDirection(Enum):
    """
    <summary>
        Represent corner direction transition types.
    </summary>
    """
    LeftDown = 0
    LeftUp = 1
    RightDown = 2
    RightUp = 3
    none = 4

