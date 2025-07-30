from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationMotionPathEditMode(Enum):
    """
    <summary>
        Specifies how the motion path moves when the target shape is moved
    </summary>
    """
    none = -1
    Relative = 0
    Fixed = 1

