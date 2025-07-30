from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PlaceholderType(Enum):
    """
    <summary>
        Represents the type of a placeholder.
    </summary>
    """
    Title = 0
    Body = 1
    CenteredTitle = 2
    Subtitle = 3
    DateAndTime = 4
    SlideNumber = 5
    Footer = 6
    Header = 7
    Object = 8
    Chart = 9
    Table = 10
    ClipArt = 11
    Diagram = 12
    Media = 13
    SlideImage = 14
    Picture = 15
    none = 16

