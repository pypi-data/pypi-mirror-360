from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextCapType(Enum):
    """
    <summary>
        Represents the type of text capitalisation.
    </summary>
    """
    UnDefined = -1
    none = 0
    Small = 1
    All = 2

