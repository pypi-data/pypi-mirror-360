from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FontAlignmentType(Enum):
    """
    <summary>
        Represents vertical font alignment.
    </summary>
    """
    none = -1
    Auto = 0
    Top = 1
    Center = 2
    Bottom = 3
    Baseline = 4

