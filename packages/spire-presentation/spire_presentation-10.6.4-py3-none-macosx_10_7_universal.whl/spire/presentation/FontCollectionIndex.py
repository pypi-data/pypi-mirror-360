from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FontCollectionIndex(Enum):
    """
    <summary>
        Represents font's index in a collection.
    </summary>
    """
    none = 0
    Minor = 1
    Major = 2

