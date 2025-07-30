from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ProjectionType(Enum):
    """

    """
    Automatic = 0
    Mercator = 1
    Miller = 2
    Robinson = 2
