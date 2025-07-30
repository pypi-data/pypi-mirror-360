from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineStyleList (  IEnumerable) :
    """
    <summary>
        Represents the collection of line styles.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().LineStyleList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineStyleList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextLineFormat':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.TextLineFormat" />.
    </summary>
        """
        
        GetDllLibPpt().LineStyleList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().LineStyleList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineStyleList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LineStyleList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LineStyleList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineStyleList_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().LineStyleList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().LineStyleList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineStyleList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


