from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ErrorBarSimpleType(Enum):
    """

    """
    Both = 0
    Minus = 1
    Plus = 2

