from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PictureFillType(Enum):
    """
    <summary>
        Indicates how picture will fill area.
    </summary>
    """
    Tile = 0
    Stretch = 1

