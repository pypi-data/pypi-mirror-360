from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorDirection(Enum):
    """
    <summary>
        Represents color direction.
    </summary>
    """
    none = -1
    Clockwise = 0
    CounterClockwise = 1

