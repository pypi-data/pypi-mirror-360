from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Direction(Enum):
    """
    <summary>
        Represents the orientation of a shape.
    </summary>
    """
    Horizontal = 0
    Vertical = 1

