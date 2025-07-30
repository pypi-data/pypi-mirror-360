from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideLayoutType(Enum):
    """
    <summary>
        Represents the slide layout type.
    </summary>
    """
    Custom = -1
    Title = 0
    Text = 1
    TwoColumnText = 2
    Table = 3
    TextAndChart = 4
    ChartAndText = 5
    Diagram = 6
    Chart = 7
    TextAndClipArt = 8
    ClipArtAndText = 9
    TitleOnly = 10
    Blank = 11
    TextAndObject = 12
    ObjectAndText = 13
    Object = 14
    TitleAndObject = 15
    TextAndMedia = 16
    MediaAndText = 17
    ObjectOverText = 18
    TextOverObject = 19
    TextAndTwoObjects = 20
    TwoObjectsAndText = 21
    TwoObjectsOverText = 22
    FourObjects = 23
    VerticalText = 24
    ClipArtAndVerticalText = 25
    VerticalTitleAndText = 26
    VerticalTitleAndTextOverChart = 27
    TwoObjects = 28
    ObjectAndTwoObject = 29
    TwoObjectsAndObject = 30
    SectionHeader = 31
    TwoTextAndTwoObjects = 32
    TitleObjectAndCaption = 33
    PictureAndCaption = 34

