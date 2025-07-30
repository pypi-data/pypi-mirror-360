from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterEffectType(Enum):
    """
    <summary>
        Represents filter effect types.
    </summary>
    """
    none = 0
    Barn = 1
    Blinds = 2
    Box = 3
    Checkerboard = 4
    Circle = 5
    Diamond = 6
    Dissolve = 7
    Fade = 8
    Image = 9
    Pixelate = 10
    Plus = 11
    RandomBar = 12
    Slide = 13
    Stretch = 14
    Strips = 15
    Wedge = 16
    Wheel = 17
    Wipe = 18

