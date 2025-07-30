from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PdfConformanceLevel(Enum):
    """
    <summary>
        Represent fill types.
    </summary>
    """
    none = -1
    Pdf_A1B = 0
    Pdf_X1A2001 = 1
    Pdf_A1A = 2
    Pdf_A2A = 3
    Pdf_A2B = 4
    Pdf_A3A = 5
    Pdf_A3B = 6