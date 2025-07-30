from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SplitSlideTransition (  Transition) :
    """
    <summary>
        Split slide transition effect.
    </summary>
    """
    @property

    def Direction(self)->'TransitionSplitDirection':
        """
    <summary>
        Direction of transition split.
            Read/write <see cref="T:Spire.Presentation.Drawing.Transition.TransitionInOutDirection" />.
    </summary>
        """
        GetDllLibPpt().SplitSlideTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().SplitSlideTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SplitSlideTransition_get_Direction,self.Ptr)
        objwraped = TransitionSplitDirection(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionSplitDirection'):
        GetDllLibPpt().SplitSlideTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SplitSlideTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SplitSlideTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SplitSlideTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SplitSlideTransition_Equals,self.Ptr, intPtrobj)
        return ret

