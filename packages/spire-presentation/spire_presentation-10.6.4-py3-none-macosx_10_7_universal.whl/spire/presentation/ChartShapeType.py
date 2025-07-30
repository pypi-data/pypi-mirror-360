from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartShapeType(Enum):
    """
    <summary>
        Represents a shape of chart.
    </summary>
    """
    none = -1
    Box = 0
    Cone = 1
    ConeToMax = 2
    Cylinder = 3
    Pyramid = 4
    PyramidToMaximum = 5

