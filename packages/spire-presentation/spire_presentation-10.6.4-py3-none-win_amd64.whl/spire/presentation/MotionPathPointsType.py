from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionPathPointsType(Enum):
    """
    <summary>
        Represent types of points in animation motion path.
    </summary>
    """
    none = 0
    Auto = 1
    Corner = 2
    Straight = 3
    Smooth = 4
    CurveAuto = 5
    CurveCorner = 6
    CurveStraight = 7
    CurveSmooth = 8

