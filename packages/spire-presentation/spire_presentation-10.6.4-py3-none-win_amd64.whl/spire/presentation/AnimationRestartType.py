from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationRestartType(Enum):
    """
    <summary>
        Represents whether the animation effect restarts after the effect has started once. 
    </summary>
    """
    none = -1
    Always = 0
    WhenOff = 1
    Never = 2

