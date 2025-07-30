from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PropertyValueType(Enum):
    """
    <summary>
        Represent property value types.
    </summary>
    """
    none = -1
    String = 0
    Number = 1
    Color = 2

