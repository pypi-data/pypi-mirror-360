from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCommandType(Enum):
    """
    <summary>
        Represents command effect type for command effect behavior.
    </summary>
    """
    none = -1
    Event = 0
    Call = 1
    Verb = 2

