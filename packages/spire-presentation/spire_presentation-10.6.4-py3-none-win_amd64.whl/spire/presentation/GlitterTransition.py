from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GlitterTransition (  Transition) :
    """

    """
    @property

    def Direction(self)->'GlitterTransitionDirection':
        """

        """
        GetDllLibPpt().GlitterTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().GlitterTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GlitterTransition_get_Direction,self.Ptr)
        objwraped = GlitterTransitionDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'GlitterTransitionDirection'):
        GetDllLibPpt().GlitterTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GlitterTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GlitterTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GlitterTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GlitterTransition_Equals,self.Ptr, intPtrobj)
        return ret

