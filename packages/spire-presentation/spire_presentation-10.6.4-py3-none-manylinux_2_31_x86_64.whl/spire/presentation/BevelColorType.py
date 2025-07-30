from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BevelColorType(Enum):
    """
    <summary>
        Indicates bevel color mode of shape.
    </summary>
    """
    Contour = 0
    Extrusion = 1

