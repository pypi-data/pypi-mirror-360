from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAlignmentType(Enum):
    """
    <summary>
        Represents different text alignment styles.
    </summary>
    """
    none = -1
    Left = 0
    Center = 1
    Right = 2
    Justify = 3
    Dist = 4

