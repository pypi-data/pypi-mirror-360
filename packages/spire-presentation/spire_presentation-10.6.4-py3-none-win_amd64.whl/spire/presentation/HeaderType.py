from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class HeaderType(Enum):
    """

    """
    InvalidValue = -1
    EvenHeader = 0
    OddHeader = 1
    EvenFooter = 2
    OddFooter = 3
    FirstPageHeader = 4
    FirstPageFooter = 5

