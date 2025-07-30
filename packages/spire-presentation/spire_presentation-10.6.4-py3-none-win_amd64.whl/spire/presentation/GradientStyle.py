from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStyle(Enum):
    """
    <summary>
        Represents the gradient style.
    </summary>
    """
    none = -1
    FromCorner1 = 0
    FromCorner2 = 1
    FromCorner3 = 2
    FromCorner4 = 3
    FromCenter = 4

