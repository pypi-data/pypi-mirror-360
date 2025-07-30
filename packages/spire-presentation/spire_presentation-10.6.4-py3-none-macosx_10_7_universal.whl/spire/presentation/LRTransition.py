from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LRTransition (  Transition) :
    """

    """
    @property

    def Direction(self)->'TransitionTwoDirection':
        """

        """
        GetDllLibPpt().LRTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().LRTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LRTransition_get_Direction,self.Ptr)
        objwraped = TransitionTwoDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionTwoDirection'):
        GetDllLibPpt().LRTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LRTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LRTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LRTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LRTransition_Equals,self.Ptr, intPtrobj)
        return ret

