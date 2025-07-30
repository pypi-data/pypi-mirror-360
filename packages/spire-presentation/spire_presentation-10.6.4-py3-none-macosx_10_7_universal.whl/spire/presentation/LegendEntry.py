from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LegendEntry (SpireObject) :
    """
    <summary>
        Legend entry.
    </summary>
    """
    @property

    def TextProperties(self)->'ITextFrameProperties':
        """
    <summary>
        Represent text properties of legend entry.
    </summary>
        """
        GetDllLibPpt().LegendEntry_get_TextProperties.argtypes=[c_void_p]
        GetDllLibPpt().LegendEntry_get_TextProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LegendEntry_get_TextProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


