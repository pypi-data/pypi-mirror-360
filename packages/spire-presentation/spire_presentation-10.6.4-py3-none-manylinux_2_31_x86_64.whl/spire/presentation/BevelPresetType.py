from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BevelPresetType(Enum):
    """
    <summary>
        Indicates 3D bevel of shape.
    </summary>
    """
    none = -1
    Angle = 0
    ArtDeco = 1
    Circle = 2
    Convex = 3
    CoolSlant = 4
    Cross = 5
    Divot = 6
    HardEdge = 7
    RelaxedInset = 8
    Riblet = 9
    Slope = 10
    SoftRound = 11

