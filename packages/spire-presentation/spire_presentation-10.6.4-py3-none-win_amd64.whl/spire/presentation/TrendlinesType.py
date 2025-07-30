from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TrendlinesType(Enum):
    """

    """
    Exponential = 0
    Linear = 1
    Logarithmic = 2
    MovingAverage = 3
    Polynomial = 4
    Power = 5

