from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class TextRangeList (SpireObject) :

    """
    <summary>
        Represents a collection.
    </summary>
    """

    def __getitem__(self ,index:int)->'TextRange':
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().TextRangeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextRangeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of elements actually contained in the collection.
    </summary>
        """
        GetDllLibPpt().TextRangeList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextRangeList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'TextRange':
        """
    <summary>
        Gets the element at the specified index.
    </summary>
        """
        
        GetDllLibPpt().TextRangeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextRangeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret



    def Append(self ,value:'TextRange')->int:
        """
    <summary>
        Adds a text range to the end of collection.
    </summary>
    <param name="value">The text range </param>
    <returns>The index at which the text range has been added.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TextRangeList_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRangeList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextRangeList_Append,self.Ptr, intPtrvalue)
        return ret


    def Insert(self ,index:int,value:'TextRange'):
        """
    <summary>
        Inserts a Portion into the collection at the specified index.
    </summary>
    <param name="index">The zero-based index at which Portion should be inserted.</param>
    <param name="value">The Portion to insert.</param>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().TextRangeList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().TextRangeList_Insert,self.Ptr, index,intPtrvalue)

    def Clear(self):
        """
    <summary>
        Removes all elements from the collection.
    </summary>
        """
        GetDllLibPpt().TextRangeList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TextRangeList_Clear,self.Ptr)


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes the element at the specified index of the collection.
    </summary>
    <param name="index">The zero-based index of the element to remove.</param>
        """
        
        GetDllLibPpt().TextRangeList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TextRangeList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
    <returns>An <see cref="T:System.Collections.IEnumerator" /> for the entire collection.</returns>
        """
        GetDllLibPpt().TextRangeList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextRangeList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextRangeList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextRangeList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextRangeList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextRangeList_Equals,self.Ptr, intPtrobj)
        return ret

