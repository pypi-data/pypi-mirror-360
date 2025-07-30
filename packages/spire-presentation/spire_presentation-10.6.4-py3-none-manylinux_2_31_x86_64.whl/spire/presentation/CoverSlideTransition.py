from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CoverSlideTransition (  Transition) :
    """
    <summary>
        Eight direction slide transition effect.
    </summary>
    """
    @property

    def Direction(self)->'TransitionEightDirection':
        """
    <summary>
        Direction of transition.
    </summary>
        """
        GetDllLibPpt().CoverSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().CoverSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CoverSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionEightDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionEightDirection'):
        GetDllLibPpt().CoverSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CoverSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CoverSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CoverSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CoverSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

