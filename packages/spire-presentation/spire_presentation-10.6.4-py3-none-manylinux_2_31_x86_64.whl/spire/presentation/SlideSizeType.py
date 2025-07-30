from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideSizeType(Enum):
    """
    <summary>
        Represents the slide size preset.
    </summary>
    """
    none = -1
    Screen4x3 = 0
    Letter = 1
    A4 = 2
    Film35mm = 3
    Overhead = 4
    Banner = 5
    Custom = 6
    Ledger = 7
    A3 = 8
    B4ISO = 9
    B5ISO = 10
    B4JIS = 11
    B5JIS = 12
    HagakiCard = 13
    Screen16x9 = 14
    Screen16x10 = 15

