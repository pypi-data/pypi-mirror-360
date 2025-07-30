from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientShapeType(Enum):
    """
    <summary>
        Represents the shape of gradient fill.
    </summary>
    """
    none = -1
    Linear = 0
    Rectangle = 1
    Radial = 2
    Path = 3

