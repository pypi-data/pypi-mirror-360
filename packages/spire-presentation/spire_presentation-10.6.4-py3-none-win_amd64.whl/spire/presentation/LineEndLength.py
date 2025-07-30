from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndLength(Enum):
    """
    <summary>
        Represents the length of an arrowhead.
    </summary>
    """
    none = -1
    Short = 0
    Medium = 1
    Long = 2

