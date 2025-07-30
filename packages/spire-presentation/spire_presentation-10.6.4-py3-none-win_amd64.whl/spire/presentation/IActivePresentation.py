from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IActivePresentation (SpireObject) :
    """
    <summary>
        Represents a component of a presentation.
    </summary>
    """
    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().IActivePresentation_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().IActivePresentation_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IActivePresentation_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


