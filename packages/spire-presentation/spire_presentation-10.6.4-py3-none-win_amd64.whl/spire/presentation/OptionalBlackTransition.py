from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OptionalBlackTransition (  Transition) :
    """
    <summary>
        Optional black slide transition effect.
    </summary>
    """
    @property
    def FromBlack(self)->bool:
        """
    <summary>
        This attribute specifies if the transition will start from a black screen
            (and then transition the new slide over black).
    </summary>
        """
        GetDllLibPpt().OptionalBlackTransition_get_FromBlack.argtypes=[c_void_p]
        GetDllLibPpt().OptionalBlackTransition_get_FromBlack.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OptionalBlackTransition_get_FromBlack,self.Ptr)
        return ret

    @FromBlack.setter
    def FromBlack(self, value:bool):
        GetDllLibPpt().OptionalBlackTransition_set_FromBlack.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().OptionalBlackTransition_set_FromBlack,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().OptionalBlackTransition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().OptionalBlackTransition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OptionalBlackTransition_Equals,self.Ptr, intPtrobj)
        return ret

