from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ParagraphBuildType(Enum):
    """
    <summary>
        Indicates how text display style during animation.
    </summary>
    """
    Whole = 0
    AllAtOnce = 1
    Paragraphs1 = 2
    Paragraphs2 = 3
    Paragraphs3 = 4
    Paragraphs4 = 5
    Paragraphs5 = 6
    cust = 7

