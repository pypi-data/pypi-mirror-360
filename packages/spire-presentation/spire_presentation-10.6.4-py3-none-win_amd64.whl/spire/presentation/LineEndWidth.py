from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineEndWidth(Enum):
    """
    <summary>
        Represents the width of an arrowhead.
    </summary>
    """
    none = -1
    Narrow = 0
    Medium = 1
    Wide = 2

