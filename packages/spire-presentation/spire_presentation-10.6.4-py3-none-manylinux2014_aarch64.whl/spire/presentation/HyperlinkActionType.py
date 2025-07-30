from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class HyperlinkActionType(Enum):
    """
    <summary>
        Represents a type of hyperlink action.
    </summary>
    """
    none = -1
    NoAction = 0
    Hyperlink = 1
    GotoFirstSlide = 2
    GotoPrevSlide = 3
    GotoNextSlide = 4
    GotoLastSlide = 5
    GotoEndShow = 6
    GotoLastViewedSlide = 7
    GotoSlide = 8
    StartCustomSlideShow = 9
    OpenFile = 10
    OpenPresentation = 11
    StartStopMedia = 12
    StartMacro = 13
    StartProgram = 14

