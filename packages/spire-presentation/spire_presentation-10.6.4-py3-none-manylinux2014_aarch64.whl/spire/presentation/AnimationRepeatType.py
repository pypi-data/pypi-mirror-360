from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationRepeatType(Enum):
    """
    <summary>
        Specifies the timing repeat type.
    </summary>
    """
    Number = 0
    UtilNextClick = 1
    UtilEndOfSlide = 2

