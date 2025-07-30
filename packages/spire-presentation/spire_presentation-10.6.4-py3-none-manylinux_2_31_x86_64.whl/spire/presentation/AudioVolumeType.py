from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AudioVolumeType(Enum):
    """
    <summary>
        Indicates audio volume.
    </summary>
    """
    Mixed = -1
    Mute = 0
    Low = 1
    Medium = 2
    Loud = 3

