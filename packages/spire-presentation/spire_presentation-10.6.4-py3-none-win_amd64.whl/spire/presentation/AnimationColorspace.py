from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationColorspace(Enum):
    """
    <summary>
        Represents color space for color effect behavior.
    </summary>
    """
    none = -1
    RGB = 0
    HSL = 1

