from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SideDirectionTransition (  Transition) :
    """
    <summary>
        Side direction slide transition effect.
    </summary>
    """
    @property

    def Direction(self)->'TransitionSideDirectionType':
        """
    <summary>
        Direction of transition.
    </summary>
        """
        GetDllLibPpt().SideDirectionTransition_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().SideDirectionTransition_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SideDirectionTransition_get_Direction,self.Ptr)
        objwraped = TransitionSideDirectionType(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'TransitionSideDirectionType'):
        GetDllLibPpt().SideDirectionTransition_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SideDirectionTransition_set_Direction,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SideDirectionTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SideDirectionTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SideDirectionTransition_Equals,self.Ptr, intPtrobj)
        return ret

