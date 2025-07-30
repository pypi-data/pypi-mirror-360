from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineDashStyleType(Enum):
    """
    <summary>
        Represents the line dash style.
    </summary>
    """
    none = -1
    Solid = 0
    Dot = 1
    Dash = 2
    LargeDash = 3
    DashDot = 4
    LargeDashDot = 5
    LargeDashDotDot = 6
    SystemDash = 7
    SystemDot = 8
    SystemDashDot = 9
    SystemDashDotDot = 10
    Custom = 11

