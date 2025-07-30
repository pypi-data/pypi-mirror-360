from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ErrorValueType(Enum):
    """

    """
    CustomErrorBars = 0
    FixedValue = 1
    Percentage = 2
    StandardDeviation = 3
    StandardError = 4

