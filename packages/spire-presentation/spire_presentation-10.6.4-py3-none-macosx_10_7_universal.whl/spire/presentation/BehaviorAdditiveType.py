from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BehaviorAdditiveType(Enum):
    """
    <summary>
        Represents additive type for effect behavior.
    </summary>
    """
    Undefined = -1
    none = 0
    Base = 1
    Sum = 2
    Replace = 3
    Multiply = 4

