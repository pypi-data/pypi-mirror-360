from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IActiveSlide (  IActivePresentation) :
    """
    <summary>
        Represents a component of a slide.
    </summary>
    """
    @property

    def Slide(self)->'ActiveSlide':
        """

        """
        GetDllLibPpt().IActiveSlide_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().IActiveSlide_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IActiveSlide_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


