from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionInOutDirection(Enum):
    """
    <summary>
        Represent in or out direction transition types.
    </summary>
    """
    In = 0
    Out = 1
    none = 2

