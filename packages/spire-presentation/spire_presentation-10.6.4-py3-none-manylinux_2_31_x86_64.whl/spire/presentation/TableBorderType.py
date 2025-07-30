from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TableBorderType(Enum):
    """
    <summary>
        Represents table border style.
    </summary>
    """
    none = 1
    All = 2
    Inside = 4
    Outside = 8
    ToggleTop = 16
    ToggleBottom = 32
    ToggleLeft = 64
    ToggleRight = 128
    InsideHorizontal = 256
    InsideVertical = 512
    DiagonalDown = 1024
    DiagonalUp = 2048

