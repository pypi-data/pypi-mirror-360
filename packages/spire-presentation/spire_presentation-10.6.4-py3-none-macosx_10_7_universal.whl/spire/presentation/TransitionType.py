from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TransitionType(Enum):
    """
    <summary>
        Represent slide show transition type.
    </summary>
    """
    none = 0
    Airplane = 1
    Blinds = 2
    Box = 3
    Checker = 4
    Circle = 5
    Comb = 6
    Conveyor = 7
    Cover = 8
    Cut = 9
    Cube = 10
    Curtains = 11
    Crush = 12
    Diamond = 13
    Dissolve = 14
    Doors = 15
    Drape = 16
    Fade = 17
    Ferris = 18
    FLash = 19
    Flip = 20
    Flythrough = 21
    Fracture = 22
    FallOver = 23
    Gallery = 24
    Glitter = 25
    Honeycomb = 26
    Newsflash = 27
    Orbit = 28
    Origami = 29
    PageCurlDouble = 30
    Pan = 31
    PeelOff = 32
    Plus = 33
    Prestige = 34
    Pull = 35
    Push = 36
    Random = 37
    Reveal = 38
    RandomBar = 39
    Ripple = 40
    Rotate = 41
    Shred = 42
    SoundAction = 43
    Split = 44
    Strips = 45
    Switch = 46
    Vortex = 47
    Wedge = 48
    Wheel = 49
    Wipe = 50
    Window = 51
    Wind = 52
    Warp = 53
    Zoom = 54
    Morph = 55

