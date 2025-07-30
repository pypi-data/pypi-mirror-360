from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class BlindsSlideTransition (  Transition) :
    """

    """
    @property

    def Direction(self)->'TransitionDirection':
        """

        """
        GetDllLibPpt().BlindsSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().BlindsSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().BlindsSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionDirection'):
        GetDllLibPpt().BlindsSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().BlindsSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().BlindsSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().BlindsSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().BlindsSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

