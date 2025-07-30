from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeElementFillSource(Enum):
    """
    <summary>
        Represents how shape element should be filled.
    </summary>
    """
    NoFill = 0
    Shape = 1
    Lighten = 2
    LightenLess = 3
    Darken = 4
    DarkenLess = 5
    OwnFill = 6

