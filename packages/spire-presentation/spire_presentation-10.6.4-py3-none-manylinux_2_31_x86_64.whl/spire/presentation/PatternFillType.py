from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PatternFillType(Enum):
    """
    <summary>
        Represents the pattern style.
    </summary>
    """
    UnDefined = -1
    none = 0
    Percent05 = 1
    Percent10 = 2
    Percent20 = 3
    Percent25 = 4
    Percent30 = 5
    Percent40 = 6
    Percent50 = 7
    Percent60 = 8
    Percent70 = 9
    Percent75 = 10
    Percent80 = 11
    Percent90 = 12
    DarkHorizontal = 13
    DarkVertical = 14
    DarkDownwardDiagonal = 15
    DarkUpwardDiagonal = 16
    SmallCheckerBoard = 17
    Trellis = 18
    LightHorizontal = 19
    LightVertical = 20
    LightDownwardDiagonal = 21
    LightUpwardDiagonal = 22
    SmallGrid = 23
    DottedDiamond = 24
    WideDownwardDiagonal = 25
    WideUpwardDiagonal = 26
    DashedUpwardDiagonal = 27
    DashedDownwardDiagonal = 28
    NarrowVertical = 29
    NarrowHorizontal = 30
    DashedVertical = 31
    DashedHorizontal = 32
    LargeConfetti = 33
    LargeGrid = 34
    HorizontalBrick = 35
    LargeCheckerBoard = 36
    SmallConfetti = 37
    Zigzag = 38
    SolidDiamond = 39
    DiagonalBrick = 40
    OutlinedDiamond = 41
    Plaid = 42
    Sphere = 43
    Weave = 44
    DottedGrid = 45
    Divot = 46
    Shingle = 47
    Wave = 48
    Horizontal = 49
    Vertical = 50
    Cross = 51
    DownwardDiagonal = 52
    UpwardDiagonal = 53
    DiagonalCross = 54

