from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnchorType(Enum):
    """
    <summary>
        Alignment within a text area.
    </summary>
    """
    none = -1
    Top = 0
    Center = 1
    Bottom = 2
    Justified = 3
    Distributed = 4
    Right = 5
    Left = 6

