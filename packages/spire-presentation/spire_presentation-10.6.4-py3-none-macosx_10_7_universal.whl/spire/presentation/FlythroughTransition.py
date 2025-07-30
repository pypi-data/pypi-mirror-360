from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FlythroughTransition (  Transition) :
    """

    """
    @property

    def Direction(self)->'TransitionFlythroughInOutDirection':
        """

        """
        GetDllLibPpt().FlythroughTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().FlythroughTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FlythroughTransition_get_Direction,self.Ptr)
        objwraped = TransitionFlythroughInOutDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionFlythroughInOutDirection'):
        GetDllLibPpt().FlythroughTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FlythroughTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FlythroughTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FlythroughTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FlythroughTransition_Equals,self.Ptr, intPtrobj)
        return ret

