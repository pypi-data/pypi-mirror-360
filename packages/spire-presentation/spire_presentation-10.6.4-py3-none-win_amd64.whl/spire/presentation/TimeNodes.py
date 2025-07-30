from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodes (  IEnumerable) :
    """

    """
    @property
    def Count(self)->int:
        """

        """
        GetDllLibPpt().TimeNodes_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodes_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TimeNodes_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TimeNode':
        """

        """
        
        GetDllLibPpt().TimeNodes_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TimeNodes_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNodes_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TimeNode(intPtr)
        return ret



    def RemoveAt(self ,index:int):
        """

        """
        
        GetDllLibPpt().TimeNodes_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TimeNodes_RemoveAt,self.Ptr, index)


    def Remove(self ,node:'TimeNode'):
        """

        """
        intPtrnode:c_void_p = node.Ptr

        GetDllLibPpt().TimeNodes_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodes_Remove,self.Ptr, intPtrnode)

    def Clear(self):
        """

        """
        GetDllLibPpt().TimeNodes_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodes_Clear,self.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNodes_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNodes_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodes_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """

        """
        GetDllLibPpt().TimeNodes_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodes_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNodes_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


