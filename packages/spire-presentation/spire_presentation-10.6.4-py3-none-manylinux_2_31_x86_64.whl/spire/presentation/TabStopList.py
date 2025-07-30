from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabStopList (SpireObject) :
    """
    <summary>
        Represents a collection of tabs.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().TabStopList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TabStop':
        """
    <summary>
        Gets the element at the specified index.
            Read-only <see cref="T:Spire.Presentation.TabStop" />.
    </summary>
        """
        
        GetDllLibPpt().TabStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TabStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TabStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TabStop(intPtr)
        return ret



    def Append(self ,value:'TabStop')->int:
        """
    <summary>
        Adds a Tab to the collection.
    </summary>
    <param name="value">The Tab object to be added at the end of the collection.</param>
    <returns>The index at which the tab was added.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TabStopList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStopList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_Append,self.Ptr, intPtrvalue)
        return ret

    def Clear(self):
        """
    <summary>
        Removes all elements from the collection.
    </summary>
        """
        GetDllLibPpt().TabStopList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TabStopList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().TabStopList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TabStopList_RemoveAt,self.Ptr, index)


    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Indicates whether two Tabs instances are equal.
    </summary>
    <param name="obj">The Tabs to compare with the current Tabs.</param>
    <returns>
  <b>true</b> if the specified Tabs is equal to the current Tabs; otherwise, <b>false</b>.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TabStopList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStopList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TabStopList_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
    <summary>
        Gets hash code for this object.
    </summary>
        """
        GetDllLibPpt().TabStopList_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStopList_GetHashCode,self.Ptr)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().TabStopList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TabStopList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TabStopList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


