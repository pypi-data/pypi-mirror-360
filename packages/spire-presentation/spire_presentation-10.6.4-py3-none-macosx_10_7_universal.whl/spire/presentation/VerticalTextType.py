from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class VerticalTextType(Enum):
    """
    <summary>
        Indicates vertical writing mode for a text.
    </summary>
    """
    none = -1
    Horizontal = 0
    Vertical = 1
    Vertical270 = 2
    WordArtVertical = 3
    EastAsianVertical = 4
    MongolianVertical = 5
    WordArtVerticalRightToLeft = 6

