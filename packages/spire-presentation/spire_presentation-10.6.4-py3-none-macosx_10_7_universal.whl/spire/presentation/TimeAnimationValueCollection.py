from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeAnimationValueCollection (  IEnumerable) :
    """
    <summary>
        Represent collection of animation points.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of points in the collection.
    </summary>
        """
        GetDllLibPpt().TimeAnimationValueCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValueCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TimeAnimationValue':
        """
    <summary>
        Gets a point at the specified index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().TimeAnimationValueCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TimeAnimationValueCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TimeAnimationValue(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for the collection.
    </summary>
    <returns>Iterator.</returns>
        """
        GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeAnimationValueCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


