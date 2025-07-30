from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodePresetClassType(Enum):
    """
    <summary>
        Represent effect class types.
    </summary>
    """
    none = 0
    Entrance = 1
    Exit = 2
    Emphasis = 3
    Path = 4
    Verb = 5
    MediaCall = 6

