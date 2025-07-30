from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionEightDirection(Enum):
    """
    <summary>
        Represent eight direction transition types.
    </summary>
    """
    LeftDown = 0
    LeftUp = 1
    RightDown = 2
    RightUp = 3
    Left = 4
    Up = 5
    Down = 6
    Right = 7
    none = 8

