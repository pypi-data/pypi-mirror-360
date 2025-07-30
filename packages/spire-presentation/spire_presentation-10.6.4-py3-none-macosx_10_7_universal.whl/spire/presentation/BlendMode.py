from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlendMode(Enum):
    """
    <summary>
        Indicates blend mode.
    </summary>
    """
    Darken = 0
    Lighten = 1
    Multiply = 2
    Overlay = 3
    Screen = 4
    none = 5

