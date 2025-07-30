from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AudioPlayMode(Enum):
    """
    <summary>
        Indicates how a sound is played.
    </summary>
    """
    Mixed = -1
    Auto = 0
    OnClick = 1
    Presentation = 2

