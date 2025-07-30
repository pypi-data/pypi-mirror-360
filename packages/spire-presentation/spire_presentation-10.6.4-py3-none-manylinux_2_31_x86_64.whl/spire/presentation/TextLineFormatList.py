from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextLineFormatList (  IEnumerable) :
    """
    <summary>
        Represents a collection of LineFormat objects.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().TextLineFormatList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextLineFormatList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextLineFormat':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
        """
        
        GetDllLibPpt().TextLineFormatList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextLineFormatList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormatList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets the enumerator for an entire collection.
    </summary>
    <returns>
  <see cref="T:System.Collections.IEnumerator" /> for an entire collection.</returns>
        """
        GetDllLibPpt().TextLineFormatList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextLineFormatList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextLineFormatList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


