from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetMaterialType(Enum):
    """
    <summary>
        Indicates material of shape.
    </summary>
    """
    none = -1
    Clear = 0
    DkEdge = 1
    Flat = 2
    LegacyMatte = 3
    LegacyMetal = 4
    LegacyPlastic = 5
    LegacyWireframe = 6
    Matte = 7
    Metal = 8
    Plastic = 9
    Powder = 10
    SoftEdge = 11
    Softmetal = 12
    TranslucentPowder = 13
    WarmMatte = 14

