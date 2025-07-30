from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextStrikethroughType(Enum):
    """
    <summary>
        Represents the type of text strikethrough.
    </summary>
    """
    UnDefined = -1
    none = 0
    Single = 1
    Double = 2

