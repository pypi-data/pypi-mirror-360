from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionSideDirectionType(Enum):
    """
    <summary>
        Represent side direction transition types.
    </summary>
    """
    Left = 0
    Up = 1
    Down = 2
    Right = 3

