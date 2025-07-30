from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BehaviorAccumulateType(Enum):
    """
    <summary>
        Represents types of accumulation of effect behaviors.
    </summary>
    """
    UnDefined = -1
    Always = 0
    none = 1

