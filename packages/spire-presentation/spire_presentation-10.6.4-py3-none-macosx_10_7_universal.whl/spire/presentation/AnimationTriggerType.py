from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationTriggerType(Enum):
    """
    <summary>
        Represents the trigger that starts an animation.
    </summary>
    """
    AfterPrevious = 0
    Mixed = 1
    OnPageClick = 2
    WithPrevious = 3
    none = 4

