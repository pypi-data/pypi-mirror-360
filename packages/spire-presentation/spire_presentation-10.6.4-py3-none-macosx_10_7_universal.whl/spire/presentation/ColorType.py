from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorType(Enum):
    """

    """
    none = -1
    RGB = 0
    HSL = 1
    Scheme = 3
    System = 4
    KnownColor = 5

