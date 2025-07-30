from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FormatAndVersion(Enum):
    """
    <summary>
        Specifies the format and version of file.
    </summary>
    """
    PPT = 0
    Pptx2007 = 1
    Pptx2010 = 2
    Pptx2013 = 3
    Pptx2016 = 4
    PPS = 5
    Ppsx2007 = 6
    Ppsx2010 = 7
    Ppsx2013 = 8
    Ppsx2016 = 9
    Odp = 10
    Uop = 11
    Pot = 12
    Potm2007 = 13
    Potm2010 = 14
    Potm2013 = 15
    Potm2016 = 16
    Potx2007 = 17
    Potx2010 = 18
    Potx2013 = 19
    Potx2016 = 20
    Pptm2007 = 21
    Pptm2010 = 22
    Pptm2013 = 23
    Pptm2016 = 24
    Ppsm2007 = 25
    Ppsm2010 = 26
    Ppsm2013 = 27
    Ppsm2016 = 28

