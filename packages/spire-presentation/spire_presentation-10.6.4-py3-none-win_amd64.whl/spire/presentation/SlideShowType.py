from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideShowType(Enum):
    """

    """
    Present = 0
    Browse = 1
    Kiosk = 2

