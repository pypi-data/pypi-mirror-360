from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlitterTransitionDirection(Enum):
    """
    <summary>
        Represent glitter transition direction types.
    </summary>
    """
    HexagonFromLeft = 0
    HexagonFromUp = 1
    HexagonFromDown = 2
    HexagonFromRight = 3
    DiamondFromLeft = 4
    DiamondFromUp = 5
    DiamondFromDown = 6
    DiamondFromRight = 7

