from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionSoundMode(Enum):
    """
    <summary>
        Represent sound mode of transition.
    </summary>
    """
    none = -1
    StartSound = 0
    StopPrevoiusSound = 1

