from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideOrienation(Enum):
    """
    <summary>
        Represents the slide orientation.
    </summary>
    """
    Landscape = 0
    Portrait = 1

