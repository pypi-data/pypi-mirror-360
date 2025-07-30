from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SmartArtStyleType(Enum):
    """

    """
    SimpleFill = 0
    WhiteOutline = 1
    SubtleEffect = 2
    ModerateEffect = 3
    IntenceEffect = 4
    Polished = 5
    Inset = 6
    Cartoon = 7
    Powder = 8
    BrickScene = 9
    FlatScene = 10
    MetallicScene = 11
    SunsetScene = 12
    BirdsEyeScene = 13

