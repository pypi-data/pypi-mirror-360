from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Transition (  PptObject) :
    """
    <summary>
        Class for slide transition effects.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Transition_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Transition_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Transition_Equals,self.Ptr, intPtrobj)
        return ret

