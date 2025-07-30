from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectFillType(Enum):
    """
    <summary>
        Represent fill types.
    </summary>
    """
    none = -1
    Remove = 0
    Freeze = 1
    Hold = 2
    Transition = 3

