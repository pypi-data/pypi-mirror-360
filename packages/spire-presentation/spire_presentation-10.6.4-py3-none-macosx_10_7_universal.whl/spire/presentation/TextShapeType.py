from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextShapeType(Enum):
    """
    <summary>
        Represents text wrapping shape.
    </summary>
    """
    UnDefined = -1
    none = 0
    Plain = 1
    Stop = 2
    Triangle = 3
    TriangleInverted = 4
    Chevron = 5
    ChevronInverted = 6
    RingInside = 7
    RingOutside = 8
    ArchUp = 9
    ArchDown = 10
    Circle = 11
    Button = 12
    ArchUpPour = 13
    ArchDownPour = 14
    CirclePour = 15
    ButtonPour = 16
    CurveUp = 17
    CurveDown = 18
    CanUp = 19
    CanDown = 20
    Wave1 = 21
    Wave2 = 22
    DoubleWave1 = 23
    Wave4 = 24
    Inflate = 25
    Deflate = 26
    InflateBottom = 27
    DeflateBottom = 28
    InflateTop = 29
    DeflateTop = 30
    DeflateInflate = 31
    DeflateInflateDeflate = 32
    FadeRight = 33
    FadeLeft = 34
    FadeUp = 35
    FadeDown = 36
    SlantUp = 37
    SlantDown = 38
    CascadeUp = 39
    CascadeDown = 40
    Custom = 41

