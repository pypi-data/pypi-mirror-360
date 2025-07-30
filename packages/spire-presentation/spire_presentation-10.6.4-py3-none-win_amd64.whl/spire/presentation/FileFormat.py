from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FileFormat(Enum):
    """
    <summary>
        Specifies the type of file format.
    </summary>
    """
    Auto = 0
    PPT = 1
    Pptx2007 = 2
    Pptx2010 = 3
    Pptx2013 = 4
    Pptx2016 = 5
    Pptx2019 = 6
    Pptm = 7
    Ppsx2007 = 8
    Ppsx2010 = 9
    Ppsx2013 = 10
    Ppsx2016 = 11
    Ppsx2019 = 12
    PPS = 13
    ODP = 14
    #UOP = 15
    Html = 16
    #Tiff = 17
    XPS = 18
    PCL = 19
    PS = 20
    OFD = 21
    PDF = 22
    Potx = 23
    Dps = 24
    Dpt = 25
    #Bin = 26

