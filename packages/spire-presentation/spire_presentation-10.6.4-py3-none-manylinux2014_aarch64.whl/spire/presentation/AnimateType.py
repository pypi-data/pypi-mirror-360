from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimateType(Enum):
    """

    """
    All = 0
    Word = 1
    Letter = 2

