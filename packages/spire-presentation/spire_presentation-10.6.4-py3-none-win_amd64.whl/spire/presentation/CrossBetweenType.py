from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CrossBetweenType(Enum):
    """

    """
    none = 0
    Between = 0
    MidpointOfCategory = 1

