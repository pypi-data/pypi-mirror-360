from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabAlignmentType(Enum):
    """
    <summary>
        Represents the tab alignment.
    </summary>
    """
    none = -1
    Left = 0
    Center = 1
    Right = 2
    Decimal = 3

