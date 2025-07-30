from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class QuartileCalculation(Enum):
    """
    <summary>
        It represents Quartile calculation used for Box and Whisker Chart series
     </summary>
    """
    InclusiveMedian = 0
    ExclusiveMedian = 1

