from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeArrange(Enum):
    """
    <summary>
        Represents the arrangement of shape
    </summary>
    """
    BringToFront = 0
    SendToBack = 1
    BringForward = 2
    SendBackward = 3

