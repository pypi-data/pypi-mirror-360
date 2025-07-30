from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PenAlignmentType(Enum):
    """
    <summary>
        Represents the lines alignment type.
    </summary>
    """
    none = -1
    Center = 0
    Inset = 1

