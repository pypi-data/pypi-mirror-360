from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MetaCharacterType(Enum):
    """
    <summary>
        Represents different types of meta characters used in a text.
    </summary>
    """
    SlideNumer = 0
    DateTime = 1
    GenericDateTime = 2
    Footer = 3
    Header = 4
    RtfFormatDateTime = 5

