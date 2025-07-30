from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetLightRigType(Enum):
    """
    <summary>
        Indicates light preset types.
    </summary>
    """
    none = -1
    Balanced = 0
    BrightRoom = 1
    Chilly = 2
    Contrasting = 3
    Flat = 4
    Flood = 5
    Freezing = 6
    Glow = 7
    Harsh = 8
    LegacyFlat1 = 9
    LegacyFlat2 = 10
    LegacyFlat3 = 11
    LegacyFlat4 = 12
    LegacyHarsh1 = 13
    LegacyHarsh2 = 14
    LegacyHarsh3 = 15
    LegacyHarsh4 = 16
    LegacyNormal1 = 17
    LegacyNormal2 = 18
    LegacyNormal3 = 19
    LegacyNormal4 = 20
    Morning = 21
    Soft = 22
    Sunrise = 23
    Sunset = 24
    ThreePt = 25
    TwoPt = 26

