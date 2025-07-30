from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCalculationMode(Enum):
    """
    <summary>
        Represent calc mode for animation property.
    </summary>
    """
    none = -1
    Discrete = 0
    Linear = 1
    Formula = 2

