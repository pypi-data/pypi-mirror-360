from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextHorizontalOverflowType(Enum):
    """
    <summary>
        Represents text horizontal overflow type.
    </summary>
    """
    none = -1
    Overflow = 0
    Clip = 1

