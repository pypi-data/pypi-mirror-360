from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextBulletType(Enum):
    """
    <summary>
        Represents the type of the extended bullets.
    </summary>
    """
    UnDefined = -1
    none = 0
    Symbol = 1
    Numbered = 2
    Picture = 3

