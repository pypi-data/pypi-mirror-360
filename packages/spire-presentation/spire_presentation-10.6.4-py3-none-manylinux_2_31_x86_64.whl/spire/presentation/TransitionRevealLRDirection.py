from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionRevealLRDirection(Enum):
    """
    <summary>
        Represent reveal leftright transition direction types.
    </summary>
    """
    SmoothlyFromLeft = 0
    SmoothlyFromRight = 1
    TroughBlackFromLeft = 2
    TroughBlackFromRight = 3

