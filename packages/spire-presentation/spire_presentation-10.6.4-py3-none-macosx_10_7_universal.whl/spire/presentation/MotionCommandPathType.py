from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionCommandPathType(Enum):
    """
    <summary>
        Represent types of command for animation motion effect behavior.
    </summary>
    """
    MoveTo = 0
    LineTo = 1
    CurveTo = 2
    CloseLoop = 3
    End = 4

