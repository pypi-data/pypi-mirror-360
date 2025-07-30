from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureType(Enum):
    """
    <summary>
        Indicates mode of bar picture filling.
    </summary>
    """
    none = -1
    Stack = 0
    StackScale = 1
    Stretch = 2

