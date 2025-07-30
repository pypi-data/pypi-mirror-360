from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillStyleList (  FillListBase) :
    """
    <summary>
        Represents the collection of fill styles.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillStyleList_Equals,self.Ptr, intPtrobj)
        return ret

