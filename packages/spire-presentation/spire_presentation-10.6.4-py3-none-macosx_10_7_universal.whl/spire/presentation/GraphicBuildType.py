from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicBuildType(Enum):
    """
    <summary>
        Indicates how graphic display style during animation.
    </summary>
    """
    BuildAsOne = 0
    BuildAsSeries = 1
    BuildAsCategory = 2
    BuildAsSeriesElement = 3
    BuildAsCategoryElement = 4

