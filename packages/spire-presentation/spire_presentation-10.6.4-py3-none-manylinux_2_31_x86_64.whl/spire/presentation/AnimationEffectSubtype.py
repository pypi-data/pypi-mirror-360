from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffectSubtype(Enum):
    """
    <summary>
        Represents subtypes of animation effect.
    </summary>
    """
    none = 0
    Across = 1
    Bottom = 2
    BottomLeft = 3
    BottomRight = 4
    Center = 5
    Clockwise = 6
    CounterClockwise = 7
    GradualAndCycleClockwise = 8
    GradualAndCycleCounterClockwise = 9
    Down = 10
    DownLeft = 11
    DownRight = 12
    FontAllCaps = 13
    FontBold = 14
    FontItalic = 15
    FontShadow = 16
    FontStrikethrough = 17
    FontUnderline = 18
    Gradual = 19
    Horizontal = 20
    HorizontalIn = 21
    HorizontalOut = 22
    In = 23
    InBottom = 24
    InCenter = 25
    InSlightly = 26
    Instant = 27
    Left = 28
    OrdinalMask = 29
    Out = 30
    OutBottom = 31
    OutCenter = 32
    OutSlightly = 33
    Right = 34
    Slightly = 35
    Top = 36
    TopLeft = 37
    TopRight = 38
    Up = 39
    UpLeft = 40
    UpRight = 41
    Vertical = 42
    VerticalIn = 43
    VerticalOut = 44
    Wheel1 = 45
    Wheel2 = 46
    Wheel3 = 47
    Wheel4 = 48
    Wheel8 = 49

