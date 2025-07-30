from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlackWhiteMode(Enum):
    """
    <summary>
        Indicates how colored shape should be transformed into black and white.
    </summary>
    """
    none = -1
    Color = 0
    Auto = 1
    Gray = 2
    LightGray = 3
    InverseGray = 4
    GrayWhite = 5
    BlackGray = 6
    BlackWhite = 7
    Black = 8
    White = 9
    Hidden = 10

