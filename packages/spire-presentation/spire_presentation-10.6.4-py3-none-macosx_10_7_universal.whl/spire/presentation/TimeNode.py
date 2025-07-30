from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNode (SpireObject) :
    """

    """
    @property

    def ChildNodes(self)->'TimeNodes':
        """

        """
        GetDllLibPpt().TimeNode_get_ChildNodes.argtypes=[c_void_p]
        GetDllLibPpt().TimeNode_get_ChildNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNode_get_ChildNodes,self.Ptr)
        ret = None if intPtr==None else TimeNodes(intPtr)
        return ret


    @property

    def SubNodes(self)->'TimeNodes':
        """

        """
        GetDllLibPpt().TimeNode_get_SubNodes.argtypes=[c_void_p]
        GetDllLibPpt().TimeNode_get_SubNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNode_get_SubNodes,self.Ptr)
        ret = None if intPtr==None else TimeNodes(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNode_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNode_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNode_Equals,self.Ptr, intPtrobj)
        return ret

