from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ZoomSlideTransition (  Transition) :
    """

    """
    @property

    def Direction(self)->'TransitionInOutDirection':
        """
    <summary>
        Direction of a transition effect.
            Read/write <see cref="T:Spire.Presentation.Drawing.Transition.TransitionInOutDirection" />.
    </summary>
        """
        GetDllLibPpt().ZoomSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().ZoomSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ZoomSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionInOutDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionInOutDirection'):
        GetDllLibPpt().ZoomSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ZoomSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ZoomSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ZoomSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ZoomSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

