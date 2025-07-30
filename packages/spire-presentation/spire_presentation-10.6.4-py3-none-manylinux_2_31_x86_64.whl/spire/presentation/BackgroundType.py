from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BackgroundType(Enum):
    """
    <summary>
        Defines the slide background fill type.
    </summary>
    """
    none = -1
    Themed = 0
    Custom = 1

