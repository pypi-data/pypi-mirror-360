from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ImportDataFormat(Enum):
    """
    <summary>
        Represents source file format.
    </summary>
    """
    Ppt = 0
    Pptx = 1
    Odp = 2

