from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationMotionOrigin(Enum):
    """
    <summary>
        Indicates that the origin of the motion path.
    </summary>
    """
    none = -1
    Parent = 0
    Layout = 1

