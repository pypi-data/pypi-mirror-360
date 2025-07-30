from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CellRanges (  SpireObject ) :
    """
    <summary>
        Represents collection of a cells with data.
    </summary>
    """

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().CellRanges_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellRanges_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret

    def get_Item(self ,index:int)->'CellRange':
        """
    <summary>
        Gets a cell by index.
    </summary>
    <param name="index">Index of a cell.</param>
    <returns>Cell with data.</returns>
        """
        
        GetDllLibPpt().CellRanges_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CellRanges_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CellRange(intPtr)
        return ret
    

    def Add(self ,cellRange:'CellRange')->int:
        """
    <summary>
        Add new cell to the collection.
    </summary>
    <param name="cellRange">New cell to add.</param>
    <returns>Index of a new added <see cref="T:Spire.Presentation.Charts.CellRange" />.</returns>
        """
        intPtrcellRange:c_void_p = cellRange.Ptr

        GetDllLibPpt().CellRanges_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRanges_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_Add,self.Ptr, intPtrcellRange)
        return ret

    
    def AddObject(self ,value:SpireObject)->int:
        """
    <summary>
        Creates <see cref="T:Spire.Presentation.Charts.CellRange" /> from specified value and adds it to the collection.
    </summary>
    <param name="value">The value.</param>
    <returns>Index of a new added <see cref="T:Spire.Presentation.Charts.CellRange" />.</returns>
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().CellRanges_AddV.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CellRanges_AddV.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_AddV,self.Ptr, intPtrvalue)
        return ret


    def RemoveAt(self ,index:int):
        """
    <summary>
        Removes a cell from the collection by index.
    </summary>
    <param name="index">Index of a cell to remove.</param>
        """
        
        GetDllLibPpt().CellRanges_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CellRanges_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an enumerator for the entire collection.
    </summary>
        """
        GetDllLibPpt().CellRanges_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CellRanges_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CellRanges_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property
    def Count(self)->int:
        """
    <summary>
        Gets the count of cells in collection.
    </summary>
        """
        GetDllLibPpt().CellRanges_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CellRanges_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CellRanges_get_Count,self.Ptr)
        return ret

