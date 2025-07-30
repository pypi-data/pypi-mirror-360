from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAlignment(Enum):
    """
    <summary>
        Represents alignment of shape.
    </summary>
    """
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignTop = 3
    AlignMiddle = 4
    AlignBottom = 5
    DistributeVertically = 6
    DistributeHorizontally = 7

