from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PlaceholderSize(Enum):
    """
    <summary>
        Represents the size of a placeholder.
    </summary>
    """
    Full = 0
    Half = 1
    Quarter = 2
    none = 3

