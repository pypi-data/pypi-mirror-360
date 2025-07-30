from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterRevealType(Enum):
    """
    <summary>
        Represents filter reveal type.
    </summary>
    """
    UnDefined = -1
    none = 0
    In = 1
    Out = 2

